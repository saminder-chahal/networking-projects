INTRODUCION:

SDN created the whole new world of network design and enabled the innovative approaches to networking due to the separation of control plane and the data plane. Thus, SDN also caused us to reconsider how the security policies are enforced in the network.

Open vSwitch has traditionally supported only stateless matches on the policies. However, work is being done by the Open vSwitch community to have connection tracking to maintain the state tables of existing sessions.If any organisation requires the stateful firewall protections specifically, then they must use the SDN policies to steer the traffic with service-chaining toward a stateful packet inspection Network Function Virtualization (NFV) firewall.

I deployed the firewall as a service for hierarchical multi-tenant Data Center network by provisioning rules to allow specific source MAC addresses to communicate specific Tenants while resolving the conflict between the standard programmed flow and Firewall programmed flows.

My research work can be divided into following key points:
  1. Deploy Hierarchical multi-Tenant Data Center network in the automated manner using Mininet Python API infrastructure simulation.
  2. Then deploy Python based SDN Controller (POX) in layer 2 switch mode and verify end to end connectivity of the hosts.
  3. Finally deploy the firewall plugin in the layer 2 switch controller which installs the firewall flow rules by reading the csv   
     file containing the rules taking care to resolve the conflicts between standard programmed flow and firewall programed flows.
  

HARDWARE REQUIREMENTS:
One compute node that can scale to install mininet on ubuntu with FW plugin and POX controller binaries.

ENVIRONMENT SETUP:
    
    METHOD 1:
        1. Install Ubuntu or other linux operating system.(http://www.ubuntu.com/download/desktop)
        2. Install Git by typing "sudo apt-get install git" in the terminal.
        3. Install Mininet: Mininet is a network emulator which can create a network of hosts, links and switches on a single machine.            Installing the mininet from github is very easy use the following command from your home directory to install it:
           "git clone https://github.com/mininet/mininet.git"
        4. Install SDN POX Controller by typing "git clone https://github.com/noxrepo/pox.git"
        
    METHOD 2:
       1. Install VM Imagage with Mininet pre installed from https://github.com/mininet/mininet/wiki/Mininet-VM-Images
          Simply download the vm image from the above link and import in to your own VM. This VM has mininet, git and vim  
          pre-installed with it. 
       2. Then install POX same as mentioned above by running git clone https://github.com/noxrepo/pox.git


IMPLEMENTATION:
 1. Type “sudo mn –controller=remote –topo=single, 4 –mac” to create a single switch with four hosts on Mininet in the Terminal.
 2. Now with mininet running in one terminal , open the other terminal and go inside the pox repository and type “python pox.py   log.level –DEBUG forwarding.l2_learning” to run the pox controller to connect to the mininet using OpenFlow protocol.
 3. Verify end to end connectivity by typing "pingall" in mininet console. At this point every host should communicate with other hosts over the network we created.  
 4. Now, to implement our Firewall orchestration, copy and paste the Firewall.py file of this project inside the pox controller   
    repository at /pox/pox/forwarding location.
 5. Finally, paste our Firewall rules file inside the pox repository from where we run our pox controller and our job is done.

So, after implementing all the steps mentioned above our Firewall Plugin should work and hosts mapped in rules file should not be able to ping each other.

Note: You can type "sudo ovs-ofctl dump-flows s1" to check the current flow table entries on our switch.
