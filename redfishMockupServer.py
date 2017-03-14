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

                Globals.Lbl = "   " + sys._getframe().f_code.co_name[3:] + ": Headers: "    # ensures that all the methods are properly represented in the console/logfile
                print(Globals.Lbl + "{}".format(self.headers))  # Output to Console
                sys.stdout.flush()
                self.Req_Hdr()
                if self.Req_Hdr_ErrFlag is True:
                        self.end_headers()
                else:
                        self.authentication()   # Module to check the authentication of the user. If -N Option is given, the authentication process will be circumvented in the method
                        if self.UserFlag is False:
                                self.UserError()        # Method if an unauthorized user is detected
                                self.end_headers()
                        else:
                                self.command_delay(self.command)        # method command_delay used to determine the appropriate delay time
                                # Check the validity of the index.json file. If not valid, server will raise warning and create log
                                if os.path.isfile(Globals.fpath) is True:
                                        try:
                                                Globals.I_File = json.load(open(Globals.fpath))
                                                self.ResponseCode = 200
                                                self.send_response(self.ResponseCode)
                                                indexErr = False
                                        except:
                                                self.ResponseCode = 412
                                                self.send_response(self.ResponseCode)
                                                err1 = " **ERROR**: Index.Json is not valid Json Data file\n"
                                                print(err1)
                                                indexErr = True         # Flag to check validity of index.json
                                                if Globals.LogFlag is True:
                                                                with open(Globals.Logfile, 'a') as Log:
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
                                                if Globals.JFlag is True:        # Checking the -J option and dump the data to strip copyright
                                                        if Globals.CopyFlag is True:
                                                                Globals.I_File.pop('@Redfish.Copyright', 0)       # Strips Copyright Data
                                                        self.wfile.write(json.dumps(Globals.I_File, sort_keys=False).encode())
                                                else:                           # if no -J option, The Json data will remain unchanged
                                                        f = open(Globals.fpath, "r")
                                                        self.wfile.write(f.read().encode())
                                                        f.close()
                                # If the URI has index.xml in it:
                                elif os.path.isfile(Globals.fpathxml) is True:
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
                                        f = open(Globals.fpathxml, "r")
                                        self.wfile.write(f.read().encode())
                                        f.close()
                                else:
                                        self.ResponseCode = 404
                                        self.send_response(self.ResponseCode)
                                        self.end_headers()
                print(Globals.apath)
                print(Globals.rpath)

                # If -l option is chosen, all console output will be logged in LogFile
                if Globals.LogFlag is True:
                        self.Log_Write_CMD()

        def do_HEAD(self):
                """This method will send only the Header data for HEAD method from updated_header module.
                The Header Data are captured from the three header sources. - Assumption is that there will be separate header blocks for GET and HEAD methods in the DFLT_Header
                and GET_Header Files, so the contents may be different between GET and HEAD methods. """  # Paul to confirm this assumption
                Globals.Lbl = "   " + sys._getframe().f_code.co_name[3:] + ": Headers: "
                print(Globals.Lbl + "{}".format(self.headers))
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

                if Globals.LogFlag is True:
                        self.Log_Write_CMD()

        def do_PATCH(self):
                Globals.Lbl = "   " + sys._getframe().f_code.co_name[3:] + ": Headers: "
                print(Globals.Lbl + "{}".format(self.headers))
                sys.stdout.flush()
                self.file_path()  # file_path method is called here only for PATCH requests in order to process ETag requests
                self.Req_Hdr()
                if self.Req_Hdr_ErrFlag is True:
                        self.end_headers()
                else:
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
                print(Globals.apath)
                print(Globals.rpath)
                if Globals.LogFlag is True:
                        self.Log_Write_CMD()

        def do_POST(self):
                Globals.Lbl = "   " + sys._getframe().f_code.co_name[3:] + ": Headers: "
                print(Globals.Lbl + "{}".format(self.headers))
                sys.stdout.flush()
                self.Req_Hdr()
                if self.Req_Hdr_ErrFlag is True:
                        self.end_headers()
                else:
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
                if Globals.LogFlag is True:
                        self.Log_Write_CMD()

        def do_DELETE(self):
                Globals.Lbl = "   " + sys._getframe().f_code.co_name[3:] + ": Headers: "
                print(Globals.Lbl + "{}".format(self.headers))
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
                if Globals.LogFlag is True:
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
                if Globals.AuthFlag is True:     # if -N is not given, default AuthFlag will be True and the server will continue to authorization check
                        """ Redfish Session Token based on .Redfish-Profile-Simulator\SimpleOcpServerV1Sim\redfishURI.py """
                        if self.headers['hdr_token_key'] is not None:
                                if self.headers['hdr_token_key'] == "123456SESSIONauthcode" :
                                        self.UserFlag = True
                                else:
                                        AuthFileError = " ***ERROR** The redfish Token is invalid"
                                        if Globals.LogFlag is True:
                                                with open(Globals.Logfile, 'a') as Log:
                                                        Log.write('\n' + str(time.strftime("%c")) + AuthFileError)

                        else:
                                try:
                                        key_file = json.load(open('users.json'))         # Loads the approved user and PW list from the top directory
                                        # decode the header key
                                        header_key = (str(base64.b64decode(str(self.headers['Authorization'])[6:])).replace('b','')).replace("'" , "").split(":")
                                        # match header key with the user/password list
                                        for k, v in key_file.items():
                                                if (k == header_key[0]) and  (v == header_key[1]):
                                                        self.UserFlag = True
                                                        User_OK = " User " + k + " authorized"
                                                        print(User_OK)
                                                        if Globals.LogFlag is True:  # writes to the logfile
                                                                with open(Globals.Logfile, 'a') as Log:
                                                                        Log.write('\n' + str(time.strftime("%c")) + User_OK)
                                                        break

                                except:
                                        # if the User/Password file is corrupt or not available, return 401
                                        AuthFileError = " ***ERROR** The users.json file is missing or corrupt"
                                        print(AuthFileError)
                                        if Globals.LogFlag is True:
                                                with open(Globals.Logfile, 'a') as Log:
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
                if Globals.LogFlag is True:      # Logging to Logfile
                        with open(Globals.Logfile, 'a') as Log:
                                Log.write('\n' + str(time.strftime("%c")) + UserError)



        # To generate the paths:
        def file_path(self):
                Globals.rfile = "index.json"
                Globals.rfileXml = "index.xml"
                Globals.Tfile = "TIME.json"
                if self.path[0] == '/':
                        Globals.rpath = self.path[1:]
                        Globals.rpath = Globals.rpath.split('?', 1)[0]
                        Globals.rpath = Globals.rpath.split('#', 1)[0]
                        Globals.apath = self.server.mockDir  # this is the real absolute path to the mockup directory
                        # form the path in the mockup of the file
                        # old only support mockup in CWD:  apath=os.path.abspath(rpath)
                        Globals.fpath = os.path.join(Globals.apath, Globals.rpath, Globals.rfile)
                        Globals.fpathxml = os.path.join(Globals.apath, Globals.rpath, Globals.rfileXml)
                        Globals.tpath = os.path.join(Globals.apath, Globals.rpath, Globals.Tfile)

        def command_delay(self, command):
                """command_delay Module determines the appropriate wait time based on the parameters.
                Arguments:
                if -t is provided - the arg will be be used as system wait time
                if -d is provided, The values is TIME.json will be used as wait time for individual methods (GET/PATCH?HEAD/DELETE/POST...)
                if TIME.json is not available or if it does not content wait time for any of the methods, then -d arg will be used as default time
                if -t or -d is not provided, the wait time will be system default (set as 0.0 seconds)
                if both -t & -d is given, it will be an error
                """

                if self.command != "PATCH":   # For PATCH, this is executed separately. It is done to process the Etag request
                        self.file_path()
                delay_time = Globals.responseTime
                if not Globals.tflag:
                        if Globals.dflttimeflag:
                                if os.path.isfile(Globals.tpath):
                                        with open(Globals.tpath, "r+") as jfile:
                                                try:
                                                        djson = json.load(jfile)
                                                        delay_time = float(djson.get(self.command + "time", Globals.dflttime))  #Self.command returns
                                                        #the name of the request "GET/HEAD?DELETE/PATCH/POST..." and used to find the appropriate key in TIME.json
                                                except ValueError:
                                                        delay_time = Globals.dflttime
                                else:
                                    delay_time = Globals.dflttime
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

                # TOPHeaderfile = "DFLT_RESPONSE_HEADERS.json"   # Make sure there is no space in the Key Values else the headers will not be returned
                # SUBHeaderfile = "GET_RESPONSE_HEADERS.json"
                TOP_Header_Path = os.path.join(Globals.apath, Globals.TOPHeaderfile)
                self.file_path()
                if os.path.isfile(Globals.fpath) is True:
                        system_header = {"Content-Type": "Application/Json,charset=utf-8"}   # If any additional header items need to be incorporated in the code, this field can be used
                elif os.path.isfile(Globals.fpathxml) is True:
                        system_header = {"Content-type": "application/xml,charset=utf-8"}   # If any additional header items need to be incorporated in the code, this field can be used
                else:
                        system_header = {"": ""}
                merged_header = {}

                SUB_Header_Path = os.path.join(Globals.apath, Globals.rpath, Globals.SUBHeaderfile)
                TOP_Header = ""
                SUB_Header = ""
                try:
                        if os.path.isfile(TOP_Header_Path):
                                TOP_Header = json.load(open(TOP_Header_Path))
                except:
                        J_resp_1 = "Error in DFTL_RESPOSE_HEADERS.json"
                        print(J_resp_1)
                        if Globals.LogFlag is True:
                                with open(Globals.Logfile, 'a') as Log:
                                        Log.write("\n" + str(time.strftime("%c")) + J_resp_1+"\n")
                try:
                        if os.path.isfile(SUB_Header_Path):
                                SUB_Header = json.load(open(SUB_Header_Path))
                except:
                        J_resp_2 = "Error in GET_RESPONSE_HEADERS.json"
                        if Globals.LogFlag is True:
                                with open(Globals.Logfile, 'a') as Log:
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

                # If there is a "Origin" in the Headers, Send the value back as Header Item # ( Ref. G5 Redfish Dev spec section 5.13.2(7))
                if dict(self.headers).get('Origin') is not None:
                        OriginHeader = dict([("Access-Control-Allow-Origin", dict(self.headers).get('Origin'))])
                        for (key, value) in OriginHeader.items():
                                merged_header[key] = value

                # check if ETag option is requested
                if 'ETag' in merged_header:
                        if Globals.testETagFlag is True:
                                return merged_header
                        else:
                                merged_header.pop('ETag', 0)
                                return merged_header

                else:
                        return merged_header

        def Log_Write_CMD(self):
                """This module is to write the logs in logfile with -l enabled"""
                # recreate the auto generated prompt
                Response = "\n" + str(Globals.hostname) + "-- [" + str(time.strftime("%c")) + '] "' + str(self.requestline) + '" ' + str(self.ResponseCode) + "-"
                # print the header values from client request
                HDR = dict(self.headers)
                with open(Globals.Logfile, 'a') as Log:
                        Log.write(Response + "\n")
                        Log.write("\n" + str(time.strftime("%c")) + Globals.Lbl + "\n")
                        for key, value in HDR.items():
                                Log.write(str(key) + ": " + str(value) + '\n')

        def Req_Hdr(self):
                """This method is to process the Request Headers (The headers sent to the Redfish service [on G5MC] from the client)

                """
                #self.originflag = False
                self.Req_Hdr_ErrFlag = False
                Err_REQ_HDR = ''
                # If 'Host' is not defined in the header, send 400 ( Ref. G5 Redfish Dev spec section 5.13.2(6))
                if dict(self.headers).get('Host') is None:
                        self.ResponseCode = 400
                        self.send_response(self.ResponseCode)
                        self.Req_Hdr_ErrFlag = True
                        Err_REQ_HDR = "Response: 400 - Bad Request.  'Host' is not defined"
                        print(Err_REQ_HDR)
                # If Odata-Version is defined in Header but value is <> 4.0, send response 412  ( Ref. G5 Redfish Dev spec section 5.13.2(3))
                elif ((dict(self.headers).get('OData-Version')) is not None) and ((dict(self.headers).get('OData-Version')) != '4.0'):
                        self.ResponseCode = 412
                        self.send_response(self.ResponseCode)
                        self.Req_Hdr_ErrFlag = True
                        Err_REQ_HDR = "Response: 412 - Precondition fail. Requested Odata-Version is not 4.0"
                        print(Err_REQ_HDR)

                elif self.command == 'GET':
                        # If there is no "Access" in Header, the server will work normally and send the data  ( Ref. G5 Redfish Dev spec section 5.13.2(1))
                        if ((dict(self.headers).get('Accept')) is None) or ((dict(self.headers).get('Accept')) == '*/*'):
                                pass
                        else:
                                # if the filepath is "/redfish/v1/$metadata HTTP/1.1" but the "Accept: application/json is given, or for other cases if the "Accept: application/xml is given, send 406 -
                                for k, v in self.headers.items():
                                        if ((k == "Accept") and (v != "application/xml") and "GET /redfish/v1/$metadata HTTP/1.1" in self.requestline) or \
                                                ((k == "Accept") and (v != "application/json") and "GET /redfish/v1/$metadata HTTP/1.1" not in self.requestline):
                                                self.ResponseCode = 406
                                                self.send_response(self.ResponseCode)
                                                self.Req_Hdr_ErrFlag = True
                                                Err_REQ_HDR = "Response: 406 - Not supported"
                                                print(Err_REQ_HDR)

                # For Post and Patch Request, 'Content-Type = 'Application/json' or 'Charset=utf8' must be in the header (# ( Ref. G5 Redfish Dev spec section 5.13.2(2))
                elif (self.command == 'PATCH') or (self.command == 'POST'):
                        if ((dict(self.headers).get('Content-Type')) == "application/json") or ((dict(self.headers).get('Content-Type')) == "Charset=utf8"):
                                pass
                        else:
                                self.ResponseCode = 415
                                self.send_response(self.ResponseCode)
                                self.Req_Hdr_ErrFlag = True
                                Err_REQ_HDR = "Response: 415 - Unsupported Media Type"
                                print(Err_REQ_HDR)

                # ETag request for PATCH Method ( Ref. G5 Redfish Dev spec section 5.13.2(8))
                if (self.command == 'PATCH') and ('redfish/v1/AccountService/Accounts' in self.requestline) and 'If-Match' in self.headers:
                        SUB_Header_Path = os.path.join(Globals.apath, Globals.rpath, Globals.SUBHeaderfile).replace('\\','/')

                        try:
                                if os.path.isfile(SUB_Header_Path):
                                        if (self.headers['If-Match'] == json.load(open(SUB_Header_Path))['METHODS']['PATCH']['ETag']) or (self.headers['If-Match'] == chr(42)) :
                                                pass
                                        else:
                                                self.ResponseCode = 412                        # If the header file is missing, send 404
                                                self.send_response(self.ResponseCode)
                                                self.Req_Hdr_ErrFlag = True
                                                Err_REQ_HDR = "Response: 412 - Precondition Failed. ETag is not matching"
                                                print(Err_REQ_HDR)
                        except:
                                self.ResponseCode = 412                        # If the header file is missing, send 404
                                self.send_response(self.ResponseCode)
                                self.Req_Hdr_ErrFlag = True
                                Err_REQ_HDR = "Response: 412 - Precondition Failed- Corrupt or missing Header file in URI:"+Globals.rpath
                                print(Err_REQ_HDR)


                # if Logfile is requested, write the logs
                if (Globals.LogFlag is True) and (self.Req_Hdr_ErrFlag is True):
                        with open(Globals.Logfile, 'a') as Log:
                                Log.write("\n" + str(time.strftime("%c")) + Err_REQ_HDR+"\n")


