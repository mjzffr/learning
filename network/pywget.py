#!/usr/bin/env python2

import os.path
import sys
import socket
import math
# I'm not using urlib on purpose!

DELIMITER = '\r\n'
CONNECTION = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def parse_cmdline():
    usage = "Usage:" + sys.argv[0] + " URL. URL must start with 'http://'"
    if '-h' in sys.argv or 'help' in sys.argv:
        print usage
    elif len(sys.argv) == 2 and sys.argv[1].startswith('http://'):
        # remove http://
        urlString = sys.argv[1].replace('http://', '', 1)
        # URL object stores domain and path separately
        url = URL(urlString)
        filename = os.path.basename(url.path)
        if filename: download(url, filename) 
        else: print 'URL does not specify a file.'
    else: 
        print usage


def parse_httpresponse(firstpiece):
    ''' Returns a tuple (headers, data) where headers is a str:str dictionary
    and data is a str of first part of data. `firstpiece` contains first few 
    bytes of response received as a string.'''
    if firstpiece.find(DELIMITER * 2) == -1 or \
        not firstpiece.startswith('HTTP'):
        stop("Not an HTTP response?!")
        
    # identify the different parts of the response
    (httpresponse, data) = tuple(firstpiece.split(DELIMITER * 2, 1))
    (codestring,headerstring) = tuple(httpresponse.split(DELIMITER,1))

    # check for 200 OK
    if codestring.find('200') == -1:
        stop(codestring)

    # dictionary of headers, e.g. 'Content-Type':'text/html'
    headers = {h[0].strip(): h[1].strip() for h in \
        [i.split(':', 1) for i in headerstring.split(DELIMITER) if \
         i.find(':') != -1]}

    return (headers, data)
    

def download(url, filename):
    # connect to the web server on port 80: this socket will be used
    # for one request and one reply and then be destroyed
    # TODO: add exception handling; what if the connection is unsuccessful?
    CONNECTION.connect((url.domain, 80))

    request =   "GET " + url.path + " HTTP/1.1" + DELIMITER + \
                "User-Agent: pywget (linux-gnu)" + DELIMITER + \
                "Accept: */*" + DELIMITER  + \
                "Host: " + url.domain + DELIMITER + \
                "Connection: Keep-Alive" + DELIMITER * 2           

    CONNECTION.send(request)

    # distinguish http response from its payload
    # what recv returns nothing?! TODO
    (headers, data) = parse_httpresponse(CONNECTION.recv(1024))

    try:
        writefile(data, int(headers['Content-Length']), filename)
    except KeyError as e:
        stop(str(e) + ' not found')

    CONNECTION.close()


def writefile(data, total_size, filename):
    ''' saves downloaded data to `filename`. There might be some initial data in
    `data'''
    downloaded = len(data)
    with open(filename, 'w') as fp:
        fp.write(data)
        while downloaded < total_size:
            data = CONNECTION.recv(4096)
            if not data:
                print 'Connection lost?'
                break
            downloaded += len(data)
            print str(int(math.floor(float(downloaded) / \
                total_size * 100))) + '%'
            fp.write(data)


def stop(msg):
    print msg
    CONNECTION.close()
    sys.exit()


class URL:
    def __init__(self, urlString):
        self.original = urlString
        # split into domain and path
        urlParts = urlString.split('/', 1)
        self.domain = urlParts[0]
        if len(urlParts) == 2:
            self.path = '/' + urlParts[1]
        else:
            self.path = ''

    def __str__(self):
        return 'domain: [' + self.domain + ']; path: [' + self.path + ']'

if __name__ == "__main__":
    parse_cmdline()