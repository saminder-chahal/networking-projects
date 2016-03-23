#Welcome Message
print "\nWelcome to packet Switching Simulator v1.0\n"
print "Please use these two arguements while running prog:<port number to connect to router> <packets file path>"
import socket
import sys
import time
import random

portnum=sys.argv[1]
pfile=sys.argv[2]

NetAtoNetB = 0
NetAtoNetC = 0
NetBtoNetA = 0
NetBtoNetC = 0
NetCtoNetA = 0
NetCtoNetB = 0
InvalidDestination = 0
ID = 0
count = 0
      

def SRC():                                                 # getting source IP
    t=random.randint(0,2)
    if t == 0:
        n=random.randint(0,1)
        if n == 0:
            return "192.168.128.7",t
             
        elif n == 1:
            return "192.168.128.1",t
    elif t == 1:
        n=random.randint(0,2)
        if n == 0:
            return "192.168.192.10",t
        elif n == 1:
            return "192.168.192.6",t
        elif n == 2:
            return "192.168.192.4",t
    elif t == 2:
        n=random.randint(0,3)
        if n == 0:
            return "192.224.0.5", t
        elif n == 1:
            return "192.224.10.5",t
        elif n == 2:
           return "192.224.0.7",t
        elif n == 3:
            return "192.224.10.5",t
def DEST():                                               # getting destination IP
    z=random.randint(0,3)
    if z == 0:
        n=random.randint(0,1)
        if n == 0:
            return "192.168.128.7",z
             
        elif n == 1:
            return "192.168.128.1",z
    elif z == 1:
        n=random.randint(0,2)
        if n == 0:
            return "192.168.192.10",z
        elif n == 1:
            return "192.168.192.6",z
        elif n == 2:
            return "192.168.192.4",z
    elif z == 2:
        n=random.randint(0,3)
        if n == 0:
            return "192.224.0.5", z
        elif n == 1:
            return "192.224.10.5",z
        elif n == 2:
           return "192.224.0.7",z
        elif n == 3:
            return "192.224.10.5",z
    elif z == 3:
         return "168.130.192.1",z
def TTL():                                          # getting Time to live
     x=random.randint(0,3)
     if x == 0:
         return 1
     elif x == 1:
         return 2
     elif x == 2:
         return 3
     elif x == 3:
         return 4
def create_packet():
    global ID
    global NetAtoNetB
    global NetAtoNetC
    global NetBtoNetA
    global NetBtoNetC
    global NetCtoNetA
    global NetCtoNetB
    global InvalidDestination
    global count
    packet = ""
    ID = ID + 1                                      # increementing ID
    src, t = SRC()
    dest,z = DEST()
    ttl = TTL()
    payload = "Hello Saminder"                       # Data

    packet = str(ID) + " " + str(src) + " " + str(dest) + " " + str(ttl) + " " + payload                        #Packet formation
    
    if ( t == 0 and z == 1):
        NetAtoNetB=NetAtoNetB + 1
        return packet
    elif (t == 0 and z == 2):
        NetAtoNetC=NetAtoNetC + 1
        return packet
    elif (t == 1 and z == 0):
        NetBtoNetA=NetBtoNetA + 1
        return packet
    elif (t == 1 and z == 2):
        NetBtoNetC=NetBtoNetC + 1
        return packet
    elif (t == 2 and z == 0):
        NetCtoNetA=NetCtoNetA + 1
        return packet
    elif (t == 2 and z == 1):
        NetCtoNetB=NetCtoNetB + 1
        return packet
    elif (t == z):                                 # if destination and source networks are same
        return 0
    else:
        InvalidDestination=InvalidDestination + 1
        return packet
    
def updatepacketfile(pfile):
    try:
        packetfile = open (pfile,'w')
        packetfile.write("Net A to Net B:%d\n"%NetAtoNetB)
        packetfile.write("Net A to Net C:%d\n"%NetAtoNetC)
        packetfile.write("Net B to Net A:%d\n"%NetBtoNetA)
        packetfile.write("Net B to Net C:%d\n"%NetBtoNetC)
        packetfile.write("Net C to Net A:%d\n"%NetCtoNetA)
        packetfile.write("Net C to Net B:%d\n"%NetCtoNetB)
        packetfile.write("InvalidDestination:%d"%InvalidDestination)
        
        
    except IOError:
        print"Can not update Packet file,but no worries try next time\n"
       

   
def packetfile(pfile):
    try:
        global count
        count = count + 1
        if (count == 20):
            print "\n Packet file has been updated\n"
            updatepacketfile(pfile)
            count=0                                  #reset counter
    except IOError:
        print " Error occured packet file not found\n"

if (len(sys.argv) != 3):                                    #Checking if user has entered invalid number of argument 
	print "Wrong arguements entered \n"
	sys.exit()


while True:
    try:
        packet = create_packet()
        packetfile(pfile)
        if (packet!=0):
            print packet
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.sendto(str(packet), ('127.0.0.1', int(portnum)))
            except IOError:
                print "Can not connect to port\n"
                sys.exit()
        time.sleep(1)
        
    except KeyboardInterrupt:
        print "\nPacket file has been updated\n"      #updating packetfile when Ctrl+C operation happened
	print "program has been terminated!,so no more packets will be generated\n"
	updatepacketfile(pfile)
	s.close()
	sys.exit()

    

        

