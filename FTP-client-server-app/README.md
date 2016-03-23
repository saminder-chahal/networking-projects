Implementation of an unreliable (UDP) simplified file server.
The file server is started with three command line arguments. The first argument is a UDP port on which it will listen to service requests 
made by the clients. The second argument is a directory from where the server serves files to the clients. The last argument is a log file in
which the server logs all transactions with all clients.

We will also implement the file client. The client is started with three command line arguments. The first argument is the IP address of
the machine the server is running on, the second argument is the UDP port the server listens to client requests, and the third argument is the name of the file the client is trying to get from the server.
Server and client may run on different machines connected by a network.

IMPLEMENTATION 

SERVER:
$python schahal_server 9090 /some/where/documents /some/where/logfile
This would invoke file_server listening on the local machine on port 9090, serving up files from the directory /some/where/documents, 
and logging transactions to /some/where/logfile.

CLIENT:
$python schahal_client 192.168.10.1 9090 filename
This would invoke file_client sending a transfer request of filename to the server running on 192.168.10.1 and listening to UDP port 9090.
