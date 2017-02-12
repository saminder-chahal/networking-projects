"""This controller performs all L2 switching operations succesfully for non-reduntant networks and 
is compatible with protocol OpenFlow13 only.It creates a new thread which sends flow stat request 
every 3 seconds and new flow stat replies are printed on everypacket in, copy of all flow stat 
replies is created in .csv file with dpid ==> flow_stats mapping whose path is displayed on every 
packet in. 
"""

import csv,os
from ryu.base import app_manager as manager
from ryu.controller import handler
from ryu.controller import ofp_event
from ryu.ofproto import ofproto_v1_3 as of13
from ryu.ofproto import ofproto_v1_3_parser as parser13
from ryu.lib.packet import packet
from ryu.lib.packet import ether_types
from ryu.lib.packet import ethernet as eth
from ryu.lib.packet import arp
from ryu.lib.packet import ipv4
from collections import defaultdict as ddict
from ryu.lib import hub
from time import gmtime, strftime


class MyController(manager.RyuApp):
	OFP_VERSIONS = [of13.OFP_VERSION]
        DEF_PRI = 100
	DEF_TIMEOUT = 30

        def __init__(self, *args, **kwargs):
                super(MyController, self).__init__(*args, **kwargs)    # Mandatory
                self.mac_tables = ddict(dict)             # {DPID => {MAC => PORT}}
		self.arp_table = dict()                   # {IP => MAC}
		self.switchports = ddict(dict)  # {DPID => {PORTID => PORT States}}
                
                #Creating a new thread and calling function for flow stat request 
                self.stats_requester_thread = hub.spawn(self._flow_stats_requester) 
                
                self.switches = {}                    #{DPID => SWITCH}
                self.flows = dict()                  #{DPID => Flows} only stores new flow stat replies
                self.flow_stat_file = []   #Storing the time values when new switches added to topo.

        #Event handler when switches are added to controller
        @handler.set_ev_cls(ofp_event.EventOFPSwitchFeatures, handler.CONFIG_DISPATCHER)
	def unknown_switch(self, ev):
                switch = ev.msg.datapath
                #ADD the Switch
                self.switches[switch.id] = switch #Storing switch datapath corresponding to dpid

                # Build a default rule
		actions_controller = [parser13.OFPActionOutput(of13.OFPP_CONTROLLER)]
		instr = [ parser13.OFPInstructionActions(
						of13.OFPIT_APPLY_ACTIONS,
						actions_controller) ]

		# Calling function to add default flow to switch
	        self.send_new_flow(switch = switch, instr = instr, priority = 0, timeout = 0)

                # Sending port status request
		msg = parser13.OFPPortDescStatsRequest(switch)
		switch.send_msg(msg)

                #Reset switch flows stats table for new topology or new switch added.
                self.flows = {}

                #Calling a function to get new time when switches added and append them in flow_stat_file.
                new_file_time = self.flow_file_generator()
                self.flow_stat_file.append(new_file_time)   


        #Event handler for the packets coming to the controller        
        @handler.set_ev_cls(ofp_event.EventOFPPacketIn, handler.MAIN_DISPATCHER)
	def unknown_flow(self, ev):
                switch = ev.msg.datapath
		data = ev.msg.data
		parsed_data = packet.Packet(data)
		in_port = ev.msg.match['in_port']
		first_eth = parsed_data.get_protocols(eth.ethernet)[0]

                #Calling function to update arp and mac tables
                self.learn(switch, in_port, parsed_data)

                # Send where?
		if first_eth.dst in self.mac_tables[switch.id]:
			out_port = self.mac_tables[switch.id][first_eth.dst]
		else:
			out_port = of13.OFPP_FLOOD

                # Flow definition
		match = parser13.OFPMatch(in_port = in_port , eth_dst = first_eth.dst)
                actions = [ parser13.OFPActionOutput(out_port) ]
		instr = [ parser13.OFPInstructionActions(
						of13.OFPIT_APPLY_ACTIONS,
						actions) ]

                # Do we use BID?
		if ev.msg.buffer_id == of13.OFP_NO_BUFFER:    # We got no buffer_id
			# ..so we send actual data
			self.send_packet_out(switch, out_port = out_port,
                                        data = data, actions = actions, in_port = in_port)
			if out_port != of13.OFPP_FLOOD:
				# ...and install a rule if it isn't a FLOOD
				self.send_new_flow(switch, match = match, instr = instr)
		else:                                           # We have buffer id
			if out_port != of13.OFPP_FLOOD:
				# ...and are not FLOODing
				# so we install a rule and send packet out in one line
				self.send_new_flow(switch, match = match, instr = instr,
                                                   buffer_id = ev.msg.buffer_id)
			else:
				# or just send a packet out, without a rule
				self.send_packet_out(switch, out_port = out_port,
                                                     buffer_id = ev.msg.buffer_id,
                                                     actions = actions, in_port = in_port)

                #Printing flow stats for every packet in.
                print "New flow stats reply with SW.ID : current flows stats: \n", self.flows , "\n"
                
                #Printing name and path of complete flow stat file for every packet in             
                new_file_t = self.flow_stat_file[-1]     
                print "For complete flow stats replies please open Sam-" + str(new_file_t) +".csv" + " in " +os.getcwd() + "/ \n\n\n"

        #Event handler to reply to port status request
	@handler.set_ev_cls(ofp_event.EventOFPPortDescStatsReply, handler.MAIN_DISPATCHER)
	def port_dump(self, ev):
             for p in ev.msg.body:
                self.switchports[ev.msg.datapath.id][p.port_no] = p.state

        #Event handler to reply to flow stat request 
        @handler.set_ev_cls(ofp_event.EventOFPFlowStatsReply, handler.MAIN_DISPATCHER)
        def flow_stat_reply(self, ev):
                for stat in ev.msg.body:
                        flow=('table_id = %s ''duration_sec = %d duration_nsec = %d '
                     'priority = %d ''idle_timeout = %d hard_timeout = %d flags = 0x%04x '
                     'cookie = %d packet_count = %d byte_count = %d ''match = %s instructions = %s' %
                     (stat.table_id, stat.duration_sec, stat.duration_nsec, stat.priority,
                      stat.idle_timeout, stat.hard_timeout, stat.flags, stat.cookie, stat.packet_count, 
                      stat.byte_count, stat.match, stat.instructions))
                        
                        #Adding new flow reply to self.flows.
                        self.flows[ev.msg.datapath.id] = flow         
                        
                        #Storing all flow replies in .csv file with dpid ==> flow mapping.
                        new_file_t = self.flow_stat_file[-1]      #getting last time when switches added from flow_stat_file 
                        sam = (open("Sam -" + str(new_file_t) +".csv","a"))  
                        newfile = csv.writer(sam)                  
                        newfile.writerow([ev.msg.datapath.id, flow])   #Storing flow stats in .csv file
                        sam.close()                #closing the file

        #Event handler if ports status is changed (port added ,deleted or modified)
        @handler.set_ev_cls(ofp_event.EventOFPPortStatus, handler.MAIN_DISPATCHER)
	def port_status(self, ev):
		p = ev.msg.desc
		if ev.msg.reason == of13.OFPPR_DELETE:
			print "Switch", ev.msg.datapath.id, "- port", p.port_no, "DELETED"
			del self.switchports[ev.msg.datapath.id][p.port_no]
                        return 
		elif ev.msg.reason == of13.OFPPR_ADD:
			print "Switch", ev.msg.datapath.id, "- port", p.port_no, "ADDED"
		elif ev.msg.reason == of13.OFPPR_MODIFY:
			print "Switch", ev.msg.datapath.id, "- port", p.port_no, "MODIFIED"

		#Updating switchports table with new port states
                self.switchports[ev.msg.datapath.id][p.port_no] = p.state
		if p.state == 1:
			print "Switch", ev.msg.datapath.id, "- port", p.port_no, "DOWN"
		elif p.state == 0:
			print "Switch", ev.msg.datapath.id, "- port", p.port_no, "UP"

        #Defining a function to send port stat request every three seconds 
        def _flow_stats_requester(self): 
            while True:
                for dp in self.switchports.keys():
                    switch = self.switches[dp]          #Getting datapath from dpid
                    cookie = cookie_mask = 0
                    match = parser13.OFPMatch()
                    msg = parser13.OFPFlowStatsRequest(switch, 0, of13.OFPTT_ALL,
                            of13.OFPP_ANY, of13.OFPG_ANY, cookie, cookie_mask, match)
                    switch.send_msg(msg)
                hub.sleep(3)                        # Sleeping for three seconds

        #Sending packet out
	def send_packet_out(self,switch,out_port = of13.OFPP_FLOOD,data = None,
			    buffer_id = of13.OFP_NO_BUFFER,actions = [],in_port = 0):

		msg = parser13.OFPPacketOut(datapath = switch,data = data,
                           buffer_id = buffer_id,actions = actions,in_port = in_port)
		switch.send_msg(msg)

        #Adding new flow to switch
	def send_new_flow(self,switch,out_port = of13.OFPP_FLOOD, match = parser13.OFPMatch(),
	     instr = [],priority = DEF_PRI, timeout = DEF_TIMEOUT, buffer_id = of13.OFP_NO_BUFFER):
                msg = parser13.OFPFlowMod(match = match, datapath = switch, instructions = instr,
                              idle_timeout = timeout,priority = priority, buffer_id = buffer_id)
		switch.send_msg(msg)

        #Updating arp table and mac table
	def learn(self, switch, in_port, parsed_data):
		first_eth = parsed_data.get_protocols(eth.ethernet)[0]

		#Learn IP => Mac
                if first_eth.ethertype == ether_types.ETH_TYPE_ARP:
			arp_header = parsed_data.get_protocols(arp.arp)[0]
			self.arp_table[arp_header.src_ip] = first_eth.src
		elif first_eth.ethertype == ether_types.ETH_TYPE_IP:
			ip_header = parsed_data.get_protocols(ipv4.ipv4)[0]
			self.arp_table[ip_header.src] = first_eth.src

                # Learn source MAC to SW_PORT 
		self.mac_tables[switch.id][first_eth.src] = in_port


        #Returning the time when switch/switches added
        def flow_file_generator(self):
            current_time = strftime("%Y-%m-%d %H-%M-%S", gmtime())
            print "Current time when switches added is :",Current_time
            return current_time
