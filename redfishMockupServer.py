# Copyright Notice:
# Copyright 2016-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Mockup-Server/blob/master/LICENSE.md

# redfishMockupServer.py
# tested and developed Python 3.4

import sys
import getopt
import time
import collections
import json
import threading
import datetime

import grequests

import os
import ssl
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, urlunparse, parse_qs
from rfSsdpServer import RfSDDPServer

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
logger.addHandler(ch)

tool_version = "1.0.7"

dont_send = ["connection", "keep-alive", "content-length", "transfer-encoding"]


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
            if (k in dct and isinstance(dct[k], dict) and isinstance(merge_dct[k], collections.Mapping)):
                dict_merge(dct[k], merge_dct[k])
            else:
                dct[k] = merge_dct[k]


def clean_path(path, isShort):
    """clean_path

    :param path:
    :param isShort:
    """
    path = path.strip('/')
    path = path.split('?', 1)[0]
    path = path.split('#', 1)[0]
    if isShort:
        path = path.replace('redfish/v1', '').strip('/')
    return path


class RfMockupServer(BaseHTTPRequestHandler):
        '''
        returns index.json file for Serverthe specified URL
        '''
        patchedLinks = dict()

        def construct_path(self, path, filename):
            """construct_path

            :param path:
            :param filename:
            """
            apath = self.server.mockDir
            rpath = clean_path(path, self.server.shortForm)
            return os.path.join(apath, rpath, filename) if filename not in ['', None] else os.path.join(apath, rpath)

        def get_cached_link(self, path):
            """get_cached_link

            :param path:
            """
            if path not in self.patchedLinks:
                if os.path.isfile(path):
                    with open(path) as f:
                        jsonData = json.load(f)
                        f.close()
                else:
                    jsonData = None
            else:
                jsonData = self.patchedLinks[path]
            return jsonData is not None and jsonData != '404', jsonData

        def try_to_sleep(self, method, path):
            """try_to_sleep

            :param method:
            :param path:
            """
            if self.server.timefromJson:
                responseTime = self.getResponseTime(method, path)
                try:
                    time.sleep(float(responseTime))
                except ValueError as e:
                    logger.info("Time is not a float value. Sleeping with default response time")
                    time.sleep(float(self.server.responseTime))
            else:
                time.sleep(float(self.server.responseTime))

        def send_header_file(self, fpath):
            """send_header_file

            :param fpath:
            """
            with open(fpath) as headers_data:
                d = json.load(headers_data)
            if isinstance(d.get("GET"), dict):
                for k, v in d["GET"].items():
                    if k.lower() not in dont_send:
                        self.send_header(k, v)

        def add_new_member(self, payload, data_received):
            members = payload.get('Members')
            n = 1
            newpath_id = data_received.get('Id', 'Member')
            newpath = os.path.join(self.path, newpath_id)
            while newpath in [m.get('@odata.id') for m in members]:
                n = n + 1
                newpath_id = data_received.get('Id', 'Member') + str(n)
                newpath = os.path.join(self.path, newpath_id)
            members.append({'@odata.id': newpath})

            payload['Members'] = members
            payload['Members@odata.count'] = len(members)
            return newpath

        def handle_eventing(self, data_received):
            sub_path = self.construct_path('/redfish/v1/EventService/Subscriptions', 'index.json')
            success, sub_payload = self.get_cached_link(sub_path)
            logger.info(sub_path)
            if not success:
                # Eventing not supported
                return (404)
            else:
                # Check if all of the parameters are given
                if ( ('EventType' not in data_received) or ('EventId' not in data_received) or
                     ('EventTimestamp' not in data_received) or ('Severity' not in data_received) or
                     ('Message' not in data_received) or ('MessageId' not in data_received) or
                     ('MessageArgs' not in data_received) or ('OriginOfCondition' not in data_received) ):
                    return (400)
                else:
                    # Need to reformat to make Origin Of Condition a proper link
                    origin_of_cond = data_received['OriginOfCondition']
                    data_received['OriginOfCondition'] = {}
                    data_received['OriginOfCondition']['@odata.id'] = origin_of_cond
                    event_payload = {}
                    event_payload['@odata.type'] = '#Event.v1_2_1.Event'
                    event_payload['Name'] = 'Test Event'
                    event_payload['Id'] = str(self.event_id)
                    event_payload['Events'] = []
                    event_payload['Events'].append(data_received)

                    # Go through each subscriber
                    events = []
                    for member in sub_payload.get('Members', []):
                        entry = member['@odata.id']
                        entrypath = self.construct_path(entry, 'index.json')
                        success, subscription = self.get_cached_link(entrypath)
                        if not success:
                            logger.info('No such resource')
                        else:
                            # Sanity check the subscription for required properties
                            if ('Destination' in subscription) and ('EventTypes' in subscription):
                                logger.info(('Target', subscription['Destination']))
                                logger.info((data_received['EventType'], subscription['EventTypes']))

                                # If the EventType in the request is one of interest to the subscriber, build an event payload
                                if data_received['EventType'] in subscription['EventTypes']:
                                    http_headers = {}
                                    http_headers['Content-Type'] = 'application/json'

                                    event_payload['Context'] = subscription.get('Context', 'Default Context')

                                    # Send the event
                                    events.append(grequests.post(subscription['Destination'], timeout=20, data=json.dumps(event_payload), headers=http_headers))
                                else:
                                    logger.info('event not in eventtypes')
                    try:
                        threading.Thread(target=grequests.map, args=(events,)).start()
                    except Exception as e:
                        logger.info('post error {}'.format( str(e)))
                    return (204)
                    self.event_id = self.event_id + 1

        def handle_telemetry(self, data_received):
            sub_path = self.construct_path('/redfish/v1/EventService/Subscriptions', 'index.json')
            success, sub_payload = self.get_cached_link(sub_path)
            logger.info(sub_path)
            if not success:
                # Eventing not supported
                return (404)
            else:
                # Check if all of the parameters are given
                if (('MetricReportName' in data_received) and ('MetricReportValues' in data_received)) or\
                   (('MetricReportName' in data_received) and ('GeneratedMetricReportValues' in data_received)) or\
                        (('MetricName' in data_received) and ('MetricValues' in data_received)):
                    # If the EventType in the request is one of interest to the subscriber, build an event payload
                    expected_keys = ['MetricId', 'MetricValue', 'Timestamp', 'MetricProperty', 'MetricDefinition']
                    other_keys = ['MetricProperty']
                    my_name = data_received.get('MetricName',
                            data_received.get('MetricReportName'))
                    my_data = data_received.get('MetricValues',
                            data_received.get('MetricReportValues',
                            data_received.get('GeneratedMetricReportValues')))
                    event_payload = {}
                    value_list = []
                    # event_payload['@Redfish.Copyright'] = 'Copyright 2014-2016 Distributed Management Task Force, Inc. (DMTF). All rights reserved.'
                    event_payload['@odata.context'] = '/redfish/v1/$metadata#MetricReport.MetricReport'
                    event_payload['@odata.type'] = '#MetricReport.v1_0_0.MetricReport'
                    event_payload['@odata.id'] = '/redfish/v1/TelemetryService/MetricReports/' + my_name
                    event_payload['Id'] = my_name
                    event_payload['Name'] = my_name
                    event_payload['MetricReportDefinition'] = {
                        "@odata.id": "/redfish/v1/TelemetryService/MetricReportDefinitions/" + my_name}
                    now = datetime.datetime.now()
                    event_payload['Timestamp'] = now.strftime('%Y-%m-%dT%H:%M:%S') + ('-%02d' % (now.microsecond / 10000))

                    for tup in my_data:
                        if all(x in tup for x in expected_keys):
                            # uncomment for stricter payload check
                            # ex: if all(x in expected_keys + other_keys for x in tup):
                            value_list.append(tup)
                    event_payload['MetricValues'] = value_list
                    logger.info(event_payload)

                    # construct path "mockdir/path/to/resource/<filename>"
                    event_fpath = self.construct_path(event_payload['@odata.id'], 'index.json')
                    self.patchedLinks[event_fpath] = event_payload

                    report_path = '/redfish/v1/TelemetryService/MetricReports'
                    report_path = self.construct_path(report_path, 'index.json')
                    success, collection_payload = self.get_cached_link(report_path)

                    if not success:
                        collection_payload = {'Members': []}
                        collection_payload['@odata.context'] = '/redfish/v1/$metadata#MetricReportCollection.MetricReportCollection'
                        collection_payload['@odata.type'] = '#MetricReportCollection.v1_0_0.MetricReportCollection'
                        collection_payload['@odata.id'] = '/redfish/v1/TelemetryService/MetricReports'
                        collection_payload['Name'] = 'MetricReports'

                    if event_payload['@odata.id'] not in [member.get('@odata.id') for member in collection_payload['Members']]:
                        collection_payload['Members'].append({'@odata.id': event_payload['@odata.id']})
                    collection_payload['Members@odata.count'] = len(collection_payload['Members'])
                    self.patchedLinks[report_path] = collection_payload

                    # Go through each subscriber
                    events = []
                    for member in sub_payload.get('Members', []):
                        entry = member['@odata.id']
                        entrypath = self.construct_path(entry, 'index.json')
                        success, subscription = self.get_cached_link(entrypath)
                        if not success:
                            logger.info('No such resource')
                        else:
                            # Sanity check the subscription for required properties
                            if ('Destination' in subscription) and ('EventTypes' in subscription):
                                logger.info(('Target', subscription['Destination']))
                                http_headers = {}
                                http_headers['Content-Type'] = 'application/json'

                                # Send the event
                                events.append(grequests.post(subscription['Destination'], timeout=20, data=json.dumps(event_payload), headers=http_headers))
                            else:
                                logger.info('event not in eventtypes')
                    try:
                        threading.Thread(target=grequests.map, args=(events,)).start()
                    except Exception as e:
                        logger.info('post error {}'.format( str(e)))
                    self.event_id = self.event_id + 1
                    return (204)
                else:
                    return (400)

        server_version = "RedfishMockupHTTPD_v" + tool_version
        event_id = 1

        # Headers only request
        def do_HEAD(self):
            """do_HEAD"""
            logger.info("Headers: ")
            logger.info(self.server.headers)

            # construct path "mockdir/path/to/resource/headers.json"
            fpath = self.construct_path(self.path, 'index.json')
            fpath_xml = self.construct_path(self.path, 'index.xml')
            fpath_headers = self.construct_path(self.path, 'headers.json')
            fpath_direct = self.construct_path(self.path, '')

            # If bool headers is true and headers.json exists...
            # else, send normal headers for given resource
            if self.server.headers and (os.path.isfile(fpath_headers)):
                self.send_response(200)
                self.send_header_file(fpath_headers)
            elif (self.server.headers is False) or (os.path.isfile(fpath_headers) is False):
                if self.get_cached_link(fpath)[0]:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("OData-Version", "4.0")
                elif os.path.isfile(fpath_xml) or os.path.isfile(fpath_direct):
                    if os.path.isfile(fpath_xml):
                        file_extension = 'xml'
                    elif os.path.isfile(fpath_direct):
                        filename, file_extension = os.path.splitext(fpath_direct)
                        file_extension = file_extension.strip('.')
                    self.send_response(200)
                    self.send_header("Content-Type", "application/" + file_extension + ";odata.metadata=minimal;charset=utf-8")
                    self.send_header("OData-Version", "4.0")
                else:
                    self.send_response(404)
            else:
                self.send_response(404)
            self.end_headers()

        def do_GET(self):
            """do_GET"""
            # for GETs always dump the request headers to the console
            # there is no request data, so no need to dump that
            logger.info(("GET", self.path))
            logger.info("   GET: Headers: {}".format(self.headers))

            # construct path "mockdir/path/to/resource/<filename>"
            fpath = self.construct_path(self.path, 'index.json')
            fpath_xml = self.construct_path(self.path, 'index.xml')
            fpath_headers = self.construct_path(self.path, 'headers.json')
            fpath_direct = self.construct_path(self.path, '')

            success, payload = self.get_cached_link(fpath)

            scheme, netloc, path, params, query, fragment = urlparse(self.path)
            query_pieces = parse_qs(query, keep_blank_values=True)

            self.try_to_sleep('GET', self.path)

            # handle resource paths that don't exist for shortForm
            # '/' and '/redfish'
            if(self.path == '/' and self.server.shortForm):
                self.send_response(404)
                self.end_headers()

            elif(self.path in ['/redfish', '/redfish/'] and self.server.shortForm):
                self.send_response(200)
                if self.server.headers and (os.path.isfile(fpath_headers)):
                    self.send_header_file(fpath_headers)
                else:
                    self.send_header("Content-Type", "application/json")
                    self.send_header("OData-Version", "4.0")
                self.end_headers()
                self.wfile.write(json.dumps({'v1': '/redfish/v1'}, indent=4).encode())

            # if this location exists in memory or as file
            elif(success):
                # if headers exist... send information (except for chunk info)
                # end headers here (always end headers after response)
                self.send_response(200)
                if self.server.headers and (os.path.isfile(fpath_headers)):
                    self.send_header_file(fpath_headers)
                else:
                    self.send_header("Content-Type", "application/json")
                    self.send_header("OData-Version", "4.0")
                self.end_headers()

                # Strip the @Redfish.Copyright property
                output_data = payload
                output_data.pop("@Redfish.Copyright", None)

                # Query evaluate
                if output_data.get('Members') is not None:
                    my_members = output_data['Members']
                    top_count = int(query_pieces.get('$top', [str(len(my_members))])[0])
                    top_skip = int(query_pieces.get('$skip', ['0'])[0])

                    my_members = my_members[top_skip:]
                    if top_count < len(my_members):
                        my_members = my_members[:top_count]
                        query_out = {'$skip': top_skip + top_count, '$top': top_count}
                        query_string = '&'.join(['{}={}'.format(k, v) for k, v in query_out.items()])
                        output_data['Members@odata.nextLink'] = urlunparse(('', '', path, '', query_string, ''))
                    else:
                        pass

                    output_data['Members'] = my_members
                    pass

                encoded_data = json.dumps(output_data, sort_keys=True, indent=4, separators=(",", ": ")).encode()
                self.wfile.write(encoded_data)

            # if XML...
            elif(os.path.isfile(fpath_xml) or os.path.isfile(fpath_direct)):
                if os.path.isfile(fpath_xml):
                    file_extension = 'xml'
                    f = open(fpath_xml, "r")
                elif os.path.isfile(fpath_direct):
                    filename, file_extension = os.path.splitext(fpath_direct)
                    file_extension = file_extension.strip('.')
                    f = open(fpath_direct, "r")
                self.send_response(200)
                self.send_header("Content-Type", "application/" + file_extension + ";odata.metadata=minimal;charset=utf-8")
                self.send_header("OData-Version", "4.0")
                self.end_headers()
                self.wfile.write(f.read().encode())
                f.close()
            else:
                self.send_response(404)
                self.end_headers()

        def do_PATCH(self):
                logger.info("   PATCH: Headers: {}".format(self.headers))
                self.try_to_sleep('PATCH', self.path)

                if("content-length" in self.headers):
                    lenn = int(self.headers["content-length"])
                    try:
                        data_received = json.loads(self.rfile.read(lenn).decode("utf-8"))
                    except ValueError:
                        print ('Decoding JSON has failed, sending 400')
                        data_received = None

                if data_received:
                    logger.info("   PATCH: Data: {}".format(data_received))

                    # construct path "mockdir/path/to/resource/<filename>"
                    fpath = self.construct_path(self.path, 'index.json')
                    success, payload = self.get_cached_link(fpath)

                    # check if resource exists, otherwise 404
                    #   if it's a file, open it, if its in memory, grab it
                    #   405 if Collection
                    #   204 if patch success
                    #   404 if payload DNE
                    #   400 if no patch payload
                    # end headers
                    if success:
                        # If this is a collection, throw a 405
                        if payload.get('Members') is not None:
                            self.send_response(405)
                        else:
                            # After getting resource, merge the data.
                            logger.info(self.headers.get('content-type'))
                            logger.info(data_received)
                            logger.info(payload)
                            dict_merge(payload, data_received)
                            logger.info(payload)
                            # put into self.patchedLinks
                            self.patchedLinks[fpath] = payload
                            self.send_response(204)
                    else:
                        self.send_response(404)
                else:
                    self.send_response(400)

                self.end_headers()

        def do_PUT(self):
                logger.info("   PUT: Headers: {}".format(self.headers))
                self.try_to_sleep('PUT', self.path)

                if("content-length" in self.headers):
                    lenn = int(self.headers["content-length"])
                    try:
                        data_received = json.loads(self.rfile.read(lenn).decode("utf-8"))
                    except ValueError:
                        print ('Decoding JSON has failed, sending 400')
                        data_received = None
                    logger.info("   PUT: Data: {}".format(data_received))

                # we don't support this service
                #   405
                # end headers
                self.send_response(405)

                self.end_headers()

        def do_POST(self):
                logger.info("   POST: Headers: {}".format(self.headers))
                if("content-length" in self.headers):
                    lenn = int(self.headers["content-length"])
                    try:
                        data_received = json.loads(self.rfile.read(lenn).decode("utf-8"))
                    except ValueError:
                        print ('Decoding JSON has failed, sending 405')
                        data_received = None
                self.try_to_sleep('POST', self.path)

                if data_received:
                    logger.info("   POST: Data: {}".format(data_received))
                    # construct path "mockdir/path/to/resource/<filename>"
                    fpath = self.construct_path(self.path, 'index.json')
                    success, payload = self.get_cached_link(fpath)

                    # don't bother if this item exists, otherwise, check if its an action or a file
                    # if file
                    #   405 if not Collection
                    #   204 if success
                    #   404 if no file present
                    if success:
                        if payload.get('Members') is None:
                            self.send_response(405)
                        else:
                            logger.info(data_received)
                            logger.info(type(data_received))
                            # with members, form unique ID
                            #   must NOT exist in Members
                            #   add ID to members, change count
                            #   store as necessary in self.patchedLinks

                            newpath = self.add_new_member(payload, data_received)

                            newfpath = self.construct_path(newpath, 'index.json')

                            logger.info(newfpath)

                            self.patchedLinks[newfpath] = data_received
                            self.patchedLinks[fpath] = payload
                            self.send_response(204)
                            self.send_header("Location", newpath)
                            self.send_header("Content-Length", "0")
                            self.end_headers()

                    # eventing framework
                    else:
                        if 'EventService/Actions/EventService.SubmitTestEvent' in self.path:
                            r_code = self.handle_eventing(data_received)
                            self.send_response(r_code)
                        elif 'TelemetryService/Actions/TelemetryService.SubmitTestMetricReport' in self.path:
                            r_code = self.handle_telemetry(data_received)
                            self.send_response(r_code)
                        else:
                            self.send_response(404)
                else:
                    self.send_response(405)
                self.end_headers()

        def do_DELETE(self):
                """
                Delete a resource
                """
                logger.info("DELETE: Headers: {}".format(self.headers))
                self.try_to_sleep('DELETE', self.path)

                fpath = self.construct_path(self.path, 'index.json')
                ppath = '/'.join(self.path.split('/')[:-1])
                parent_path = self.construct_path(ppath, 'index.json')
                success, payload = self.get_cached_link(fpath)

                # 404 if file doesn't exist
                # 204 if success, override payload with 404
                #   modify payload to exclude expected URI, subtract count
                # 405 if parent is not Collection
                # end headers
                if success:
                    success, parentData = self.get_cached_link(parent_path)
                    if success and parentData.get('Members') is not None:
                        self.patchedLinks[fpath] = '404'
                        parentData['Members'] = [x for x in parentData['Members'] if not x['@odata.id'] == self.path]
                        parentData['Members@odata.count'] = len(parentData['Members'])
                        self.patchedLinks[parent_path] = parentData
                        self.send_response(204)
                    else:
                        self.send_response(405)
                else:
                    self.send_response(404)

                self.end_headers()

        # Response time calculation Algorithm
        def getResponseTime(self, method, path):
                fpath = self.construct_path(path, 'time.json')
                success, item = self.get_cached_link(path)
                if not any(x in method for x in ("GET", "HEAD", "POST", "PATCH", "DELETE")):
                    logger.info("Not a valid method")
                    return (0)

                if(os.path.isfile(fpath)):
                    with open(fpath) as time_data:
                        d = json.load(time_data)
                        time_str = method + "_Time"
                        if time_str in d:
                            try:
                                float(d[time_str])
                            except Exception as e:
                                logger.info(
                                    "Time in the json file, not a float/int value. Reading the default time.")
                                return (self.server.responseTime)
                            return (float(d[time_str]))
                else:
                    logger.info(('response time:', self.server.responseTime))
                    return (self.server.responseTime)


