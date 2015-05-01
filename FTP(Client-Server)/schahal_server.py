#SAMINDERJIT SINGH CHAHAL                        
#Welcome Message
print "\nWelcome to packet Switching Simulator \n"                
print "Please provide <port number to listen at> <directory from where the server serves files to the clients> <log file path>\n"

import thread, socket, time, sys, os

#Declaring command-line arguements
portnum = sys.argv[1]
sfile=sys.argv[2]
logfile = sys.argv[3]

def Logfile(y,z,data,address):                 
    try:
        ip=address[0]
        port=address[1]
        lfile = open (logfile,'a')
        lfile.write("client IP is:%s"%ip)
        lfile.write("\t client port is:%s"%port)
        lfile.write("\t name of file sent is:%s"%data)
        lfile.write("\t time when request received is:%d"%z)
        lfile.write("\t time when file transmission completed is:%d\n\n"%y)
        

    except:
        print "Error occured while updating the log file!\n"
 

def Logfileupdate(z,data,address):
    try:
        ip=address[0]
        port=address[1]
        lfile = open (logfile,'a')
        lfile.write("client IP is:%s"%ip)
        lfile.write("\t client port is:%s"%port)
        lfile.write("\t name of file to be sent is:%s"%data)
        lfile.write("\t time when request received is:%d"%z)
        lfile.write("\t file not found\n\n")

    except IOError:
        print "Error occured while updating the log file!\n"

def Logfile_transmission_uncompleted(z,data,address):
    try:
        ip=address[0]
        port=address[1]
        lfile = open (logfile,'a')
        lfile.write("client IP is:%s"%ip)
        lfile.write("\t client port is:%s"%port)
        lfile.write("\t name of file to be sent is:%s"%data)
        lfile.write("\t time when request received is:%d"%z)
        lfile.write("\t transmission not completed \n\n")

    except IOError:
        print "Error occured while updating the log file!\n"
    
def serve_file(data,address,z):
    server = sfile + '\\' + data
    try:
        fin = open(server, "r")                     #To open file and read 1024 bytes at one time
        s = fin.read(1024)
        file_size=os.path.getsize(server)
        print "file size:",file_size
        try:
            while (s):
                time.sleep(3)
                serverSocket.sendto(s, address)                        #sending data to client
                s = fin.read(1024)
            if file_size % 1024 == 0:                                              #To add $ sign if file is multiple of KB
                serverSocket.sendto("$",address)
            y=time.time()                                                      #Current time when file transmission completed
            fin.close()
            Logfile(y,z,data,address)
    
        except IOError:
            Logfile_transmission_uncompleted(z,data,address)                       #Transmission not completed entry in logfile
    except:
        Logfileupdate(z,data,address)                                          #File not found entry
            
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)                 #To attach a socket in udp mode
serverSocket.bind(('127.0.0.1', int(portnum)))
print "\nServer is listening..."

while True:
    try:
        data, address = serverSocket.recvfrom(65535)
        z=time.time()                                     #Current time when file request arrived
        thread.start_new_thread(serve_file,(data,address,z,))                         

    except KeyboardInterrupt:                   #To exit if CTRL+C or other command used to interrupt server.
        print "\n\nServer is aborting all trnsmissions...\n"
        print "\n\nExiting...\n"
        serverSocket.close()
        cleanup_thread.stop_new_thread();
        sys.exit()
    
    
