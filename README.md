Copyright 2016-2018 DMTF. All rights reserved.

# redfishMockupServer

## About

***redfishMockupServer*** is a short python 3.4+ program that can be copied into folder at top of any redfish mockup and can serve redfish requests on the specified IP/port.  As a server, it may receive GET, PATCH, POST and DELETE commands, and implements the SubmitTestEvent action.

## Usage

### Requirements

In order to use this tool, please install the "requests" package for Python3.

pip3 install requests

### To start the server:

* copy the ***redfishMockupServer.py*** file to the the folder you want to execute it from
* use the `-D <mockupDir>` option to specify an absolute or relative path to the mockup dir from CWD
* use the `-T` option to tell mockup server to include response delay in time.
* use the `-t <responseTime>` option to change default delay in seconds to each response. Default is 0 sec. Must be float or int.
* use the `-X` or `--headers` option to tell mockup server, to send headers. Loads from headers.json. If not, defaults are sent.
* use the `-s` option to specify https protocol
 * In order for the server to function, you must also include `--cert` and `--key` files for the server to function
* Note that the mockup directory must start with /redfish:  
 * "redfish" should be a sub-directory.   
 * This is a "Tall Mockup" which includes /redfish/v1 in the mockup directory structure in case some of the URIs in the mockup do not start with /redfish/v1.
 * If you wish to use a "Short" Mockup, use the `-S` modifier
* make sure python34 is in your path
* run redfishMockupServer from your windows command shell eg: `.\redfishMockupServer [-D <mockupDir>]`
* Default hostname/IP is localhost:  127.0.0.1
* Default port is:  8000
* You can create multiple mockup servers running on multiple ports:

### Options:

* `redfishMockupServer -h`     -- gives help usage and exits

* `redfishMockupServer [-H *HostIpAddress* ] [-P *port*] [-D <mockupDir>] [-H <host>] [-P <port>] [-T] [-t <responseTime>] [-X] [-E]`
  * default *HostIpAddress* is 127.0.0.1
  * default *port*         is 8000
  * *mockupDir* is absolute or relative to CWD if starting with . or ..
  * -T option causes mockup server to include delay in reponse. Loads from time.json . If not, looks up the default delay time.
  * -E option causes mockup server to generate etags on GETs for certain hard coded APIs for testing client patch etag code
    * response header Etag: "W/12345" is returned on GET /redfish/v1/Systems/1
    * response header Etag: "123456"  is returned on GET /redfish/v1/AccountService/Accounts/1
  * `-t <responseTime>` tells the mockup server to add `<responseTime>` default delay to each response.  Default is 0 sec. Must be float or int
  * `-X` or `--headers` tells the mockup server to send headers from headers.json file
* Example:    
`.\redfishMockupServer -P 8001 -D ./MyServerMockup9 -X `   # to start another service on port 8001 from folder *./MyServerMockup9*

## Release Process

1. Update `CHANGELOG.md` with the list of changes since the last release
2. Update the `tool_version` variable in `redfishMockupServer.py` to reflect the new tool version
3. Push changes to Github
4. Create a new release in Github
