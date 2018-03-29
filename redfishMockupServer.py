# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Mockup-Server/LICENSE.md

# redfishMockupServer.py
# tested and developed Python 3.4

import urllib
import sys
import getopt
import time
import collections
import json
import requests
import posixpath

import os
import ssl
from http.server import BaseHTTPRequestHandler, HTTPServer

patchedLinks = dict()

tool_version = "1.0.0"

def get_cached_link(path):
    jsonData = None
    if path not in patchedLinks:
        if os.path.isfile(path):
            with open(path) as f:
                jsonData = json.load(f)
                f.close()
        else:
            return False, jsonData
    else:
        jsonData = patchedLinks[path]
    return jsonData is not None and jsonData != '404', jsonData


def dict_merge(dct, merge_dct):
        """
        https://gist.github.com/angstwad/bf22d1822c38a92ec0a9 modified
        Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
        updating only top-level keys, dict_merge recurses down into dicts nested
        to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
        ``dct``.
        :param dct: dict onto which the merge is executed
        :param merge_dct: dct merged into dct
        :return: None
        """
        for k in merge_dct:
            if (k in dct and isinstance(dct[k], dict)
                    and isinstance(merge_dct[k], collections.Mapping)):
                dict_merge(dct[k], merge_dct[k])
            else:
                dct[k] = merge_dct[k]


def clean_path(path):
    if(path[0] == '/'):
        path = path[1:]
    path = path.split('?', 1)[0]
    path = path.split('#', 1)[0]
    return path