def usage(program):
        logger.info("usage: {}   [-h][-P][-H <hostIpAddr>:<port>]".format(program))
        logger.info("      -h --help      # logger.infos usage ")
        logger.info("      -H <IpAddr>   --Host=<IpAddr>    # hostIP, default: 127.0.0.1")
        logger.info("      -p <port>     --port=<port>      # port:  default is 8000")
        logger.info("      -D <dir>,     --Dir=<dir>        # Path to the mockup directory. It may be relative to CWD")
        logger.info("      -X,           --headers          # Option to load headers or not from json files")
        logger.info("      -t <delay>    --time=<delayTime> # Delay Time in seconds added to any request. Must be float or int.")
        logger.info("      -E            --TestEtag         # (unimplemented) etag testing--enable returning etag for certain APIs for testing.  See Readme")
        logger.info("      -T                               # Option to delay response or not.")
        logger.info("      -s            --ssl              # Places server in https, requires a certificate and key")
        logger.info("      --cert <cert>                    # Specify a certificate for ssl server function")
        logger.info("      --key <key>                      # Specify a key for ssl")
        logger.info("      -S            --shortForm        # Apply shortform to mockup (allowing to omit filepath /redfish/v1)")
        logger.info("      -P            --ssdp             # Make mockup ssdp discoverable (by redfish specification)")


