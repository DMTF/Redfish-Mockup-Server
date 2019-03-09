Copyright 2016-2019 DMTF. All rights reserved.

# redfishMockupServer

## About

***redfishMockupServer*** is a short python 3.4+ program that can be copied into folder at top of any redfish mockup and can serve redfish requests on the specified IP/port.  As a server, it may receive GET, PATCH, POST and DELETE commands, and implements the SubmitTestEvent action.

## Usage

### Requirements

In order to use this tool, please install the "requests" and "grequests" package for Python3.

pip3 install requests
pip3 install grequests

or

pip3 install -r requirements.txt

### To start the server:

* Copy the ***redfishMockupServer.py*** file to the the folder you want to execute it from.
* Use the `-D <mockupDir>` option to specify an absolute or relative path to the mockup dir from CWD.
* Use the `-T` option to tell mockup server to include response delay from the mockup time.json file.
* Use the `-t <responseTime>` option to change default delay in seconds to each response. Default is 0 sec. Must be float or int.
* Use the `-X` or `--headers` option to tell mockup server to send headers. Loads from headers.json. If not, defaults are sent.
* Use the `-s` option to specify SSL (HTTPS) protocol.
 * In order for the server to function, you must also specify `--cert` and `--key` files.
* Note that the mockup directory will normally start with `/redfish`:
 * `redfish` should be a sub-directory.
 * This is a "Tall Mockup" which includes `/redfish/v1` at the top of the mockup directory structure.
 * A "Short Mockup" does not include `/redfish/v1` at the top of the mockup tree.
 * If you wish to use a "Short Mockup", use the `-S` option.
* Make sure python version 3.4+ is in your path
* Run redfishMockupServer from your command shell, e.g.: `python redfishMockupServer.py [-D <mockupDir>]`
* Default hostname/IP is localhost: 127.0.0.1
* Default port is: 8000
* You can create multiple mockup servers running on different ports using the `-p` option.
* See **Options** section below for additional options.

### Options:

* `python redfishMockupServer.py -h` -- gives help usage and exits

* Usage:

```
Usage: redfishMockupServer.py <options>
  options:
    -h, --help                               # Display usage syntax
    -H <host>, --host <host>, --Host <host>  # Hostname or IP addr, default: 127.0.0.1
    -p <port>, --port <port>, --Port <port>  # Host port, default: 8000
    -D <dir>, --dir <dir>, --Dir <dir>       # Path to the mockup directory; may be relative to CWD
    -X, --headers                            # Load headers from headers.json files
    -t <delay>, --time <delay>               # Delay time in seconds added to request; must be float or int
    -E, --test-etag, --TestEtag              # (unimplemented) etag testing
    -T                                       # Delay response based on times in time.json files
    -s, --ssl                                # Place server in SSL (HTTPS) mode; requires a certificate and key
    --cert <cert>                            # Specify a certificate for SSL
    --key <key>                              # Specify a key for SSL
    -S, --short-form, --shortForm            # Apply short form to mockup (omit filepath /redfish/v1)
    -P, --ssdp                               # Make mockup SSDP discoverable
```

* Example:    
 * Start another service on port 8001 from folder `./MyServerMockup9`:
`python redfishMockupServer.py -p 8001 -D ./MyServerMockup9`

## Release Process

1. Update `CHANGELOG.md` with the list of changes since the last release
2. Update the `tool_version` variable in `redfishMockupServer.py` to reflect the new tool version
3. Push changes to Github
4. Create a new release in Github
