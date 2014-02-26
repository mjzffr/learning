#!/usr/bin/env python2
import socket
# test with nc -l localhost -p 12345
def send_one_message():
    print 'connecting to localhost at port 12345'
    # create an INET, STREAMing socket
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect(('localhost', 12345))
    print clientsocket.recv(8)
    # message is exit to make echo_server.py close its connection
    clientsocket.send('exit')
    clientsocket.close()
    exit()

if __name__ == "__main__":
    send_one_message()