def main(argv):
        hostname = "127.0.0.1"
        port = 8000
        program = argv[0]
        logger.info(program)
        mockDirPath = None
        sslMode = False
        sslCert = None
        sslKey = None
        mockDir = None
        testEtagFlag = False
        responseTime = 0
        timefromJson = False
        headers = False
        shortForm = False
        ssdpStart = False
        logger.info("Redfish Mockup Server, version {}".format(tool_version))
        try:
            opts, args = getopt.getopt(argv[1:], "hTSPsEH:p:D:t:X", ["help", "shortForm", "ssdp", "ssl", "TestEtag", "headers", "Host=", "Port=", "Dir=",
                                                                    "time=", "cert=", "key="])
        except getopt.GetoptError:
            # usage()
            logger.info("Error parsing options")
            sys.stderr.flush()
            usage(program)
            sys.exit(2)

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                usage(program)
                sys.exit(0)
            elif opt in ("-H", "--Host"):
                hostname = arg
            elif opt in ("-X", "--headers"):
                headers = True
            elif opt in ("-p", "--port"):
                port = int(arg)
            elif opt in ("-D", "--Dir"):
                mockDirPath = arg
            elif opt in ("-E", "--TestEtag"):
                testEtagFlag = True
            elif opt in ("-t", "--time"):
                responseTime = arg
            elif opt in ("-T"):
                timefromJson = True
            elif opt in ("-s", "--ssl"):
                sslMode = True
            elif opt in ("--cert",):
                sslCert = arg
            elif opt in ("--key",):
                sslKey = arg
            elif opt in ("-S", "--shortForm"):
                shortForm = True
            elif opt in ("-P", "--ssdp"):
                ssdpStart = True
            else:
                logger.info('unhandled option')
                sys.exit(2)

        logger.info('program: {}'.format(program))
        logger.info('Hostname: {}'.format(hostname))
        logger.info('Port: {}'.format(port))
        logger.info("dir path specified by user:{}".format(mockDirPath))
        logger.info("response time: {} seconds".format(responseTime))

        # check if mockup path was specified.  If not, use current working directory
        if mockDirPath is None:
            mockDirPath = os.getcwd()

        # create the full path to the top directory holding the Mockup
        mockDir = os.path.realpath(mockDirPath)  # creates real full path including path for CWD to the -D<mockDir> dir path
        logger.info("Serving Mockup in abs real directory path:{}".format(mockDir))

        # check that we have a valid tall mockup--with /redfish in mockDir before proceeding
        if not shortForm:
            slashRedfishDir = os.path.join(mockDir, "redfish")
            if os.path.isdir(slashRedfishDir) is not True:
                logger.info("ERROR: Invalid Mockup Directory--no /redfish directory at top. Aborting")
                sys.stderr.flush()
                sys.exit(1)

        if shortForm:
            if os.path.isdir(mockDir) is not True or os.path.isfile(os.path.join(mockDir, "index.json")) is not True:
                logger.info("ERROR: Invalid Mockup Directory--dir or index.json does not exist")
                sys.stderr.flush()
                sys.exit(1)

        myServer = HTTPServer((hostname, port), RfMockupServer)

        if sslMode:
            logger.info("Using SSL with certfile: {}".format(sslCert))
            myServer.socket = ssl.wrap_socket(myServer.socket, certfile=sslCert, keyfile=sslKey, server_side=True)

        # save the test flag, and real path to the mockup dir for the handler to use
        myServer.mockDir = mockDir
        myServer.testEtagFlag = testEtagFlag
        myServer.headers = headers
        myServer.timefromJson = timefromJson
        myServer.shortForm = shortForm
        try:
            myServer.responseTime = float(responseTime)
        except ValueError as e:
            logger.info("Enter a integer or float value")
            sys.exit(2)
        # myServer.me="HELLO"

        mySDDP = None
        if ssdpStart:
            # construct path "mockdir/path/to/resource/<filename>"
            fpath = myServer.construct_path('/redfish/v1', 'index.json')
            success, item = myServer.get_cached_link(fpath)
            protocol = '{}://'.format('https' if sslMode else 'http')
            mySDDP = RfSDDPServer(item, '{}{}:{}{}'.format(protocol, hostname, port, '/redfish/v1'), hostname)

        logger.info("Serving Redfish mockup on port: {}".format(port))
        try:
            if mySDDP is not None:
                t2 = threading.Thread(target=mySDDP.start)
                t2.daemon = True
                t2.start()
            logger.info('running Server...')
            myServer.serve_forever()

        except KeyboardInterrupt:
            pass

        myServer.server_close()
        logger.info("Shutting down http server")


# the below is only executed if the program is run as a script
if __name__ == "__main__":
        main(sys.argv)

'''
TODO:
1. add -L option to load json and dump output from python dictionary
2. add authentication support -- note that in redfish some api don't require auth
3. add https support


'''
