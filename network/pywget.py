#!/usr/bin/env python2

import os.path
import sys
import socket
import math
# I'm not using urlib on purpose!

def parse_input():
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

def download(url, filename):
    ''' downloads file pointed to by URL `url` to str `filename` '''
    DELIMITER = '\r\n'
    # create an INET, STREAMing socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect to the web server on port 80: this socket will be used
    # for one request and one reply and then be destroyed

    # TODO: add exception handling; what if the connection is unsuccessful
    s.connect((url.domain, 80))

    # construct an HTTP request
    request =   "GET " + url.path + " HTTP/1.1" + DELIMITER + \
                "User-Agent: pywget (linux-gnu)" + DELIMITER + \
                "Accept: */*" + DELIMITER  + \
                "Host: " + url.domain + DELIMITER + \
                "Connection: Keep-Alive" + DELIMITER * 2           

    s.send(request)

    # distinguish http response from its payload
    firstpiece = s.recv(1024)
    if firstpiece.find(DELIMITER * 2) == -1 or \
        not firstpiece.startswith('HTTP'):
        print "Not an HTTP response?!"
        s.close()
        sys.exit()
        
    # parse the response
    (httpresponse, data) = tuple(firstpiece.split(DELIMITER * 2, 1))
    (codestring,headerstring) = tuple(httpresponse.split(DELIMITER,1))

    # check response codes TODO
    if codestring.find('200') == -1:
        print codestring
        s.close()
        sys.exit()

    headerlist = headerstring.split(DELIMITER)
    headers = {h[0].strip(): h[1].strip() for h in \
        [i.split(':', 1) for i in headerlist if i.find(':') != -1]}

    
    # get content length
    try:
        total_size = int(headers['Content-Length'])
    except KeyError as e:
        print str(e) + ' not found'
        s.close()
        sys.exit()

    # download pieces
    filename = os.path.basename(url.path)
    downloaded = len(data)
    with open(filename, 'w') as fp:
        fp.write(data)
        while downloaded < total_size:
            data = s.recv(4096)
            if not data:
                print 'Connection lost?'
                break
            downloaded += len(data)
            print str(int(math.floor(float(downloaded) / \
                total_size * 100))) + '%'
            fp.write(data)
        
    s.close()


def get_progress_str():
    pass


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
    parse_input()