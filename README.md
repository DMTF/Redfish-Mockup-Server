# Redfish Mockup Server

Copyright 2016-2020 DMTF. All rights reserved.

## About

The Redfish Mockup Server serves Redfish requests against a Redfish mockup.
The server runs at a specified IP address and port or at `127.0.0.1:8000`, which is the default IP address and port.

Sample mockups published by the DMTF can be found here: [https://www.dmtf.org/dsp/DSP2043](https://www.dmtf.org/dsp/DSP2043).
The [Redfish-Mockup-Creator](https://github.com/DMTF/Redfish-Mockup-Creator) can be used to create a mockup from an existing service.

## Requirements

If running the mockup server natively on your system:
* Install [Python 3](https://www.python.org/downloads/) and [pip](https://pip.pypa.io/en/stable/installing/)
* Install required Python packages: `pip install -r requirements.txt`

If running the mockup server as a Docker container:
* Install [Docker](https://www.docker.com/get-started)

## Usage

```
Redfish Mockup Server, version 1.1.1
usage: redfishMockupServer.py [-h] [-H HOST] [-p PORT] [-D DIR] [-E] [-X]
                              [-t TIME] [-T] [-s] [--cert CERT] [--key KEY]
                              [-S] [-P]

Serve a static Redfish mockup.

optional arguments:
  -h, --help            show this help message and exit
  -H HOST, --host HOST, --Host HOST
                        hostname or IP address (default 127.0.0.1)
  -p PORT, --port PORT, --Port PORT
                        host port (default 8000)
  -D DIR, --dir DIR, --Dir DIR
                        path to mockup dir (may be relative to CWD)
  -E, --test-etag, --TestEtag
                        (unimplemented) etag testing
  -X, --headers         load headers from headers.json files in mockup
  -t TIME, --time TIME  delay in seconds added to responses (float or int)
  -T                    delay response based on times in time.json files in
                        mockup
  -s, --ssl             place server in SSL (HTTPS) mode; requires a cert and
                        key
  --cert CERT           the certificate for SSL
  --key KEY             the key for SSL
  -S, --short-form, --shortForm
                        apply short form to mockup (omit filepath /redfish/v1)
  -P, --ssdp            make mockup SSDP discoverable
```

Example: `python redfishMockupServer.py -D /home/user/redfish-mockup`

The mockup server will start an HTTP server with the given address and port specified by the *HOST* and *PORT* arguments.
The mockup server will provide Redfish resources in the mockup directory specified by the *DIR* argument.
If the mockup does not contain the representation of the `/redfish` resource, the *short-form* argument will need to be provided by the user.
If no mockup is specified, the mockup server will serve the DMTF's "public-rackmount1" mockup.

## Docker Container

If running as a Docker container, you can either:
* Pull the container from Docker Hub: `docker pull dmtf/redfish-mockup-server:latest`
* Build a container from source: `docker build -t dmtf/redfish-mockup-server:latest .`

The following will run the container using the built-in "public-rackmount1" mockup:
```bash
docker run --rm dmtf/redfish-mockup-server:latest
```

The following will run the container using a specified mockup, where `<PathToMockup>` is the path to the mockup directory:
```bash
docker run --rm -v <PathToMockup>:/mockup dmtf/redfish-mockup-server:latest -D /mockup
```

## Release Process

Run the `release.sh` script to publish a new version.

```bash
sh release.sh <NewVersion>
```

Enter the release notes when prompted; an empty line signifies no more notes to add.