class Globals:
        # Initialize the variables
        fpath = tpath = rpath = apath = xpathxml = rfileXml = fpathxml = ''
        responseTime = dflttime = 0
        tflag = dflttimeflag = testETagFlag = LogFlag = JFlag = CopyFlag = False
        Logfile = ("Logfile'-'"+str(time.strftime("%c"))+'.txt').replace("/", "-").replace(" ", "'-'").replace(":", "")
        LogList1 = []
        Lbl = I_File = ''
        hostname = "127.0.0.1"
        AuthFlag = True
        TOPHeaderfile = "DFLT_RESPONSE_HEADERS.json"   # Make sure there is no space in the Key Values else the headers will not be returned
        SUBHeaderfile = "GET_RESPONSE_HEADERS.json"


def usage(program):
        print("usage: {}   [-h][-P][-S][-T][-J][-l][-H <hostIpAddr>:<port>]".format(program))
        print("      -h --help      # prints usage ")
        print("      -L --Load      # <not implemented yet>: load and Dump json read from mockup in pretty format with indent=4")
        print("      -S --HTTPS     # Enable HTTPS Support ( Need to have certificates installed) ")
        print("      -T --ETag      # ETag testing--enable returning ETag for certain APIs for testing.  See Readme")
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
        if Globals.LogFlag is True:
                with open(Globals.Logfile, 'w') as Log:
                        for x in Globals.LogList1:
                                Log.write(x + '\n')


