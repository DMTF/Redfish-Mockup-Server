# Redfish Mockup Server

Copyright 2016-2020 DMTF. All rights reserved.

## About

The Redfish Mockup Server serves Redfish requests against a Redfish mockup. The server runs at either a specified IP address and port or the default IP address and port, `127.0.0.1:8000`.

You can find DMTF-published sample mockups at [All Published Versions of DSP2043](https://www.dmtf.org/dsp/DSP2043 "https://www.dmtf.org/dsp/DSP2043").

To create a mockup from a service, use the [Redfish-Mockup-Creator](https://github.com/DMTF/Redfish-Mockup-Creator "https://github.com/DMTF/Redfish-Mockup-Creator").

## Requirements

To run the mockup server natively on your system:

* Install [Python 3](https://www.python.org/downloads/ "https://www.python.org/downloads/") and [pip](https://pip.pypa.io/en/stable/installing/ "https://pip.pypa.io/en/stable/installing").
* Install required Python packages: `pip install -r requirements.txt`
* See the [Native system example](#native-system-example).

To run the mockup server as a Docker container:

* Install [Docker](https://www.docker.com/get-started "https://www.docker.com/get-started").
* See the [Docker container example](#docker-container-example).

## Usage

```
Redfish Mockup Server, version 1.1.4
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

### Description

The mockup server starts an HTTP server at the `-H HOST` host and `-p PORT` port. The mockup server provides Redfish resources in the `-D DIR` mockup directory.

If the mockup does not contain the representation of the `/redfish` resource, you must provide the `--short-form` argument. If you omit the mockup, the mockup server serves DMTF's `public-rackmount1` mockup.

### Native system example

```bash
python redfishMockupServer.py -D /home/user/redfish-mockup
```

### Docker container example

To run as a Docker container, use one of these actions to pull or build the container:

* Pull the container from Docker Hub:

    ```bash
    docker pull dmtf/redfish-mockup-server:latest
    ```
* Build a container from local source:

    ```bash
    docker build -t dmtf/redfish-mockup-server:latest .
    ```
* Build a container from GitHub:

    ```bash
    docker build -t dmtf/redfish-mockup-server:latest https://github.com/DMTF/Redfish-Mockup-Server.git
    ```

This command runs the container with the built-in `public-rackmount1` mockup:

```bash
docker run --rm dmtf/redfish-mockup-server:latest
```

This command runs the container with a specified mockup, where `<path-to-mockup>` is the path to the mockup directory:

```bash
docker run --rm -v <path-to-mockup>:/mockup dmtf/redfish-mockup-server:latest -D /mockup
```

## Release process

To publish a new version, run the `release.sh` script, where `<new-version>` is the new version number:

```bash
sh release.sh <new-version>
```

When prompted, type the release notes. To indicate the end of notes, enter an an empty line.
