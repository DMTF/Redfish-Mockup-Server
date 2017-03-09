# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Mockup-Server/LICENSE.md

# redfishMockupServer.py
# v0.9.7
# tested and developed in Python 3.4


import urllib
# import cgi
import sys
import getopt
import time
import json
import ssl
import posixpath
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import base64


class RfMockupServer(BaseHTTPRequestHandler):
        """
        returns index.json file for Server in the specified URL
        """

        server_version = "RedfishMockupHTTPD_v0.9.7"
        ResponseCode = 0  # Initialization of the response codes . Local Variable
        UserFlag = False  # to check the authentication status of the user. Local Variable

        def do_GET(self):
                # for GETs always dump the request headers to the console
                # there is no request data, so no need to dump that

                Params.Lbl = "   " + sys._getframe().f_code.co_name[3:] + ": Headers: "    # ensures that all the methods are properly represented in the console/logfile
                print(Params.Lbl + "{}".format(self.headers))  # Output to Console
                sys.stdout.flush()
                self.authentication()   # Module to check the authentication of the user. If -N Option is given, the authentication process will be circumvented in the method
                if self.UserFlag is False:
                        self.UserError()        # Method if an unauthorized user is detected
                        self.end_headers()
                else:
                        self.command_delay(self.command)        # method command_delay used to determine the appropriate delay time
                        # Check the validity of the index.json file. If not valid, server will raise warning and create log
                        if os.path.isfile(Params.fpath) is True:
                                try:
                                        Params.I_File = json.load(open(Params.fpath))
                                        self.ResponseCode = 200
                                        self.send_response(self.ResponseCode)
                                        indexErr = False
                                except:
                                        self.ResponseCode = 412
                                        self.send_response(self.ResponseCode)
                                        err1 = " **ERROR**: Index.Json is not valid Json Data file\n"
                                        print(err1)
                                        indexErr = True         # Flag to check validity of index.json
                                        if Params.LogFlag is True:
                                                        with open(Params.Logfile, 'a') as Log:
                                                                Log.write('\n' + str(time.strftime("%c")) + err1)
                                # Send Headers to client. If no header is generated from the updated_header module, server will send an empty header to client
                                try:
                                        for key, value in self.updated_headers.items():  # Sends each header as a separate line item
                                                self.send_header(key, value)
                                except:
                                        self.send_header("", self.updated_headers)
                                self.end_headers()
                                # if Index.json file is valid, the server will proceed to send the msg body
                                if indexErr is False:
                                        if Params.JFlag is True:        # Checking the -J option and dump the data to strip copyright
                                                if Params.CopyFlag is True:
                                                        Params.I_File.pop('@Redfish.Copyright',0)       # Strips Copyright Data
                                                self.wfile.write(json.dumps(Params.I_File, sort_keys=False).encode())
                                        else:                           # if no -J option, The Json data will remain unchanged
                                                f = open(Params.fpath, "r")
                                                self.wfile.write(f.read().encode())
                                                f.close()
                        # If the URI has index.xml in it:
                        elif os.path.isfile(Params.fpathxml) is True:
                                self.ResponseCode = 200
                                self.send_response(self.ResponseCode)
                                # send header -- same as method for index.json
                                try:
                                        for key, value in self.updated_headers.items():
                                                self.send_header(key, value)
                                except:
                                        self.send_header("", self.updated_headers)
                                self.end_headers()
                                # send msg body as xml
                                f = open(Params.fpathxml, "r")
                                self.wfile.write(f.read().encode())
                                f.close()
                        else:
                                self.ResponseCode = 404
                                self.send_response(self.ResponseCode)
                                self.end_headers()

                # If -l option is chosen, all console output will be logged in LogFile
                if Params.LogFlag is True:
                        self.Log_Write_CMD()

        def do_HEAD(self):
                """This method will send only the Header data for HEAD method from updated_header module.
                The Header Data are captured from the three header sources. - Assumption is that there will be separate header blocks for GET and HEAD methods in the DFLT_Header
                and GET_Header Files, so the contents may be different between GET and HEAD methods. """  # Paul to confirm this assumption
                Params.Lbl = "   "+sys._getframe().f_code.co_name[3:]+": Headers: "
                print(Params.Lbl + "{}".format(self.headers))
                sys.stdout.flush()
                self.authentication()
                if self.UserFlag is False:
                        self.UserError()
                        self.end_headers()
                else:
                        self.command_delay(self.command)
                        self.ResponseCode = 204
                        self.send_response(self.ResponseCode)
                        # each header item is sent as a separate line
                        try:
                                for key, value in self.updated_headers.items():
                                        self.send_header(key, value)
                        except:
                                self.send_header("", self.updated_headers)
                        self.end_headers()

                if Params.LogFlag is True:
                        self.Log_Write_CMD()

        def do_PATCH(self):
                Params.Lbl = "   "+sys._getframe().f_code.co_name[3:]+": Headers: "
                print(Params.Lbl + "{}".format(self.headers))
                sys.stdout.flush()
                self.authentication()
                if self.UserFlag is False:
                        self.UserError()
                        self.end_headers()
                else:
                        if "content-length" in self.headers:
                                len1 = int(self.headers["content-length"])
                                dataa = self.rfile.read(len1)
                                print("   PATCH: Data: {}".format(dataa))
                        self.command_delay(self.command)
                        self.ResponseCode = 204
                        self.send_response(self.ResponseCode)
                        self.end_headers()
                if Params.LogFlag is True:
                        self.Log_Write_CMD()

        def do_POST(self):
                Params.Lbl = "   "+sys._getframe().f_code.co_name[3:]+": Headers: "
                print(Params.Lbl + "{}".format(self.headers))
                sys.stdout.flush()
                self.authentication()
                if self.UserFlag is False:
                        self.UserError()
                        self.end_headers()
                else:
                        if "content-length" in self.headers:
                                len1 = int(self.headers["content-length"])
                                dataa = self.rfile.read(len1)
                                print("   POST: Data: {}".format(dataa))

                        self.command_delay(self.command)
                        self.ResponseCode = 204
                        self.send_response(self.ResponseCode)
                        self.end_headers()
                if Params.LogFlag is True:
                        self.Log_Write_CMD()

        def do_DELETE(self):
                Params.Lbl = "   "+sys._getframe().f_code.co_name[3:]+": Headers: "
                print(Params.Lbl + "{}".format(self.headers))
                sys.stdout.flush()
                self.authentication()
                if self.UserFlag is False:
                        self.UserError()
                        self.end_headers()
                else:
                        if "content-length" in self.headers:
                                # Deletes don't have data, so this doesnt execute
                                len1 = int(self.headers["content-length"])
                                dataa = self.rfile.read(len1)
                                print("DELETE: Data: {}".format(dataa))
                        self.command_delay(self.command)
                        self.ResponseCode = 204
                        self.send_response(self.ResponseCode)
                        self.end_headers()
                if Params.LogFlag is True:
                        self.Log_Write_CMD()
        # This is currently not used

        def translate_path(self, path):
                """
                Translate a /-separated PATH to the local filename syntax.
                Components that mean special things to the local file system
                (e.g. drive or directory names) are ignored.  (XXX They should
                probably be diagnosed.)
                """
                # abandon query parameters
                path = path.split('?', 1)[0]
                path = path.split('#', 1)[0]
                path = posixpath.normpath(urllib.unquote(path))
                words = path.split('/')
                words = filter(None, words)
                path = os.getcwd()
                for word in words:
                        drive, word = os.path.splitdrive(word)
                        head, word = os.path.split(word)
                        if word in (os.curdir, os.pardir):
                            continue
                path = os.path.join(path, word)
                return path

        def authentication(self):
                '''This method will check if -N option is given in the command line. By default, it will authenticate the users unless -N is given
                If no "-N" the server will decode the user/password from the request and authenticate with the existing user/password list.'''
                self.UserFlag = False   # Dflt user unauthorised
                if Params.AuthFlag is True:     # if -N is not given, default AuthFlag will be True and the server will continue to authorization check
                        try:
                                key_file = json.load(open('Auth.json'))         # Loads the approved user and PW list from the top directory
                                # decode the header key
                                header_key = (str(base64.b64decode(str(self.headers['Authorization'])[6:])).replace('b','')).replace("'" , "").split(":")
                                # match header key with the user/password list
                                for k, v in key_file.items():
                                        if (k == header_key[0]) and  (v == header_key[1]):
                                                self.UserFlag = True
                                                User_OK = "User " + k + " authorized"
                                                print(User_OK)
                                                if Params.LogFlag is True:  # writes to the logfile
                                                        with open(Params.Logfile, 'a') as Log:
                                                                Log.write('\n' + str(time.strftime("%c")) + User_OK)
                                                break

                        except:
                                # if the User/Password file is corrupt or not available, return 401
                                AuthFileError = " ***ERROR** The Auth.json file is missing or corrupt"
                                print(AuthFileError)
                                if Params.LogFlag is True:
                                        with open(Params.Logfile, 'a') as Log:
                                                Log.write('\n' + str(time.strftime("%c")) + AuthFileError)
                else:
                        # if -N is given, server will continue without user authentication by enabling the UserFlag
                        self.UserFlag = True

        def UserError(self):
                """If the user is not authenticated, the server will return 401 (Unauthorized) """
                self.ResponseCode = 401
                self.send_response(self.ResponseCode)
                UserError = " *ERROR** User not Authenticated"
                print(UserError)
                if Params.LogFlag is True:      # Logging to Logfile
                        with open(Params.Logfile, 'a') as Log:
                                Log.write('\n' + str(time.strftime("%c")) + UserError)



        # To generate the paths:
        def file_path(self):
                Params.rfile = "index.json"
                Params.rfileXml = "index.xml"
                Params.Tfile = "TIME.json"
                if self.path[0] == '/':
                        Params.rpath = self.path[1:]
                        Params.rpath = Params.rpath.split('?', 1)[0]
                        Params.rpath = Params.rpath.split('#', 1)[0]
                        Params.apath = self.server.mockDir  # this is the real absolute path to the mockup directory
                        # form the path in the mockup of the file
                        # old only support mockup in CWD:  apath=os.path.abspath(rpath)
                        Params.fpath = os.path.join(Params.apath, Params.rpath, Params.rfile)
                        Params.fpathxml = os.path.join(Params.apath, Params.rpath, Params.rfileXml)
                        Params.tpath = os.path.join(Params.apath, Params.rpath, Params.Tfile)

        def command_delay(self, command):
                """command_delay Module determines the appropriate wait time based on the parameters.
                Arguments:
                if -t is provided - the arg will be be used as system wait time
                if -d is provided, The values is TIME.json will be used as wait time for individual methods (GET/PATCH?HEAD/DELETE/POST...)
                if TIME.json is not available or if it does not content wait time for any of the methods, then -d arg will be used as default time
                if -t or -d is not provided, the wait time will be system default (set as 0.0 seconds)
                if both -t & -d is given, it will be an error
                """

                self.file_path()
                delay_time = Params.responseTime
                if not Params.tflag:
                        if Params.dflttimeflag:
                                if os.path.isfile(Params.tpath):
                                        with open(Params.tpath, "r+") as jfile:
                                                try:
                                                        djson = json.load(jfile)
                                                        delay_time = float(djson.get(self.command + "time", Params.dflttime))  #Self.command returns
                                                        #the name of the request "GET/HEAD?DELETE/PATCH/POST..." and used to find the appropriate key in TIME.json
                                                except ValueError:
                                                        delay_time = Params.dflttime
                                else:
                                    delay_time = Params.dflttime
                time.sleep(delay_time)

        @property
        def updated_headers(self):
                """Updated Header Module generates the header data.
                Description:
                Header data will consits of data from three possible sources : Generated header (labeled below as system_header),
                DFLT_RSPONSE_HEADERS.json which will be in the top directory of the mockup and
                API_Response_HEADERS.json that will be in the target URI, All the keys will be merged in a list where a value for a key in the system
                header with priority sequence in case of conflict (High to low): URI level headers, Generated Headers, Top Level Headers
                """

                TOPHeaderfile = "DFLT_RESPONSE_HEADERS.json"   # Make sure there is no space in the Key Values else the headers will not be returned
                SUBHeaderfile = "GET_RESPONSE_HEADERS.json"
                TOP_Header_Path = os.path.join(self.server.mockDir, TOPHeaderfile)
                self.file_path()
                if os.path.isfile(Params.fpath) is True:
                        system_header = {"Content-Type": "Application/Json,charset=utf-8"}   # If any additional header items need to be incorporated in the code, this field can be used
                elif os.path.isfile(Params.fpathxml) is True:
                        system_header = {"Content-type": "application/xml,charset=utf-8"}   # If any additional header items need to be incorporated in the code, this field can be used
                else:
                        system_header = {"": ""}
                merged_header = {}
                SUB_Header_Path = os.path.join(self.server.mockDir, Params.rpath, SUBHeaderfile)
                TOP_Header = ""
                SUB_Header = ""
                try:
                        if os.path.isfile(TOP_Header_Path):
                                TOP_Header = json.load(open(TOP_Header_Path))
                except:
                        J_resp_1 = "Error in DFTL_RESPOSE_HEADERS.json"
                        print(J_resp_1)
                        if Params.LogFlag is True:
                                with open(Params.Logfile, 'a') as Log:
                                        Log.write("\n" + str(time.strftime("%c")) + J_resp_1+"\n")
                try:
                        if os.path.isfile(SUB_Header_Path):
                                SUB_Header = json.load(open(SUB_Header_Path))
                except:
                        J_resp_2 = "Error in GET_RESPONSE_HEADERS.json"
                        if Params.LogFlag is True:
                                with open(Params.Logfile, 'a') as Log:
                                        Log.write("\n" + str(time.strftime("%c")) + J_resp_2+"\n")
                try:
                        merged_header = {key: value for key, value in TOP_Header['METHODS'][self.command].items()}
                except:
                        merged_header = merged_header
                try:
                        for (key, value) in system_header.items():   # self.command returns the name of the request "GET/HEAD?DELETE/PATCH/POST..."
                                merged_header[key] = value
                except:
                        merged_header = merged_header

                try:
                        for (key, value) in SUB_Header['METHODS'][self.command].items():  # self.command returns the name of the request "GET/HEAD?DELETE/PATCH/POST..."
                                merged_header[key] = value
                except:
                        merged_header = merged_header

                # If any Element has a '0' value in the header, it will not be sent
                merged_header = {key: value for key, value in merged_header.items() if value != ''}
                # check if Etag option is requested
                if 'Etag' in merged_header:
                        if Params.testEtagFlag is True:
                                return merged_header
                        else:
                                merged_header.pop('Etag', 0)
                                return merged_header
                else:
                        return merged_header

        def Log_Write_CMD(self):
                """This module is to write the logs in logfile with -l enabled"""
                # recreate the auto generated prompt
                Response = "\n" + str(Params.hostname) + "-- [" + str(time.strftime("%c")) + '] "' + str(self.requestline) + '" ' + str(self.ResponseCode) + "-"
                # print the header values from client request
                HDR = dict(self.headers)
                with open(Params.Logfile, 'a') as Log:
                        Log.write(Response + "\n")
                        Log.write("\n" + str(time.strftime("%c")) + Params.Lbl + "\n")
                        for key, value in HDR.items():
                                Log.write(str(key) + ": " + str(value) + '\n')


