#SAMINDERJIT SINGH CHAHAL    
import os, socket, time,sys

IP=sys.argv[1]                     #To declare arguments according to problem given
udpport=sys.argv[2]
filename=sys.argv[3]

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)          #Creating a udp socket

s.sendto(filename, (IP, int(udpport)))                        # To send a file request to server

client_file = ""                    #Global declaration of variable where client stores its data received from server.
while True:              
    try:
        s.settimeout(5)                               #To give timeout condition to client 
        data, address = s.recvfrom(65535)            
        #Here no need to run any 1KB chunk condition because server already sending it in 1KB chunks                                                                      
        print data
        if data != '$':                             #To remove dollar sign if present in data received from server.
            client_file = client_file + data         #To add data in client file if there is no dollar sign.
        
        
    except socket.timeout:                                
        #To make client enable after 5 seconds that file is transmitted or some error occured.
        print "\n Timed out, Error"
        time.sleep(1)                                             #To make it visible that after 5 sec client aborted.
        print "CLIENT FILE SAVED BY REMOVING DOLLAR SIGN IF ANY"
        print "Content of Actual CLIENT File saved is : \n",client_file   #To display content that $ sign has been removed on the client side
        s.close()
        exit()
   
        
        

