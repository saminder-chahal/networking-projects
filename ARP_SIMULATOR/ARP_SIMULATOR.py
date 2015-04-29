
                          #ARP Simulator

import os, sys, time
ARP_Table = []
ConfigurationDatabase= {}

def CONFIG_input():
    t = []
    ID = raw_input("Enter Host ID: ")
    t.append(raw_input("Enter MAC: "))
    t.append(raw_input("Enter IP: "))
    t.append(raw_input("Time_out (s): "))

    ConfigurationDatabase[ID] = t
    print "\n", ID, "has been connected.\n"

    return ID 
    
def CONFIG_print():
    t = ConfigurationDatabase.keys()

    for i in range(0, len(t)):
        print ConfigurationDatabase[t[i]]

def CONFIG_ARP_conflict(ID, MAC, IP):
    t = ConfigurationDatabase.keys()
    for i in t:
        if (i != ID):
            t1 = ConfigurationDatabase[i]
            if (t1[1] == IP):
                print "\nARP Re", t1[0], MAC, IP, IP, "\n"
                del ConfigurationDatabase[ID]
                print "\nHost", ID , "has been disconnected.\n"

def CONFIG_ARP(ID):
    t = ConfigurationDatabase[ID]

    print "ARP Request", t[0], "FF:FF:FF:FF:FF:FF", t[1], t[1], "\n"

    CONFIG_ARP_conflict(ID, t[0], t[1])

def CONFIG():

    ID = CONFIG_input()
    #CONFIG_print()
    CONFIG_ARP(ID)
    

def PRINT():
    valid_entry = []
    temp_id = ConfigurationDatabase.keys()
    
    host_id = raw_input("Enter Host ID: ")

    count = len(ARP_Table)
    if count == 0:
        print "\n Error: Unknown host " ,host_id
    else:   
        # check if host_id is in Host table
        host_entry_found = 0
        for i in temp_id:
            if host_id == i:
                host_entry_found = 1
                
        # check if host_id is in ARP table
        valid_entry = ARP_Table[0]
        count_2 = len(valid_entry)
        for i in range(0, count_2):
            if host_id == valid_entry[i] and host_entry_found == 1:
                ct = int(time.time())                                       #checking timeout in Arp_table
                elapsed_time = ct - valid_entry[i+3]
                if elapsed_time <= 0:
                    print "\n mac_addr: ", valid_entry[i+1], "ip_addr: ", valid_entry[i+2]
                    return
                
        # Correct host entered but no corresponding ARP entry
        if host_entry_found == 1:
            print("\nNo Entries")
            return
        
        # Incorrect host entered
        print "\n Error:Unknown host ", host_id
        return
                    
def RESOLVE_input():
    ID = raw_input("Enter Host ID: ")
    IP = raw_input("Enter Destination IP: ")

    if ID not in ConfigurationDatabase.keys():
        print "\nHost", ID, "does not exist"
        return 0, 0
        
    return ID, IP
  

def RESOLVE_find_dest(IP):
    t = ConfigurationDatabase.keys()

    # search for IP
    for i in t:
        t1 = ConfigurationDatabase[i]
        if (t1[1] == IP):
            return i
        
    # IP not found
    return 0        

def RESOLVE_update(t1):
    count = len(ARP_Table)
    
    if (count == 0):
        ARP_Table.append(t1)
        return

    for i in range(0, count):
         if (ARP_Table[i][0] == t1[0] and ARP_Table[i][2] == t1[2]):
             ARP_Table[i] = t1
             return
    
    ARP_Table.append(t1)
    ARP_Table.sort()
    	
def RESOLVE():
    
    ID, IP = RESOLVE_input()    

    if (ID != 0):
        t = ConfigurationDatabase[ID]
        print "\nARP Request", t[0], "FF:FF:FF:FF:FF:FF", t[1], IP, "\n"

        dID = RESOLVE_find_dest(IP)

        if dID == 0:
            print ID,"could not resolve",IP
        else:    
            z = ConfigurationDatabase[dID]
            print "\nARP Response",z[0],t[0],z[1],t[1]
            print ID,"resolved",z[1],"to",z[0]

            ct = int(time.time())
            t1 = []
            t1.append(ID)
            t1.append(z[0])
            t1.append(z[1])
            t1.append(int(z[2]) + ct)
            t1.append(dID)
            t1.append(t[0])
            t1.append(t[1])
            t1.append(int(t[2]) + ct)
            RESOLVE_update(t1)

print("\n\tWelcome to ARP Simulator v1.0\n")
while True:
    Input = raw_input("Enter your choice (config, print_table, resolve_addr, quit) : ")
    
    if (Input == "quit"):
        print "Good bye ..."
        break

    if (Input == "config"):
        CONFIG()

    if (Input == "print_table"):
        PRINT()

    if (Input == "resolve_addr"):
        RESOLVE()

    

    
