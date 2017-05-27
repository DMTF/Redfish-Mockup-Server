# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Mockup-Server/LICENSE.md

# redfishMockupServer.py
# v0.9.3
# tested and developed Python 3.4

import urllib
import cgi
import sys
import getopt
import time
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

class RfMockupServer(BaseHTTPRequestHandler):
        '''
        returns index.json file for Serverthe specified URL
        '''
        server_version = "RedfishMockupHTTPD_v0.9.3"

        # Headers only request
        def do_HEAD(self):
            print ("Sending Headers: ")
            
            rfile = "headers.json"
            if(self.path[0]=='/'):
                rpath=self.path[1:]
            rpath = rpath.split('?',1)[0]
            rpath = rpath.split('#',1)[0]

            apath=self.server.mockDir
            responseTime = self.getResponseTime('HEAD',apath,rpath)
            try:
                time.sleep(float(responseTime))
            except ValueError as e:
                print ("Time is not a float value. Sleeping with default response time")
                time.sleep(float(self.server.responseTime))
            fpath=os.path.join(apath,rpath, rfile)
            sys.stdout.flush()

            if( os.path.isfile(fpath) is True):
                self.send_response(200)
                with open(fpath) as headers_data:
                    d = json.load(headers_data)
                if isinstance(d["GET"],dict):
                    for k,v in d["GET"].items():
                        self.send_header(k,v)
            else:
                self.send_response(404)
                self.end_headers()
            self.end_headers()

        def do_GET(self):
            # for GETs always dump the request headers to the console
            # there is no request data, so no need to dump that
            print("   GET: Headers: {}".format(self.headers))
            sys.stdout.flush()

            rfile="index.json"
            rfileXml="index.xml"
            f=None
            rhfile="headers.json"
            #xpath = self.translate_path(self.path)

            if(self.path[0]=='/'):
                rpath=self.path[1:]
            rpath = rpath.split('?',1)[0]
            rpath = rpath.split('#',1)[0]
            
            # get the testEtagFlag and mockup directory path parameters passed in from the http server
            apath=self.server.mockDir    # this is the real absolute path to the mockup directory
            testEtagFlag=self.server.testEtagFlag
            responseTime = self.getResponseTime('GET',apath,rpath)
            try:
                time.sleep(float(responseTime))
            except ValueError as e:
                print ("Time is not a float value. Sleeping with default response time.")
                time.sleep(float(self.server.responseTime))

            #print("-------apath; {}".format(apath))
            #print("-------test: {}".format(testEtagFlag))

            # form the path in the mockup of the file
            #      old only support mockup in CWD:  apath=os.path.abspath(rpath)
            fpath=os.path.join(apath,rpath, rfile)
            fhpath=os.path.join(apath,rpath, rhfile)
            fpathxml=os.path.join(apath,rpath, rfileXml)
            #print("-------filepath:{}".format(fpath))
            sys.stdout.flush()

            if( os.path.isfile(fpath) is True):
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                # special cases to test etag for testing
                #if etag is returned then the patch to these resources should include this etag
                if( testEtagFlag is True ):
                        if( self.path=="/redfish/v1/Systems/1" ):
                                self.send_header("Etag", "W/\"12345\"")
                        elif( self.path=="/redfish/v1/AccountService/Accounts/1" ):
                                self.send_header("Etag", "\"123456\"")
                
                if( os.path.isfile(fhpath) is True):
                    with open(fhpath) as headers_data:
                        d = json.load(headers_data)
                    if isinstance(d["GET"],dict):
                        for k,v in d["GET"].items():
                            self.send_header(k,v)        
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
                responseTime=self.server.responseTime
                time.sleep(responseTime)

                self.send_response(204)
                self.end_headers()
                
        def do_POST(self):
                print("   POST: Headers: {}".format(self.headers))
                if( "content-length" in self.headers ):
                        len=int(self.headers["content-length"])
                        dataa=self.rfile.read(len)
                        print("   POST: Data: {}".format(dataa))
                responseTime=self.server.responseTime
                time.sleep(responseTime)
                self.send_response(204)
                self.end_headers()
                
        def do_DELETE(self):
                print("DELETE: Headers: {}".format(self.headers))
                if( "content-length" in self.headers ):
                        # Deletes don't have data, so this doesnt execute
                        len=int(self.headers["content-length"])
                        dataa=self.rfile.read(len)
                        print("DELETE: Data: {}".format(dataa))
                responseTime=self.server.responseTime
                time.sleep(responseTime)
                
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

        
        # Response time calculation Algorithm
        def getResponseTime(self,method,apath,rpath):
            rfile = "time.json"
            fpath=os.path.join(apath,rpath, rfile)
            if not any(x in method for x in ("GET", "HEAD","POST","PATCH","DELETE") ): 
                print ("Not a valid method")
                return (0)

            if( os.path.isfile(fpath) is True):
                with open(fpath) as time_data:
                    d=json.load(time_data)
                    time_str = method + "_Time"
                    if time_str in d:
                        try:
                            float(d[time_str])
                        except Exception as e:
                            print ("Time in the json file, not a float/int value. Reading the default time.")
                            return (self.server.responseTime)
                        return (float(d[time_str]))
            return (self.server.responseTime)

