  #SAMINDERJIT SINGH CHAHAL                 #CCID-schahal , ALberta#1448705


#IMPORTANT NOTE : - I have not decreemented the value of TTL ,i assume if TTL value is 1 when it reaches to router so it will drop the packet as we did in our class.


#Welcome Message
print "\nWelcome to packet Switching Simulator \n"                
print "Please provide <port number to listen at> <routing table file path> <statistics file path>\n"

import sys
import socket
import time
import random


def IPtoInt(dest):     # please look for a built-in function
    l = dest.split(".")
    n = int(l[0])
    n = n * 256 + int(l[1])
    n = n * 256 + int(l[2])
    n = n * 256 + int(l[3])

    return n
   
def check(dest, bits, net):
    n = IPtoInt(dest)

    a = ""
    for i in range(0, bits):
        a = a + "1"

    for i in range(0, 32 - bits):
        a = a + "0"

    if (n & int(a,2)) == IPtoInt(net):
        return 1
    else:
        return 0


expired_packets = 0
unroutable_packets = 0
delivered_direct = 0
toRouterB = 0
toRouterC = 0
count=0


netmask=[]
dest_net=[]
nexthop=[]

portnum = sys.argv[1]
rtfile = sys.argv[2]
stfile = sys.argv[3]


try:
    with open(rtfile,'r') as routingtable:
        data=routingtable.readlines()
        for line in data:
            words=line.split()
            netmask.append(int(words[0]))
            dest_net.append(words[1])
            nexthop.append(words[2])
except IOError:
    print " Can not find Routingtable file!\n"                 #if routing table file does not exist or entered incorrect filename
    sys.exit()
    


def updatestatisticfile(stfile):
    try:
        statisticalfile = open (stfile,'w')
        statisticalfile.write("expired packets: %d\n"%expired_packets)
        statisticalfile.write("Unroutable packet: %d\n"%unroutable_packets)
        statisticalfile.write("delivered direct: %d\n"%delivered_direct)
        statisticalfile.write("to router B: %d\n"%toRouterB)
        statisticalfile.write("to router C: %d\n"%toRouterC)
    except IOError:
        print "Error occured while updating the statistics file!\n"
        
        
def statisticfile(stfile):
    try:
        global count
        count = count + 1
        if (count == 20):
            print "20 packets received"
            updatestatisticfile(stfile)
            count=0                                    #reset counter
    except IOError:
        print "Error occured:Statistic file not found\n"
           
    


if (len(sys.argv) != 4):                                    #Checking if user has entered valid number of argument or not
	print "Wrong arguements entered \n"
	sys.exit()
	

try:
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverSocket.bind(('127.0.0.1', int(portnum)))

except IOError:
    print " Error: Can not connect to the udp port"


try:
    while True:
        try:
            packet, address = serverSocket.recvfrom(65535)
            print packet
            l = packet.split()
            if int(l[3]) == 1:
                expired_packets = expired_packets + 1
            else:
                if check(l[2], netmask[0], dest_net[0]):
                    toRouterB = toRouterB + 1
                else:
                    if check(l[2], netmask[1], dest_net[1]):
                        print"Delivering direct: packet ID=",l[0],"dest=",l[2]
                        delivered_direct = delivered_direct + 1
                    elif check(l[2], netmask[2], dest_net[2]):
                        toRouterC = toRouterC + 1
                    else:
                        unroutable_packets = unroutable_packets + 1
                        
        except KeyboardInterrupt:
            print "\nStatistic file has been updated\n"      #updating statistic file when Ctrl+C operation happenned
            print "program has been terminated!"
            updatestatisticfile(stfile)
            serverSocket.close()
            sys.exit()
        except IOError:
            print "Error occured while receiving packet but no worries I will catch the next one.\n"
    statisticfile(stfile)
        
except IOError:
    print "Can not receive/listen to the client now\n"
    sys.exit()
