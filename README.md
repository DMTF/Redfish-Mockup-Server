Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.

# redfishMockupServer

## About
***redfishMockupServer*** is a short python 3.4+ program that can be copied into folder at top of any redfish mockup and can serve redfish requests on the specified IP/port.

## Usage
###To start the server:
* copy the ***redfishMockupServer.py*** file to the the folder you want to execute it from
* use the `-D <mockupDir>` option to specify an absolute or relative path to the mockup dir from CWD
* Note that the mockup directory must start with /redfish:  
 * "redfish" should be a sub-directory.   
 * This is a "Tall Mockup" which includes /redfish/v1 in the mockup directory structure in case some of the URIs in the mockup do not start with /redfish/v1.

* make sure python34 is in your path
* run redfishMockupServer from your windows command shell eg: `.\redfishMockupServer [-D <mockupDir>]`
* Default hostname/IP is localhost:  127.0.0.1
* Default port is:  8000
* You can create multiple mockup servers running on multiple ports:

### Options:

* `redfishMockupServer -h`     -- gives help usage and exits

* `redfishMockupServer [-H *HostIpAddress* ] [-P *port*] [-D <mockupDir>] [-H <host>] [-P <port>] [-T]`    
  * default *HostIpAddress* is 127.0.0.1
  * default *port*         is 8000
  * *mockupDir* is absolute or relative to CWD if starting with . or ..
  * -T option causes mockup server to generate etags on GETs for certain hard coded APIs for testing client patch etag code
    * response header Etag: "W/12345" is returned on GET /redfish/v1/Systems/1
    * response header Etag: "123456"  is returned on GET /redfish/v1/AccountService/Accounts/1
* Example:    
`.\redfishMockupServer -P 8001 -D ./MyServerMockup9`   # to start another service on port 8001 from folder *./MyServerMockup9*



