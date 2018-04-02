#!/usr/bin/env python3

'''
A simple authenticated web server handler
'''

from http.server import BaseHTTPRequestHandler, HTTPServer, CGIHTTPRequestHandler

#from SimpleHTTPServer import SimpleHTTPRequestHandler
import os
import sys
import base64
import ssl
import socketserver
import argparse
import time

#from . import __prog__

CERT_FILE = os.path.expanduser("~/.ssh/cert.pem")
KEY_FILE = os.path.expanduser("~/.ssh/key.pem")
SSL_CMD = "openssl req -newkey rsa:2048 -new -nodes -x509 "\
            "-days 3650 -keyout {0} -out {1}".format(KEY_FILE, CERT_FILE)

class SimpleHTTPAuthHandler(CGIHTTPRequestHandler):
    ''' Main class to present webpages and authentication. '''
    KEY = ''
    cgi_directories = ["/cgi-bin"]

    def do_HEAD(self):
        ''' head method '''
        print("send header")
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_authhead(self):
        ''' do authentication '''
        print("send header")
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Test\"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        ''' Present frontpage with user authentication. '''
        if self.headers.get('Authorization') is None:
            self.do_authhead()
            self.wfile.write(b'no auth header received')
        elif self.headers.get('Authorization') == 'Basic '+ self.KEY:
            #SimpleHTTPRequestHandler.do_GET(self)
            CGIHTTPRequestHandler.do_GET(self)
        else:
            self.do_authhead()
            self.wfile.write(self.headers.get('Authorization'))
            self.wfile.write('not authenticated')

#def serve_https(https_port=80, https=True, start_dir=None, handler_class=SimpleHTTPAuthHandler):
#    ''' setting up server '''
#    httpd = socketserver.TCPServer(("", https_port), handler_class)
#
#    if https:
#        httpd.socket = ssl.wrap_socket(httpd.socket, keyfile=KEY_FILE,
#                                       certfile=CERT_FILE, server_side=True)
#
#    if start_dir:
#        print("Changing dir to {cd}".format(cd=start_dir))
#        os.chdir(start_dir)
#
#    socket_addr = httpd.socket.getsockname()
#    print("Serving HTTP on", socket_addr[0], "port", socket_addr[1], "...")
#    httpd.serve_forever()

def main():
    ''' Parsing inputs '''
#    parser = argparse.ArgumentParser(prog=__prog__)
#    parser.add_argument('port', type=int, help='port number')
#    parser.add_argument('key', help='username:password')
#    parser.add_argument('--dir', required=False, help='directory')
#    parser.add_argument('--https', help='Use https', action='store_true', default=False)
#    args = parser.parse_args()

#    if args.https:
#        if not (os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE)):
#            print >>sys.stderr
#            print >>sys.stderr, "Missing {} or {}".format(CERT_FILE, KEY_FILE)
#            print >>sys.stderr, "Run `{}`".format(SSL_CMD)
#            print >>sys.stderr
#            sys.exit(1)

    SimpleHTTPAuthHandler.KEY = base64.b64encode(bytes("USER:PASS", 'utf-8')).decode("utf-8")

#    serve_https(int(81), https='', start_dir='/opt/web/root', handler_class=SimpleHTTPAuthHandler)

    hostName=""
    hostPort=80
    os.chdir("/opt/SmartHouse/web/root")
    myServer = HTTPServer((hostName, hostPort), SimpleHTTPAuthHandler)
    print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

    try:
        myServer.serve_forever()
    except KeyboardInterrupt:
        pass

    myServer.server_close()
    print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))




if __name__ == '__main__':
    main()