def usage(program):
        print("usage: {}   [-h][-P][-H <hostIpAddr>:<port>]".format(program))
        print("      -h --help      # prints usage ")
        print("      -L --Load      # <not implemented yet>: load and Dump json read from mockup in pretty format with indent=4")
        print("      -H <IpAddr>   --Host=<IpAddr>    # hostIP, default: 127.0.0.1")
        print("      -P <port>     --Port=<port>      # port:  default is 8000")
        print("      -D <dir>,     --Dir=<dir>        # the to the mockup directory. It may be relative to CWD")
        print("      -T --TestEtag  # etag testing--enable returning etag for certain APIs for testing.  See Readme")
        print("      -t <responseTime> --time=<executionTime> # time added to respond to any API")
        sys.stdout.flush()


def main(argv):
        hostname="127.0.0.1"
        port=8000
        load=False
        program=argv[0]
        print(program)
        mockDirPath=None
        mockDir=None
        testEtagFlag=False
        responseTime=0
        
        try:
                opts, args = getopt.getopt(argv[1:],"hLTH:P:D:t:",["help","Load", "TestEtag", "Host=", "Port=", "Dir=",
                                                                   "time="])
        except getopt.GetoptError:
                #usage()
                print("Error parsing options", file=sys.stderr)
                sys.stderr.flush()
                usage(program)
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
                elif opt in ("-D", "--Dir"):
                        mockDirPath=arg
                elif opt in ("-T", "--TestEtag"):
                        testEtagFlag=True
                elif opt in ("-t", "--time"):
                        responseTime=arg
                else:
                        print('unhandled option', file=sys.stderr)
                        sys.exit(2)

        print ('program: ', program)
        print ('Hostname:', hostname)
        print ('Port:', port)
        print ("dir path specified by user:{}".format(mockDirPath))
        print ("response time: {} seconds".format(responseTime))
        sys.stdout.flush()

        # check if mockup path was specified.  If not, use current working directory
        if mockDirPath is None:
                mockDirPath=os.getcwd()

        #create the full path to the top directory holding the Mockup  
        mockDir=os.path.realpath(mockDirPath) #creates real full path including path for CWD to the -D<mockDir> dir path
        
        print ("Serving Mockup in abs real directory path:{}".format(mockDir))

        # check that we have a valid tall mockup--with /redfish in mockDir before proceeding
        slashRedfishDir=os.path.join(mockDir, "redfish")
        if os.path.isdir(slashRedfishDir) is not True:
                print("ERROR: Invalid Mockup Directory--no /redfish directory at top. Aborting", file=sys.stderr)
                sys.stderr.flush()
                sys.exit(1)

        myServer=HTTPServer((hostname, port), RfMockupServer)

        # save the test flag, and real path to the mockup dir for the handler to use
        myServer.mockDir=mockDir
        myServer.testEtagFlag=testEtagFlag
        try:
           myServer.responseTime=float(responseTime)
        except ValueError as e:
            print ("Enter a integer or float value")
            sys.exit(2)
        #myServer.me="HELLO"
        
        print( "Serving Redfish mockup on port: {}".format(port))
        sys.stdout.flush()
        try:
                myServer.serve_forever()
        except KeyboardInterupt:
                pass

        myServer.server_close()
        print("Shutting down http server")
        sys.stdout.flush()
        

# the below is only executed if the program is run as a script
if __name__ == "__main__":
        main(sys.argv)

'''
TODO:
1. add -L option to load json and dump output from python dictionary
2. add authentication support -- note that in redfish some api don't require auth
3. add https support


'''
