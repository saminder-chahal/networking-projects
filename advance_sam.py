" Switching operation using openflow protocol version 1.3"
from ryu.base import app_manager
from ryu.controller import ofp_event as event
from ryu.controller.handler import CONFIG_DISPATCHER,MAIN_DISPATCHER,set_ev_cls
from ryu.ofproto import ofproto_v1_3 as ofp3
from ryu.lib.packet import packet,ethernet,ether_types
from ryu.lib.packet import arp,ipv4

class SamController13(app_manager.RyuApp):
    ofp_version=[ofp3.OFP_VERSION]
    def __init__(self, *args, **kwargs):
        super(SamController13, self).__init__(*args, **kwargs)   #class initialisation
        self.mac_to_port={}          # Mac to port table empty in starting
        self.arp_table={}            # IP ==> MAC Mapping
        self.switchports={}              # DPID => {port number => port state}

    @set_ev_cls(event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_controller_flow(self, ev):
        datapath=ev.msg.datapath                  #Getting info about switch path
        ofproto=datapath.ofproto                     #Initialising the openflow protocol for handshake,req-response messages
        parser=datapath.ofproto_parser             #parsing the data in decoded form and making a channel to communicate with switch
        match=parser.OFPMatch()                    #For flow match
        actions=[parser.OFPActionOutput(ofproto.OFPP_CONTROLLER)]             #defining the default action to take for unknow packet
        self.add_new_flow(datapath=datapath,priority=0,match=match,actions=actions,timeout=0)    #adding default flow to controller to switch

        #Request port description
        req=parser.OFPPortDescStatsRequest(datapath)
        print "Request is :",req
        datapath.send_msg(req)
    #Port desc reply
    @set_ev_cls(event.EventOFPPortDescStatsReply, MAIN_DISPATCHER)
    def port_desc_reply(self,ev):
        self.switchports.setdefault(ev.msg.datapath.id, {})
        for p in ev.msg.body:
            self.switchports[ev.msg.datapath.id][p.port_no]=p.state
    #Port Status
    @set_ev_cls(event.EventOFPPortStatus,MAIN_DISPATCHER)
    def port_status_handler(self, ev):
        #self.switchports.setdefault(dpid, {})
        msg = ev.msg.desc
        if ev.msg.reason == ofp3.OFPPR_ADD:
            print "Port Number %d of switch %d is added" % (msg.port_no,ev.msg.datapath.id)
        elif ev.msg.reason == ofp3.OFPPR_DELETE:
            print "Port Number %d of switch %d is deleted" % (msg.port_no,ev.msg.datapath.id)
            del self.switchports[ev.msg.datapath.id][msg.port_no]
            return
        elif ev.msg.reason == ofp3.OFPPR_MODIFY:
            print "Port Number %d of switch %d is modified" % (msg.port_no,ev.msg.datapath.id)
            if msg.state == 1:
                print "Port Number",msg.port_no,"of switch",ev.msg.datapath.id,"is down now"
            if msg.state == 0:
                print "Port Number",msg.port_no,"of switch",ev.msg.datapath.id,"is up now"
        self.switchports[ev.msg.datapath.id][msg.port_no]=msg.state

    def ip_mac(self,datapath,packet,protocol_header):       #IP ==> MAC Maping
        self.arp_table.setdefault(None)
        if protocol_header.ethertype == ether_types.ETH_TYPE_ARP:
            arp_header=packet.get_protocols(arp.arp)[0]
            #print arp_header
            self.arp_table[arp_header.src_ip]=protocol_header.src

            #print self.arp_table
        elif protocol_header.ethertype == ether_types.ETH_TYPE_IP:
            ip_header=packet.get_protocols(ipv4.ipv4)[0]
            print "IP Header is :",ip_header
            self.arp_table[ip_header.src]=protocol_header.src


    def add_new_flow(self, datapath, priority, match, actions,timeout=30,buffer_id=None):
        ofproto=datapath.ofproto
        parser=datapath.ofproto_parser
        instr=[parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]                    #Giving instructions to apply actions defined
        if buffer_id != None:                                                                         #to Add flow with buffer id
            flow=parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, instructions=instr, buffer_id=buffer_id,idle_timeout=timeout)
        else:
            flow=parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, instructions=instr,idle_timeout=timeout)         #to Add flow without buffer id
        datapath.send_msg(flow)    #Adding the flow.
    @set_ev_cls(event.EventOFPPacketIn, MAIN_DISPATCHER)
    def unknown_flow(self,ev):
        datapath=ev.msg.datapath                    #Getting info about switch path
        ofproto=datapath.ofproto                    #Initialising the openflow protocol for handshake,req-response messages
        parser=datapath.ofproto_parser               #parsing the data in decoded form and making a channel to communicate with switch
        in_port=ev.msg.match['in_port']                #learning about in_port
        pkt=packet.Packet(ev.msg.data)             #Getting the data inside the packet
        eth_header=pkt.get_protocols(ethernet.ethernet)[0]             #Taking out ethernet header
        dst=eth_header.dst                                    #Storing destination address in variable dst for futur use
        src=eth_header.src                                  #Storing source address in variable src for futur use
        dpid=datapath.id                                  #Case of multiple switches,dpid gives info about particular switch

        self.ip_mac(datapath=datapath, packet=pkt, protocol_header= eth_header)


        self.mac_to_port.setdefault(dpid, {})                 #Initialising mac_to_port dictionary with dpids as primary key
        self.logger.info("Packet arrived from switch %s,src_addr=%s, dst_addr=%s, in_port=%s\n",dpid,src,dst,in_port)    #Displaying packet in info
        # Updating Mac table
        self.mac_to_port[dpid][eth_header.src]=in_port
        if dst in self.mac_to_port[dpid]:                           #Checking mac table for destination address port
            out_port=self.mac_to_port[dpid][dst]
        else:
            out_port=ofproto.OFPP_FLOOD                             #If dst port not found flodding the packet
        actions=[parser.OFPActionOutput(out_port)]                    #Defining our action to send packet out
        #Installing flow for this packet
        if out_port != ofproto.OFPP_FLOOD:
            match=parser.OFPMatch(in_port=in_port, eth_dst=dst)
            if ev.msg.buffer_id != ofproto.OFP_NO_BUFFER:
                print "YEah dst with buffer id known \n"
                self.add_new_flow(datapath=datapath,priority=100,match=match,actions=actions,timeout=30,buffer_id=ev.msg.buffer_id)
            else:
                print "DSt known but not buffer_id Sir Note here \n"
                self.add_new_flow(datapath=datapath,priority=100,match=match,actions=actions,timeout=30)
        else:   #Else sending packet out (flood) with no data inside
            print "Flooded packet \n"
            data=None
            out=parser.OFPPacketOut(datapath=datapath,buffer_id=ev.msg.buffer_id,in_port=in_port,actions=actions,data=data)
            datapath.send_msg(out)
