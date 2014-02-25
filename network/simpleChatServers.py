#!/usr/bin/env python2

import socket
import select
import sys
import errno

'''
idea: lots of clients (e.g use netcat) can connect to this server
and the server will echo what client k sends to all clients. 
(A chat server!)
(learning goal: reimplement what tom demo'ed the other day)

Note:  a.send(m) := send m TO a
                    a.recv(x) := receive  <= x bytes FROM a

Some of the select stuff is modelled after http://pymotw.com/2/select/
'''

HOST = 'localhost'
PORT = 50000
SIZE = 1024

def bind_listening_socket():
    print "Server on"
    # default params are INET and STREAM
    s = socket.socket()
    #prevent the "already in use error"
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # TODO: bind raises an exception if port is already in use
    s.bind((HOST, PORT))
    s.listen(5)

    return s

# Exploring non-blocking sockets
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

def print_sockets(list):
    print '[',
    for l in list:
        if isinstance(l, socket.SocketType):
            try:
                print str(l.getpeername()) + ', ',
            except socket.error:
                print 'S:' + str(l.getsockname()) + ', ',
    print ']'

def start_client():
    s = socket.socket()
    s.connect((HOST,PORT))
    # A port is assigned to s after the above connection is established
    (s_ip, s_port) = s.getsockname()
    readables = [s, sys.stdin]

    while True:
        ready_rds, _, _ = select.select(readables, [], [])
        for input in ready_rds:
            if input is sys.stdin:
                line = sys.stdin.readline()
                if line.strip() == 'exit':
                    s.send(str(s_port) + " left.\n")
                    # "If you want to close a connection in a timely fashion
                    # call shutdown() before close(). This doesn't really help
                    # the exceptions I encounter though."
                    s.shutdown(socket.SHUT_RDWR)
                    s.close()
                    sys.exit()
                s.send(str(s_port) + ": " + line)
                display_prompt()
            if input is s:
                data = input.recv(SIZE)
                if len(data) == 0:
                    print '\nConnection lost'
                    s.shutdown(socket.SHUT_RDWR)
                    s.close()
                    sys.exit()
                else:
                    sys.stdout.write('\n' + data)
                    display_prompt()

def display_prompt():
    ''' prompt used by client '''
    sys.stdout.write('>>')
    ''' sys.stdout.write() isn't guaranteed to display text 
    immediately, so flush. Same problem with print''' 
    sys.stdout.flush()


class NicerServer:
    def __init__(self, listener):
        self.readables = []
        self.writables = []
        self.allsockets = []
        self.listener = listener

    def run(self):
        ''' Uses select to only handle sockets that are ready/available.'''

        '''listening socket should be examined by select too so that it doesn't
            block on "accept".
            Including stdin to allow 'exit' command on server side
            (readline() is also blocking) '''
        self.readables = [self.listener,sys.stdin]
        self.allsockets = [self.listener]
        # Outgoing messages (socket:string)
        #message_queues = {}
        
        while True:
            ''' 
            select the sockets that are ready for blocking calls
                like recv and accept

            notes/experiments: 
            * time-out 0 (i.e. select(x,x,x,0)) used a lot of CPU resources
            * I originally used select to only monitor readable streams 
            (ready_inputs). This is bad because clients in this list are not 
            necessarily ready to be sent to, so now I also keep track of the 
            writeable streams in ready_recipients. I did this because I was running 
            into a socket error after a client disconnected; according to select, 
            the disconnected client was still ready for reading.
            * Select doesn't actually detect if a connection is closed! It just 
            monitors if there is data available to be read/if there is room in the
            object's buffer to write. (I think.)

            questions:
            * when using select, does it matter whether the sockets are blocking or
            non-blocking? My impression is that select prevents you from having to
            use non-blocking sockets.
            '''

            # wait for at least one of the sockets to be ready
            # print "Readable"
            # print_sockets(self.readables)
            # print "Writable"
            # print_sockets(self.writables)
            # print "All Sockets"
            # print_sockets(self.allsockets)
            ready_rds, ready_wrs, exceptional = \
                select.select(self.readables, self.writables, self.allsockets)

            # Process incoming data
            for input in ready_rds:
                # accept a client connection
                if input is self.listener:
                    clientsocket, address = self.listener.accept()
                    self.readables.append(clientsocket)
                    self.writables.append(clientsocket)
                    self.allsockets.append(clientsocket)
                    # assuming that the accept() call was successful
                    clientsocket.send("Hello to " + str(address) + '\n')
                elif input is sys.stdin:
                    if (sys.stdin.readline()).strip() == 'exit':
                        # (?): assume that client is responsible for closing
                        # its connection
                        self.listener.close()
                        print "Server off"
                        sys.exit()
                # collect a message from each ready client
                else: self.relay_msg(input, ready_wrs)

            # disconnect from any other errorful clients
            #if exceptional: print_sockets(exceptional)
            for s in exceptional:
                for list in [self.readables, self.writables, self.allsockets]:
                    if s in list:
                        list.remove(s)
                s.close()
        
    def relay_msg(self, source, destinations):
        ''' Send message from source to all other clients in destinations list
        '''
        msg = source.recv(SIZE)
        if msg:
            for recipient in destinations:
                #print_sockets(destinations) 
                if recipient is not source:
                    try:
                        recipient.send(msg)
                    except socket.error as e:
                        # remote peer disconnected
                        if isinstance(e.args, tuple) and e[0] == errno.EPIPE:
                            self.disconnect_client(recipient)
                        else:
                            # some other unanticipated issue. :(
                            raise e
        else:
            # no data received means that source has disconnected
            self.disconnect_client(source)

    def disconnect_client(self, s):
        print "Disconnecting: " + str(s.getpeername())
        if s in self.writables:
            self.writables.remove(s)
        if s in self.readables:
            self.readables.remove(s)
        if s in self.allsockets:
            self.allsockets.remove(s)
        s.close()


                


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == 'client':
        start_client()
    else:
        NicerServer(bind_listening_socket()).run()