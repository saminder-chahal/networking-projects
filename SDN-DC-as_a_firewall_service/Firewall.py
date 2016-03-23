"""
An L2 learning switch with firewall as a service

"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str
from pox.lib.util import str_to_bool
import time
from pox.lib.revent import *
from pox.lib.addresses import EthAddr
from collections import namedtuple
from csv import DictReader
from os.path import abspath, exists


log = core.getLogger()
File = abspath("rulesfile.csv")

#Policy contains a single source-destination flow to be blocked on the controller.
Policy = namedtuple('Policy', ('dl_src', 'dl_dst'))

class LearningSwitch (object):
 
  def __init__ (self, connection):
    self.connection = connection
    self.mactable = {}              # Mac addresses to port mapping
    connection.addListeners(self)      #Listening for packets

  def _handle_PacketIn (self, event):
    packet = event.parsed           # Parsing the packet content

    def flood (message = None):                     #To flood the packets out from all the ports except the incoming packet port
      self.connection.send( of.ofp_packet_out( action = of.ofp_action_output( port = of.OFPP_FLOOD), in_port = event.port, data = event.ofp))


    def drop (): #Drop the packet
      self.connection.send( of.ofp_flow_mod( action = of.ofp_action_output( port = of.OFPP_NONE), idle_timeout = 10, 
          hard_timeout = 30, data = event.ofp, match = of.ofp_match.from_packet(packet, event.port)))

    self.mactable[packet.src] = event.port       #Adding entry

    
    if packet.type == packet.LLDP_TYPE or packet.dst.isBridgeFiltered(): #If packet is of type LLDP or Bridgefiltered ,then drop packet
	    drop() # 2a
            return
    
    if packet.dst.is_multicast:    #Drop packet if its destination is multicast
      flood() # 3a
    
    else:
      
      if packet.dst not in self.mactable: # 4              Flood packet if its not found in mactable
        flood("Port for %s unknown -- flooding" % (packet.dst,)) # 4a
      
      else:
        port = self.mactable[packet.dst]                        
        if port == event.port: # 5                                                   
          log.warning("Same port for packet from %s -> %s on %s.%s.  Drop."
              % (packet.src, packet.dst, dpid_to_str(event.dpid), port))
          drop()
          return
        # 6
        log.debug("installing flow for %s.%i -> %s.%i" %
                  (packet.src, event.port, packet.dst, port))
        
		#Adding the flow to switch
        self.connection.send( of.ofp_flow_mod( action = of.ofp_action_output( port = port), idle_timeout = 10, 
          hard_timeout = 30, data = event.ofp, match = of.ofp_match.from_packet(packet, event.port)))

       

class FirewallPlugin (EventMixin):

    def __init__ (self):
        self.listenTo(core.openflow)
        log.debug("Enabling Firewall Module")

    def read_rulesfile (self, file):                     #Reading the firewall rules file
        with open(file, 'r') as rulesfile:
            reader = DictReader(rulesfile, delimiter = ",")
            FirewallPolicies = {}                          #dictionary with ID as keys and mac address pairs values
            for row in reader:
                FirewallPolicies[row['id']] = Policy(EthAddr(row['mac_0']), EthAddr(row['mac_1']))
        return FirewallPolicies

    def _handle_ConnectionUp (self, event):                     #Connection up event handler
        FirewallPolicies = self.read_rulesfile(File)
        for policy in FirewallPolicies.itervalues():
            #ploicy in one direction and installing this message to switch flowtable
            event.connection.send( of.ofp_flow_mod( action = of.ofp_action_output( port = of.OFPP_NONE), priority = 65535,
            match = of.ofp_match(dl_src = policy.dl_src, dl_dst= policy.dl_dst)))

            #policy for opposite direction and installing this message to switch flowtable
            event.connection.send( of.ofp_flow_mod( action = of.ofp_action_output( port = of.OFPP_NONE), priority = 65535,
            match = of.ofp_match(dl_src = policy.dl_dst, dl_dst= policy.dl_src)))

            # debug
            log.info("Installing firewall rule for src=%s, dst=%s" % (policy.dl_src, policy.dl_dst))
            
        
        log.debug("Firewall rules installed on %s", dpid_to_str(event.dpid))



class l2_learning (object):
 
  def __init__ (self):
    core.openflow.addListeners(self)
    

  def _handle_ConnectionUp (self, event):
    log.debug("Connection %s" % (event.connection,))
    LearningSwitch(event.connection)



def launch ():
  core.registerNew(l2_learning)             #Launching the layer two switch 
  core.registerNew(FirewallPlugin)                                  #Launch the Firewall Plugin
