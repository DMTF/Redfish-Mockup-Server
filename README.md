Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.

# redfishMockupServer

## About
***redfishMockupServer*** is a short python 3.4+ program that can be copied into folder at top of any redfish mockup and can serve redfish requests on the specified IP/port.

## Usage
###To start the server:
* copy to the folder that is the top of the mockup.  
 * "redfish" should be a sub-directory.   
 * This is a "Tall Mockup" which includes /redfish/v1 in the mockup directory structure in case some of the URIs in the mockup do not start with /redfish/v1.

* make sure python34 is in your path
* run redfishMockupServer from your windows command shell: `.\redfishMockupServer`
* Default hostname/IP is localhost:  127.0.0.1
* Default port is:  8000
* You can create multiple mockup servers running on multiple ports:

### Options:

* `redfishMockupServer -h`     -- gives help usage and exits

* `redfishMockupServer [-H *HostIpAddress* ] [-P *port*]`    
  * default *HostIpAddress* is 127.0.0.1
  * default *port*         is 8000
* Example:    
`.\redfishMockupServer -P 8001`   # to start another service on port 8001