def main(argv):
        port = 8000
        load = False
        program = argv[0]
        print(program)
        mockDirPath = os.getcwd()
        mockDir = os.path.realpath(mockDirPath)
        DirFlag = 0
        HTTPSFlag = False

        try:
                opts, args = getopt.getopt(argv[1:], "hLTSJClNH:P:D:t:d:", ["help", "Load", "TestETag", "HTTPS", "Json", "Copy", "Log", "NoAuth", "Host=", "Port=", "Dir=", "time=", "dflttime="])
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
                        Globals.hostname = arg
                elif opt in ("-P", "--Port"):
                        port = int(arg)
                elif opt in ("-D", "--Dir"):
                        DirFlag = True
                        mockDirPath = arg
                        mockDir = os.path.realpath(mockDirPath)  # creates real full path including path for the arg
                elif opt in ("-T", "--ETag"):
                        Globals.testETagFlag = True
                elif opt in ("-t", "--time"):
                        Globals.tflag = True
                        Globals.responseTime = float(arg)
                elif opt in ("-d", "--dflttime"):
                        Globals.dflttimeflag = True
                        Globals.dflttime = float(arg)
                elif opt in ("-S", "--HTTPS"):
                        HTTPSFlag = True
                elif opt in ("-l", "--Log"):
                        Globals.LogFlag = True
                elif opt in ("-J", "--Json"):
                        Globals.JFlag = True
                elif opt in ("-C", "--Copy"):
                        Globals.CopyFlag = True
                elif opt in ("-N", "--NoAuth"):
                        Globals.AuthFlag = False
                else:
                        UH = 'unhandled option'
                        print(UH)
                        Globals.LogList1.append(str(time.strftime("%c")) + " " + UH)
                        sys.exit(2)

        # check that that -d and -t were not both specified
        if (Globals.tflag is True) and (Globals.dflttimeflag is True):
                tde = "ERROR: -t and -d dflttime not valid together here"
                print(tde)
                Globals.LogList1.append(str(time.strftime("%c")) + " " + tde)  # Update list for log entry
                Log_Write()
                sys.stderr.flush()
                sys.exit(1)

        Program = ('program: ' + str(program))
        print(Program)
        Globals.LogList1.append(str(time.strftime("%c")) + " " + Program)  # Update list for log entry
        # sys.stdout.flush()
        Host = ('Hostname:' + str(Globals.hostname))
        print(Host)
        Globals.LogList1.append(str(time.strftime("%c")) + " " + Host)  # Update list for log entry
        # sys.stdout.flush()
        Port = ('Port:' + str(port))
        print(Port)
        Globals.LogList1.append(str(time.strftime("%c")) + " " + Port)  # Update list for log entry
        # sys.stdout.flush()

        if DirFlag is True:
                DF = ("dir path specified by user:{}".format(mockDirPath))
        else:
                DF = "dir path specified by user: None"
        print(DF)
        Globals.LogList1.append(str(time.strftime("%c")) + " " + DF)

        # sys.stdout.flush()
        # time.sleep(2)
        Path = ("Serving Mockup in abs real directory path:{}".format(mockDir))
        print(Path)
        Globals.LogList1.append(str(time.strftime("%c")) + " " + Path)   # Update list for log entry
        # sys.stdout.flush()
        # check that we have a valid tall mockup--with /redfish in mockDir before proceeding
        slashRedFishDir = os.path.join(mockDir, "redfish")
        if os.path.isdir(slashRedFishDir) is not True:
                FLDRErr = "ERROR: Invalid Mockup Directory--no /redfish directory at top. Aborting"
                print(FLDRErr)
                # Updating list for log entry
                Globals.LogList1.append(str(time.strftime("%c")) + " " + FLDRErr)   # Update list for log entry
                Log_Write()
                sys.stderr.flush()
                sys.exit(1)

        myServer = HTTPServer((Globals.hostname, port), RfMockupServer)
        # save the test flag, and real path to the mockup dir for the handler to use
        myServer.mockDir = mockDir
        myServer.testETagFlag = Globals.testETagFlag
        myServer.responseTime = Globals.responseTime

        # SSL wrapping for https support
        if HTTPSFlag is True:
                try:
                        P_Key = 'key.pem'   # keys are generated by OpenSSL
                        CERT = 'cert.pem'
                        myServer.socket = ssl.wrap_socket(myServer.socket, keyfile=P_Key, certfile=CERT, server_side=True)
                except:
                        CERTErr = "Certificates not found or invalid certificates. Exiting server"
                        print(CERTErr)
                        Globals.LogList1.append(str(time.strftime("%c")) + " " + CERTErr)  # Update list for log entry
                        sys.exit(1)

        # myServer.me="HELLO"
        # time.sleep(1)

        Port_add = ("Serving Redfish mockup on port: {}".format(port))
        print(Port_add)
        Globals.LogList1.append(str(time.strftime("%c")) + " " + Port_add)  # Update list for log entry
        # sys.stdout.flush()

        if Globals.dflttimeflag is True:
                DTText = "System Respose default Time is {} seconds".format(str(Globals.dflttime))
        else:
                DTText = "System response time: {} seconds".format(str(Globals.responseTime))
        print(DTText)
        Globals.LogList1.append(str(time.strftime("%c")) + " " + DTText)  # Update list for log entry

        if (Globals.CopyFlag is True) and (Globals.JFlag is False):
                JCtext = ("***Warning***: -C <Copyright) option entered without -J. Copyright information will not be "
                          "removed from Data. \n To remove Copyright information put both -J and -C in command line")
                print(JCtext)
                Globals.LogList1.append(str(time.strftime("%c")) + " " + JCtext)  # Update list for log entry
        sys.stdout.flush()
        Log_Write()

        try:
                myServer.serve_forever()
        except KeyboardInterrupt:
                pass
        myServer.server_close()
        Close_Txt = "Shutting down http server"
        print(Close_Txt)
        if Globals.LogFlag is True:
                with open(Globals.Logfile, 'a') as Log:
                        Log.write(str(time.strftime("%c")) + " " + Close_Txt)

        sys.stdout.flush()


# the below is only executed if the program is run as a script
if __name__ == "__main__":
        main(sys.argv)


'''
TODO:
1. add -L option to load json and dump output from python dictionary - ???? -> Similar to Option -J
2. add Redfish authentication support -- note that in redfish some api don't require auth -



'''
