#!/usr/bin/env python2

import os.path
import sys
import socket
import math
# I'm not using urlib on purpose, for learning

def parse_input():
    usage = "Usage:" + sys.argv[0] + " URL. URL must start with 'http://'"
    if '-h' in sys.argv or 'help' in sys.argv:
        print usage
    elif len(sys.argv) == 2 and sys.argv[1].startswith('http://'):
        # remove http://
        urlString = sys.argv[1].replace('http://', '', 1)
        # URL object stores domain and path separately
        url = URL(urlString)
        download(url)
    else: 
        print usage


def download(url):
    ''' downloads file pointed to by URL object '''
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
    if firstpiece.count(DELIMITER * 2) == 0:
        # not an HTTP response?
        s.close()
        raise Exception #TODO
 
    # parse the response
    (httpresponse, data) = tuple(firstpiece.split(DELIMITER * 2, 1))
    (codestring,headerstring) = tuple(httpresponse.split(DELIMITER,1))
    headerlist = headerstring.split(DELIMITER)
    headers = {h[0].strip(): h[1].strip() for h in \
        [i.split(':', 1) for i in headerlist if i.find(':') != -1]}

    # check response codes TODO

    # get content length
    total_size = int(headers['Content-Length'])

    # make a file name
    filename = os.path.basename(url.path)

    downloaded = len(data)
    with open(filename, 'w') as fp:
        fp.write(data)
        while True:
            data = s.recv(4096)
            downloaded += len(data)
            print str(int(math.floor(float(downloaded) / \
                total_size * 100))) + '%'
            if not data:
                print "Done"
                break
            fp.write(data)
        
    s.close()


    # set up a file to download to
    # assuming it's a text file (for windows); otherwise mode need 'b'
    # with ensures the file is closed when this block is done
    #with open('file1', 'w') as fp:
        # do stuff
         # while True:
   #              chunk = req.read(CHUNK)
   #              downloaded += len(chunk)
   #              print math.floor( (downloaded / total_size) * 100 )
   #              if not chunk: break
   #              fp.write(chunk)


''' Example HTTP request (observed with wireshark on real wget):
    GET /~mfrydrychowicz/data/movies-mpaa.txt HTTP/1.1\r\n
    User-Agent: Wget/1.13.4 (linux-gnu)\r\n             # pywget (linux-gnu)?
    Accept: */*\r\n                                     # accept any media type
    Host: sonic.dawsoncollege.qc.ca\r\n                 # repeats URL content
    Connection: Keep-Alive\r\n
    \r\n
'''

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