#!/usr/bin/env python2
import socket

def start_server():
    print 'run `nc localhost 12345` from another terminal to connect'
    # create an INET, STREAMing socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind the socket to a public host, using localhost instead of
    # socket.gethostname()
    serversocket.bind(('localhost', 12345))
    # become a server socket, max k=1 connect requests can be in queue
    serversocket.listen(1)

    # accept one connection from outside; print until client says 'exit'
    (clientsocket, address) = serversocket.accept()
    print 'Connection from' + str(address)
    clientsocket.send('Hello!\n')
    while True:
        msg = clientsocket.recv(8)
        #print(msg)
        if msg.startswith('exit'):
            print "no!"
            break
        else:
            print msg
    serversocket.close()
    exit()

if __name__ == "__main__":
    start_server()