class RfMockupServer(BaseHTTPRequestHandler):
        '''
        returns index.json file for Serverthe specified URL
        '''
        server_version = "RedfishMockupHTTPD_v" + tool_version

        # Headers only request
        def do_HEAD(self):
            print("Headers: ")
            sys.stdout.flush()

            rfile = "headers.json"
            rpath = clean_path(self.path)
            if self.server.shortForm:
                rpath = rpath.replace('redfish/v1/', '')
                rpath = rpath.replace('redfish/v1', '')
            apath = self.server.mockDir
            fpath = os.path.join(apath, rpath, rfile)

            if self.server.timefromJson:
                responseTime = self.getResponseTime('HEAD', apath, rpath)
                try:
                    time.sleep(float(responseTime))
                except ValueError as e:
                    print("Time is not a float value. Sleeping with default response time")
                    time.sleep(float(self.server.responseTime))

            sys.stdout.flush()
            print(self.server.headers)

            if self.server.headers and (os.path.isfile(fpath) is True):
                self.send_response(200)
                with open(fpath) as headers_data:
                    d = json.load(headers_data)
                if isinstance(d["GET"], dict):
                    for k, v in d["GET"].items():
                        self.send_header(k, v)
                self.end_headers()
            elif (self.server.headers is False) or (os.path.isfile(fpath) is False):
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("OData-Version", "4.0")
                self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()

        def do_GET(self):
            # for GETs always dump the request headers to the console
            # there is no request data, so no need to dump that
            print("   GET: Headers: {}".format(self.headers))
            sys.stdout.flush()
            dont_send = ["Connection", "Keep-Alive", "Content-Length"]
            rfile = "index.json"
            rfileXml = "index.xml"
            rhfile = "headers.json"

            rpath = clean_path(self.path)
            if self.server.shortForm:
                # print(rpath)
                rpath = rpath.replace('redfish/v1/', '')
                rpath = rpath.replace('redfish/v1', '')
                # print(rpath)
            apath = self.server.mockDir    # this is the real absolute path to the mockup directory
            # form the path in the mockup of the file
            #      old only support mockup in CWD:  apath=os.path.abspath(rpath)
            fpath = os.path.join(apath, rpath, rfile)
            fhpath = os.path.join(apath, rpath, rhfile)
            fpathxml = os.path.join(apath, rpath, rfileXml)
            fpathdirect = os.path.join(apath, rpath)
            print(fpath)

            # get the testEtagFlag and mockup directory path parameters passed in from the http server
            testEtagFlag = self.server.testEtagFlag

            print(self.server.timefromJson)
            if self.server.timefromJson:
                responseTime = self.getResponseTime('GET', apath, rpath)
                try:
                    time.sleep(float(responseTime))
                except ValueError as e:
                    print("Time is not a float value. Sleeping with default response time.")
                    time.sleep(float(self.server.responseTime))

            sys.stdout.flush()
 
            if(self.path == '/' and self.server.shortForm):
                self.send_response(404)
                self.end_headers()

            elif(self.path in ['/redfish', '/redfish/'] and self.server.shortForm):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({'v1':'/redfish/v1'}, indent=4).encode())

            # if this location exists in memory or as file
            elif(os.path.isfile(fpath) or fpath in patchedLinks):
                if patchedLinks.get(fpath) != '404':
                    self.send_response(200)
                else:
                    self.send_response(404)
                # special cases to test etag for testing
                # if etag is returned then the patch to these resources should include this etag
                if testEtagFlag is True:
                        if(self.path == "/redfish/v1/Systems/1"):
                                self.send_header("Etag", "W/\"12345\"")
                        elif(self.path == "/redfish/v1/AccountService/Accounts/1"):
                                self.send_header("Etag", "\"123456\"")

                if(os.path.isfile(fhpath) is True):
                    with open(fhpath) as headers_data:
                        d = json.load(headers_data)
                    if isinstance(d["GET"], dict):
                        for k, v in d["GET"].items():
                            if k not in dont_send:
                                self.send_header(str(k), str(v))
                elif (os.path.isfile(fhpath) is False):
                    self.send_header("Content-Type", "application/json")
                    self.send_header("OData-Version", "4.0")
                self.end_headers()

                if fpath not in patchedLinks:
                    f = open(fpath, "r")
                    self.wfile.write(f.read().encode())
                    f.close()
                else:
                    if patchedLinks[fpath] not in [None, '404']:
                        self.wfile.write(json.dumps(patchedLinks[fpath], indent=4).encode())

            elif(os.path.isfile(fpathxml) is True or os.path.isfile(fpathdirect) is True):
                if os.path.isfile(fpathxml):
                    file_extension = 'xml'
                    f = open(fpathxml, "r")
                elif os.path.isfile(fpathdirect):
                    filename, file_extension = os.path.splitext(fpathdirect)
                    f = open(fpathdirect, "r")
                self.send_response(200)
                self.send_header("Content-Type", "application/" + file_extension + ";odata.metadata=minimal;charset=utf-8")
                self.end_headers()
                self.wfile.write(f.read().encode())
                f.close()
            else:
                self.send_response(404)
                self.end_headers()

        def do_PATCH(self):
                print("   PATCH: Headers: {}".format(self.headers))
                responseTime = self.server.responseTime
                time.sleep(responseTime)

                if("content-length" in self.headers):
                    lenth = int(self.headers["content-length"])
                    dataa = json.loads(self.rfile.read(lenth).decode("utf-8"))
                    print("   PATCH: Data: {}".format(dataa))

                    rpath = clean_path(self.path)
                    if self.server.shortForm:
                        rpath = rpath.replace('redfish/v1/', '')
                        rpath = rpath.replace('redfish/v1', '')
                    apath = self.server.mockDir    # this is the real absolute path to the mockup directory
                    fpath = os.path.join(apath, rpath, 'index.json')

                    # check if resource exists, otherwise 404
                    #   if it's a file, open it, if its in memory, grab it
                    success, jsonData = get_cached_link(fpath)
                    if success:
                        # If this is a collection, throw a 405
                        if jsonData.get('Members') is not None:
                            self.send_response(405)
                        else:
                            # After getting resource, merge the data.
                            print(self.headers.get('content-type'))
                            print(dataa)
                            print(jsonData)
                            dict_merge(jsonData, dataa)
                            print(jsonData)
                            # put into patchedLinks
                            patchedLinks[fpath] = jsonData
                            self.send_response(204)
                    else:
                        self.send_response(404)

                self.end_headers()

        def do_PUT(self):
                print("   PUT: Headers: {}".format(self.headers))
                responseTime = self.server.responseTime
                time.sleep(responseTime)

                if("content-length" in self.headers):
                    len = int(self.headers["content-length"])
                    dataa = json.loads(self.rfile.read(len).decode("utf-8"))
                    print("   PUT: Data: {}".format(dataa))

                # we don't support this service
                self.send_response(405)

                self.end_headers()

        def do_POST(self):
                print("   POST: Headers: {}".format(self.headers))
                if("content-length" in self.headers):
                        lenth = int(self.headers["content-length"])
                        dataa = json.loads(self.rfile.read(lenth).decode("utf-8"))
                        print("   POST: Data: {}".format(dataa))
                responseTime = self.server.responseTime
                time.sleep(responseTime)

                rpath = clean_path(self.path)
                xpath = rpath
                if self.server.shortForm:
                    rpath = rpath.replace('redfish/v1/', '')
                    rpath = rpath.replace('redfish/v1', '')
                apath = self.server.mockDir    # this is the real absolute path to the mockup directory
                fpath = os.path.join(apath, rpath, 'index.json')
                parentpath = os.path.join(apath, rpath.rsplit('/', 1)[0], 'index.json')

                # don't bother if this item exists
                #   otherwise, check if its an action or a file
                if os.path.isfile(fpath) or patchedLinks.get(fpath) is not None:
                    success, jsonData = get_cached_link(fpath)
                    if success:
                        if jsonData.get('Members') is None:
                            self.send_response(405)
                        else:
                            print(dataa)
                            print(type(dataa)) 

                            members = jsonData.get('Members')
                            newpath = '/{}/{}'.format(xpath, len(members) + 1)
                            members.append({'@odata.id': newpath})

                            jsonData['Members'] = members
                            jsonData['Members@odata.count'] = len(members)

                            newfpath = os.path.join(newpath, 'index.json')
                            newfpath = apath + newfpath

                            print(newfpath)

                            if self.server.shortForm:
                                newfpath = newfpath.replace('redfish/v1/', '')

                            print(newfpath)

                            patchedLinks[newfpath] = dataa
                            patchedLinks[fpath] = jsonData
                            self.send_response(204)
                    else:
                        self.send_response(404)

                else:
                    if 'EventService/Actions/EventService.SubmitTestEvent' in rpath:
                        eventpath = os.path.join(apath, 'redfish/v1/EventService/Subscriptions', 'index.json')
                        if self.server.shortForm:
                            eventpath = eventpath.replace('redfish/v1/', '')
                        success, jsonData = get_cached_link(eventpath)
                        print(eventpath)
                        if not success:
                            self.send_response(404)
                        else:
                            print(jsonData.get('Members'))
                            for member in jsonData.get('Members', []):
                                entry = member['@odata.id']
                                if self.server.shortForm:
                                    entry = entry.replace('redfish/v1/', '')
                                entrypath = os.path.join(apath + entry, 'index.json')
                                success, jsonData = get_cached_link(entrypath)
                                print(apath)
                                print(entrypath)
                                if not success:
                                    print('No such resource')
                                else:
                                    destination = jsonData.get('Destination', 'http://0.0.0.0')
                                    print('target', destination)
                                    print(dataa.get('EventType'), jsonData.get('EventTypes'))
                                    if dataa.get('EventType', 'None') in jsonData.get('EventTypes', [])\
                                            or jsonData.get('EventTypes') is None:
                                        try:
                                            r = requests.post(destination, timeout=20, data=dataa)
                                            print('post complete', r.status_code)
                                        except Exception as e:
                                            print('post error', str(e))
                                    else:
                                        print('event not in eventtypes')
                                sys.stdout.flush()
                            self.send_response(204)
                    else:
                        self.send_response(405)

                self.end_headers()

        def do_DELETE(self):
                """
                Delete a resource
                """
                print("DELETE: Headers: {}".format(self.headers))
                if("content-length" in self.headers):
                        len = int(self.headers["content-length"])
                        #dataa = json.loads(self.rfile.read(len).decode("utf-8"))
                        dataa = {}
                        print("   POST: Data: {}".format(dataa))

                responseTime = self.server.responseTime
                time.sleep(responseTime)

                rpath = clean_path(self.path)
                xpath = '/' + rpath
                if self.server.shortForm:
                    rpath = rpath.replace('redfish/v1/', '')
                    rpath = rpath.replace('redfish/v1', '')
                apath = self.server.mockDir    # this is the real absolute path to the mockup directory
                fpath = os.path.join(apath, rpath, 'index.json')
                parentpath = os.path.join(apath, rpath.rsplit('/', 1)[0], 'index.json')

                success, jsonData = get_cached_link(fpath)
                if success:
                    success, parentData = get_cached_link(parentpath)
                    if success and parentData.get('Members') is not None:
                        patchedLinks[fpath] = '404'
                        parentData['Members'] = [x for x in parentData['Members'] if not x['@odata.id'] == xpath]
                        patchedLinks[parentpath] = parentData
                        self.send_response(204)
                    else:
                        self.send_response(405)
                else:
                    self.send_response(404)

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
        print("      -D <dir>,     --Dir=<dir>        # Path to the mockup directory. It may be relative to CWD")
        print("      -X,           --headers          # Option to load headers or not from json files")
        print("      -t <delay>    --time=<delayTime> # Delay Time in seconds added to any request. Must be float or int.")
        print("      -E            --TestEtag         # etag testing--enable returning etag for certain APIs for testing.  See Readme")
        print("      -T                               # Option to delay response or not.")
        print("      -s            --ssl              # Places server in https, requires a certificate and key")
        print("      --cert <cert>                    # Specify a certificate for ssl server function")
        print("      --key <key>                      # Specify a key for ssl")
        print("      -S            --shortForm        # Apply shortform to mockup (allowing to omit /redfish/v1)")
        sys.stdout.flush()


