#!/usr/bin/env python2

import socket

'''
idea: lots of clients can connect to this server
and the server will echo what client k sends to all clients. 
(A chat server!)
(learning goal: reimplement what tom demo'ed the other day)

Test it with netcat: `nc localhost 50000`
'''

HOST = 'localhost'
PORT = 50000
SIZE = 1024

# This function just explores non-blocking sockets
def start_server():
    '''To accept many connections on blocking sockets, need threads.
    This is why I make the sockets non-blocking; otherwise the main loop
    will get stuck.
    '''

    clients = []
    # default params are INET and STREAM
    listener = socket.socket()
    #prevent the "already in use error"
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # TODO: bind raises an exception if port is already in use
    listener.bind((HOST, PORT))
    listener.listen(5)
    listener.setblocking(False)

    # accept client connections
    while True:
            # s is non-blocking so it won't get stuck
        try:
            #but accept() will raise "resource temporarily unavailable"
            # if there's nothing trying to connect?
            clientsocket, address = listener.accept()
            #recv is also blocking, so we need the clients to be non-blocking too
            clientsocket.setblocking(False)           
            clients.append(clientsocket)
            clientsocket.send("Hello to " + str(address) + '\n')
        except socket.error as e:
            # we're ignoring the exception because the point of this
            # terrible server is to keep looping until a connection is made
            print e

        # collect a message from each client, if available
        for cur_client in clients:
            msg = ''
            try:
                msg = cur_client.recv(SIZE)
            except socket.error as e:
                # same idea as exception above: this is the point
                # of this terrible server
                print e
            if msg != '':
                # and send the message to everyone
                for otherclient in clients:
                    if otherclient is not cur_client:
                        otherclient.send(msg) 

if __name__ == "__main__":
    start_server()