class Params:
        # Initialize the variables
        fpath = tpath = rpath = apath = xpathxml = rfileXml = fpathxml = ''
        responseTime = dflttime = 0
        tflag = dflttimeflag = testEtagFlag = LogFlag = JFlag = CopyFlag = False
        Logfile = ("Logfile'-'"+str(time.strftime("%c"))+'.txt').replace("/", "-").replace(" ", "'-'").replace(":", "")
        LogList1 = []
        Lbl = I_File = ''
        hostname = "127.0.0.1"
        AuthFlag = True


def usage(program):
        print("usage: {}   [-h][-P][-S][-T][-J][-l][-H <hostIpAddr>:<port>]".format(program))
        print("      -h --help      # prints usage ")
        print("      -L --Load      # <not implemented yet>: load and Dump json read from mockup in pretty format with indent=4")
        print("      -S --HTTPS     # Enable HTTPS Support ( Need to have certificates installed) ")
        print("      -T --Etag      # etag testing--enable returning etag for certain APIs for testing.  See Readme")
        print("      -J --Json      # Loads Index.json and dumps it back ")
        print("      -C --Copy      # Strips Copyright information from the data . To be used with -J option only")
        print("      -l --Log       # Enable Logging events in Logfile.txt")
        print("      -N --NoAuth    # Disables the User Authentication Process. Default is Enabled")
        print("      -H <IpAddr>   --Host=<IpAddr>    # hostIP, default: 127.0.0.1")
        print("      -d <dftlTime> --dflttime=<executionTime> # time added to respond to any API from Time.json")   # Need to fix
        print("      -P <port>     --Port=<port>      # port:  default is 8000")
        print("      -D <dir>,     --Dir=<dir>        # the to the mockup directory. It may be relative to CWD")
        print("      -t <responseTime> --time=<executionTime> # time added to respond to any API")
        print("-" * 100)
        print("       Exit : ^C <Ctrl+C> ")
        sys.stdout.flush()


