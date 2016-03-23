Designed and developed a layer 3 switch application using Ryu SDN controller, mininet and OpenFlow v1.3 which sends LLDP packets between the switches to detect link failure problems, updates ARP tables for new flow , flow tables with idle timeout and hard timeouts , switches send port state changes and flowstat requests to the controller in case port is added ,deleted or modified.

Algorithm: Controller remembers all the switches connected. After boot a new thread is connected for a function that polls switches for FlowStats, every 3 seconds. Stat replies are stored and printed out on a screen on every packetin.

ENVIRONMENT SETUP:


    1. Install Ubuntu or other linux operating system. (http://www.ubuntu.com/download/desktop)
    
    2. Install Git by typing "sudo apt-get install git" in the terminal.
    
    3. Install Mininet: Mininet is a network emulator which can create a network of hosts, links and switches on a single machine. Installing the mininet from github is very easy use the following command from your home directory to install it:
       "git clone https://github.com/mininet/mininet.git"
       
    4. Install SDN POX Controller by typing "git clone https://github.com/noxrepo/pox.git"

After we are done, typing "sudo mn" from inside the mininet directory should create a default mininet topology. Then run Ryu controller from other terminals and they should connect to each other using port 6633 by default.

Then, keep on changing the mininet topologies to single switch four hosts; mesh topologies; linear topologies etc and my controller performs all the layer2 and layer3 switching operations while printing the flow stats every 3 seconds on the controller console.