def main(argv):
        hostname="127.0.0.1"
        port=8000
        load=False
        program=argv[0]
        print(program)
        mockDirPath=None
        sslMode=False
        sslCert=None
        sslKey=None
        mockDir=None
        testEtagFlag=False
        responseTime=0
        timefromJson = False
        headers = False
        shortForm=False
        print("Redfish Mockup Server, version {}".format(tool_version))
        try:
                opts, args = getopt.getopt(argv[1:],"hLTSsEH:P:D:t:X",["help","Load", "shortForm", "ssl","TestEtag","headers", "Host=", "Port=", "Dir=",
                                                                   "time=", "cert=", "key="])
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
                elif opt in ("-X","--headers"):
                        headers=True
                elif opt in ("-P", "--Port"):
                        port=int(arg)
                elif opt in ("-D", "--Dir"):
                        mockDirPath=arg
                elif opt in ("-E", "--TestEtag"):
                        testEtagFlag=True
                elif opt in ("-t", "--time"):
                        responseTime=arg
                elif opt in ("-T"):
                        timefromJson=True
                elif opt in ("-s", "--ssl"):
                        sslMode=True
                elif opt in ("--cert",):
                        sslCert=arg
                elif opt in ("--key",):
                        sslKey=arg
                elif opt in ("-S", "--shortForm"):
                        shortForm=True
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
        if not shortForm:
            slashRedfishDir=os.path.join(mockDir, "redfish")
            if os.path.isdir(slashRedfishDir) is not True:
                    print("ERROR: Invalid Mockup Directory--no /redfish directory at top. Aborting", file=sys.stderr)
                    sys.stderr.flush()
                    sys.exit(1)

        if shortForm:
            if os.path.isdir(mockDir) is not True or os.path.isfile(os.path.join(mockDir, "index.json")) is not True:
                    print("ERROR: Invalid Mockup Directory--dir or index.json does not exist", file=sys.stderr)
                    sys.stderr.flush()
                    sys.exit(1)

        myServer=HTTPServer((hostname, port), RfMockupServer)

        if sslMode:
            print("Using SSL with certfile: {}".format(sslCert))
            myServer.socket = ssl.wrap_socket(myServer.socket, certfile=sslCert, keyfile=sslKey, server_side=True)

        # save the test flag, and real path to the mockup dir for the handler to use
        myServer.mockDir=mockDir
        myServer.testEtagFlag=testEtagFlag
        myServer.headers = headers
        myServer.timefromJson = timefromJson
        myServer.shortForm = shortForm
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
        except KeyboardInterrupt:
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
