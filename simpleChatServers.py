#!/usr/bin/env python2

import socket
import select
import sys

'''
idea: lots of clients (e.g use netcat) can connect to this server
and the server will echo what client k sends to all clients. 
(A chat server!)
(learning goal: reimplement what tom demo'ed the other day)

Note (Check this):  a.send(m) := send m TO a
                    a.recv(x) := receive  <= x bytes FROM a
'''

def bind_listening_socket():
    # default params are INET and STREAM
    s = socket.socket()
    #prevent the "already in use error"
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # TODO: bind raises an exception if 8000 is already in use
    s.bind(('localhost', 8000))
    s.listen(5)

    return s

def start_terrible_server():
    '''To accept many connections on blocking sockets, need threads.
    This is why I make the sockets non-blocking; otherwise the main loop
    will get stuck.
    '''

    clients = []
    listener = bind_listening_socket()
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
        except socket.error, e:
            # we're ignoring the exception because the point of this
            # terrible server is to keep looping until a connection is made
            print e

        # collect a message from each client, if available
        for cur_client in clients:
            msg = ''
            try:
                msg = cur_client.recv(1024)
            except socket.error, e:
                # same idea as exception above: this is the point
                # of this terrible server
                print e
            if msg != '':
                # and send the message to everyone
                for otherclient in clients:
                    if otherclient is not cur_client:
                        otherclient.send(msg) 

    # TODO: what about closing the connections? Important?

def start_nicer_server():
    ''' Uses select to only handle sockets that are ready/available.'''
    
    listener = bind_listening_socket()

    # listening socket should be examined by select too so that it doesn't
    # block on "accept"
    # Including stdin to allow 'exit' command on server side
    all_input = [listener,sys.stdin]
    all_clients = []

    while True:
        # pull out the sockets that are ready to be read from
        # i.e. ready to recv/accept?
        # aside/experiment: time-out 0 (i.e. select(x,x,x,0)) used 
        #   a lot of CPU resources 
        ready_input, _, _ = select.select(all_input, [], [])

        for cur_input in ready_input:
            # accept a client connection
            if cur_input is listener:
                clientsocket, address = listener.accept()
                all_input.append(clientsocket)
                all_clients.append(clientsocket)
                clientsocket.send("Hello to " + str(address) + '\n')
            elif cur_input == sys.stdin:
                if (sys.stdin.readline()).strip() == 'exit':
                    # TODO: important to close all the client sockets, too?
                    listener.close()
                    sys.exit()
            # collect a message from each ready client
            # ask about this (excluding listener)
            # Maybe better to just move the listener to different select?
            else:
                msg = cur_input.recv(1024)
                if msg:
                    # and send the message to everyone
                    # (check allInput not readyInput because we're sending
                    # to them not receiving from them)
                    for otherinput in all_clients:
                        if otherinput is not cur_input:
                            otherinput.send(msg) 

if __name__ == "__main__":
    start_nicer_server()