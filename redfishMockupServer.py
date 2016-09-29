# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tools/LICENSE.md

# redfishMockupServer.py
# v0.9.1
# tested and developed Python 3.4

import urllib
import cgi
import sys
import getopt

import os
from http.server import BaseHTTPRequestHandler, HTTPServer

class RfMockupServer(BaseHTTPRequestHandler):
        '''
        returns index.json file for Serverthe specified URL
        '''
        server_version = "RedfishMockupHTTPD_v0.9.1"

        def do_GET(self):
                # for GETs always dump the request headers to the console
                # there is no request data, so no need to dump that
                print("   GET: Headers: {}".format(self.headers))
                rfile="index.json"
                rfileXml="index.xml"
                f=None

                #xpath = self.translate_path(self.path)

                if(self.path[0]=='/'):
                        rpath=self.path[1:]
                rpath = rpath.split('?',1)[0]
                rpath = rpath.split('#',1)[0]
                apath=os.path.abspath(rpath)
                fpath=os.path.join(apath,rfile)
                fpathxml=os.path.join(apath,rfileXml)
                #print("filepath:{}".format(fpath))

                if( os.path.isfile(fpath) is True):
                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        # special cases to test etag for testing
                        # if etag is returned then the patch to these resource should include this etag
                        if( self.path=="/redfish/v1/Systems/1" ):
                                self.send_header("Etag", "W/\"12345\"")
                        elif( self.path=="/redfish/v1/AccountService/Accounts/1" ):
                                self.send_header("Etag", "W/\"123456\"")
                        self.end_headers()
                        f=open(fpath,"r")
                        self.wfile.write(f.read().encode())
                        f.close()
                elif( os.path.isfile(fpathxml) is True):
                        self.send_response(200)
                        self.send_header("Content-type", "application/xml")
                        self.end_headers()
                        f=open(fpathxml,"r")
                        self.wfile.write(f.read().encode())
                        f.close()
                else:
                        self.send_response(404)
                        self.end_headers()
                        
        def do_PATCH(self):
                print("   PATCH: Headers: {}".format(self.headers))
                if( "content-length" in self.headers ):
                        len=int(self.headers["content-length"])
                        dataa=self.rfile.read(len)
                        print("   PATCH: Data: {}".format(dataa))
                self.send_response(204)
                self.end_headers()
                
        def do_POST(self):
                print("   POST: Headers: {}".format(self.headers))
                if( "content-length" in self.headers ):
                        len=int(self.headers["content-length"])
                        dataa=self.rfile.read(len)
                        print("   POST: Data: {}".format(dataa))
                self.send_response(204)
                self.end_headers()
                
        def do_DELETE(self):
                print("DELETE: Headers: {}".format(self.headers))
                if( "content-length" in self.headers ):
                        # Deletes don't have data, so this doesnt execute
                        len=int(self.headers["content-length"])
                        dataa=self.rfile.read(len)
                        print("DELETE: Data: {}".format(dataa))
                self.send_response(204)
                self.end_headers()
                
        # this is currently not used
        def translate_path(self, path):
                """
                Translate a /-separated PATH to the local filename syntax.
                Components that mean special things to the local file system
                (e.g. drive or directory names) are ignored.  (XXX They should
                probably be diagnosed.)
                """
                # abandon query parameters
                path = path.split('?',1)[0]
                path = path.split('#',1)[0]
                path = posixpath.normpath(urllib.unquote(path))
                words = path.split('/')
                words = filter(None, words)
                path = os.getcwd()
                for word in words:
                        drive, word = os.path.splitdrive(word)
                        head, word = os.path.split(word)
                        if word in (os.curdir, os.pardir): continue
                path = os.path.join(path, word)
                return path

def usage(program):
        print("usage: {}   [-h][-P][-H <hostIpAddr>:<port>]".format(program))
        print("      -h --help      # prints usage ")
        print("      -L --Load      # <not implemented yet>: load and Dump json read from mockup in pretty format with indent=4")
        print("      -H <IpAddr>   --Host=<IpAddr>    # hostIP, default: 127.0.0.1")
        print("      -P <port>     --Port=<port>      # port:  default is 8000")
        print("   by default, service runs on 127.0.0.1:8000, using raw JSON response from mockup")

def main(argv):
        hostname="127.0.0.1"
        port=8000
        load=False
        program=argv[0]
        print(program)
        
        try:
                opts, args = getopt.getopt(argv[1:],"hLH:P:",["help","Load","Host=","Port="])
        except getopt.GetoptError as err:
                #usage()
                print(err)
                usage()
                sys.exit(2)

        for opt, arg in opts:
                if opt in ("-h", "--help"):
                        usage(program)
                        sys.exit(0)
                elif opt in ("L", "--Load"):
                        load=True
                elif opt in ("-H", "--Host"):
                        hostname=arg
                elif opt in ("-P", "--Port"):
                        port=int(arg)
                else:
                        print('unhandled option')
                        sys.exit(2)

        print ('program: ', program)
        print ('Hostname:', hostname)
        print ('Port:', port)

        myServer=HTTPServer((hostname, port), RfMockupServer)
        print( 'Serving Redfish mockup on port:', port)
        try:
                myServer.serve_forever()
        except KeyboardInterupt:
                pass

        myServer.server_close()
        print("Shutting down http server")
        

# the below is only executed if the program is run as a script
if __name__ == "__main__":
        main(sys.argv)

'''
TODO:
1. add -L option to load json and dump output from python dictionary
2. add authentication support -- note that in redfish some api don't require auth
3. add https support


'''