def Log_Write():
        '''If -l or --Log is selected, a logfile will be created and all the console output will be recorded'''
        if Params.LogFlag is True:
                with open(Params.Logfile, 'w') as Log:
                        for x in Params.LogList1:
                                Log.write(x + '\n')


def main(argv):
        # global responseTime#, tflag#, dflttime#, dflttimeflag  #, testEtagFlag
        # hostname = "127.0.0.1"
        port = 8000
        load = False
        program = argv[0]
        print(program)
        mockDirPath = os.getcwd()
        mockDir = os.path.realpath(mockDirPath)
        # testEtagFlag = False
        # responseTime = 0
        # tflag = False
        # dflttime = 0
        # dflttimeflag = False
        # tTime = 0
        DirFlag = 0
        HTTPSFlag = False
        # LogList1 = []

        try:
                opts, args = getopt.getopt(argv[1:], "hLTSJClNH:P:D:t:d:", ["help", "Load", "TestEtag", "HTTPS", "Json", "Copy", "Log", "NoAuth", "Host=", "Port=", "Dir=", "time=", "dflttime="])
        except getopt.GetoptError:
                print("Error parsing options")
                sys.stderr.flush()
                usage(program)
                sys.exit(2)

        for opt, arg in opts:
                if opt in ("-h", "--help"):
                        usage(program)
                        sys.exit(0)
                elif opt in ("L", "--Load"):
                        load = True
                elif opt in ("-H", "--Host"):
                        Params.hostname = arg
                elif opt in ("-P", "--Port"):
                        port = int(arg)
                elif opt in ("-D", "--Dir"):
                        DirFlag = True
                        mockDirPath = arg
                        mockDir = os.path.realpath(mockDirPath)  # creates real full path including path for the arg
                elif opt in ("-T", "--Etag"):
                        Params.testEtagFlag = True
                elif opt in ("-t", "--time"):
                        Params.tflag = True
                        Params.responseTime = float(arg)
                elif opt in ("-d", "--dflttime"):
                        Params.dflttimeflag = True
                        Params.dflttime = float(arg)
                elif opt in ("-S", "--HTTPS"):
                        HTTPSFlag = True
                elif opt in ("-l", "--Log"):
                        Params.LogFlag = True
                elif opt in ("-J", "--Json"):
                        Params.JFlag = True
                elif opt in ("-C", "--Copy"):
                        Params.CopyFlag = True
                elif opt in ("-N", "--NoAuth"):
                        Params.AuthFlag = False
                else:
                        UH = 'unhandled option'
                        print(UH)
                        Params.LogList1.append(str(time.strftime("%c")) + " " + UH)
                        sys.exit(2)

        # check that that -d and -t were not both specified
        if (Params.tflag is True) and (Params.dflttimeflag is True):
                tde = "ERROR: -t and -d dflttime not valid together here"
                print(tde)
                Params.LogList1.append(str(time.strftime("%c")) + " " + tde)
                Log_Write()
                sys.stderr.flush()
                sys.exit(1)

        Program = ('program: ' + str(program))
        print(Program)
        Params.LogList1.append(str(time.strftime("%c")) + " " + Program)
        # sys.stdout.flush()
        Host = ('Hostname:' + str(Params.hostname))
        print(Host)
        Params.LogList1.append(str(time.strftime("%c")) + " " + Host)
        # sys.stdout.flush()
        Port = ('Port:' + str(port))
        print(Port)
        Params.LogList1.append(str(time.strftime("%c")) + " " + Port)
        # sys.stdout.flush()

        if DirFlag is True:
                DF = ("dir path specified by user:{}".format(mockDirPath))
        else:
                DF = "dir path specified by user: None"
        print(DF)
        Params.LogList1.append(str(time.strftime("%c")) + " " + DF)

        # sys.stdout.flush()
        # time.sleep(2)
        Path = ("Serving Mockup in abs real directory path:{}".format(mockDir))
        print(Path)
        Params.LogList1.append(str(time.strftime("%c")) + " " + Path)
        # sys.stdout.flush()
        # check that we have a valid tall mockup--with /redfish in mockDir before proceeding
        slashRedFishDir = os.path.join(mockDir, "redfish")
        if os.path.isdir(slashRedFishDir) is not True:
                FLDRErr = "ERROR: Invalid Mockup Directory--no /redfish directory at top. Aborting"
                print(FLDRErr)
                Params.LogList1.append(str(time.strftime("%c")) + " " + FLDRErr)
                Log_Write()
                sys.stderr.flush()
                sys.exit(1)

        #       Adding https support -- Yet to be implemented

        myServer = HTTPServer((Params.hostname, port), RfMockupServer)
        # save the test flag, and real path to the mockup dir for the handler to use
        myServer.mockDir = mockDir
        myServer.testEtagFlag = Params.testEtagFlag
        myServer.responseTime = Params.responseTime

        # SSL wrapping for https support
        if HTTPSFlag is True:
                try:
                        P_Key = 'C:/Users/Nasimul_Hassan/Documents/Python_Scripts/key.pem'
                        CERT = 'C:/Users/Nasimul_Hassan/Documents/Python_Scripts/cert.pem'
                        myServer.socket = ssl.wrap_socket(myServer.socket, keyfile=P_Key, certfile=CERT, server_side=True)
                except:
                        CERTErr = "Certificate are not found. Exiting"
                        print(CERTErr)
                        Params.LogList1.append(str(time.strftime("%c")) + " " + CERTErr)
                        sys.exit(1)

        # myServer.me="HELLO"
        # time.sleep(1)

        Port_add = ("Serving Redfish mockup on port: {}".format(port))
        print(Port_add)
        Params.LogList1.append(str(time.strftime("%c")) + " " + Port_add)
        # sys.stdout.flush()

        if Params.dflttimeflag is True:
                DTText = "System Respose default Time is {} seconds".format(str(Params.dflttime))
        else:
                DTText = "System response time: {} seconds".format(str(Params.responseTime))
        print(DTText)
        Params.LogList1.append(str(time.strftime("%c")) + " " + DTText)

        if (Params.CopyFlag is True) and (Params.JFlag is False):
                JCtext = ("***Warning***: -C <Copyright) option entered without -J. Copyright information will not be "
                          "removed from Data. \n To remove Copyright information put both -J and -C in command line")
                print(JCtext)
                Params.LogList1.append(str(time.strftime("%c")) + " " + JCtext)
        sys.stdout.flush()
        Log_Write()

        try:
                myServer.serve_forever()
        except KeyboardInterrupt:
                pass
        myServer.server_close()
        Close_Txt = "Shutting down http server"
        print(Close_Txt)
        if Params.LogFlag is True:
                with open(Params.Logfile, 'a') as Log:
                        Log.write(str(time.strftime("%c")) + " " + Close_Txt)

        sys.stdout.flush()


# the below is only executed if the program is run as a script
if __name__ == "__main__":
        main(sys.argv)


'''
TODO:
1. add -L option to load json and dump output from python dictionary - ???? -> Similar to Option -J
2. add authentication support -- note that in redfish some api don't require auth
3. add https support - Done


'''
