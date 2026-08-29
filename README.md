# Redfish Mockup Server

Copyright 2016-2020 DMTF. All rights reserved.

[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://github.com/DMTF/Redfish-Mockup-Server/blob/main/LICENSE.md)
[![Pulls](https://img.shields.io/docker/pulls/dmtf/redfish-mockup-server?style=flat&logo=docker&label=Pulls)](https://hub.docker.com/r/dmtf/redfish-mockup-server)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat)](https://github.com/psf/black)
[![Linters](https://github.com/DMTF/Redfish-Mockup-Server/actions/workflows/linters.yml/badge.svg)](https://github.com/DMTF/Redfish-Mockup-Server/actions/workflows/linters.yml)
[![Docker](https://github.com/DMTF/Redfish-Mockup-Server/actions/workflows/docker.yml/badge.svg)](https://github.com/DMTF/Redfish-Mockup-Server/actions/workflows/docker.yml)
[![GitHub stars](https://img.shields.io/github/stars/DMTF/Redfish-Mockup-Server.svg?style=flat-square&label=github%20stars)](https://github.com/DMTF/Redfish-Mockup-Server)
[![GitHub Contributors](https://img.shields.io/github/contributors/DMTF/Redfish-Mockup-Server.svg?style=flat-square)](https://github.com/DMTF/Redfish-Mockup-Server/graphs/contributors)

## About

The Redfish Mockup Server serves Redfish requests against a Redfish mockup.  The server runs at either a specified IP address and port or the default IP address and port, `127.0.0.1:8000`.

You can find DMTF-published sample mockups at [All Published Versions of DSP2043](https://www.dmtf.org/dsp/DSP2043 "https://www.dmtf.org/dsp/DSP2043").

To create a mockup from a service, use the [Redfish-Mockup-Creator](https://github.com/DMTF/Redfish-Mockup-Creator "https://github.com/DMTF/Redfish-Mockup-Creator").

The scope of this tool is to serve a static mockup for development purposes.  It does support modification requests, such as `PATCH` and `POST`, and actions to a limited extent.  For a more feature-rich Redfish experience, one of the following tools can be used instead of the Redfish Mockup Server:

* [Redfish-Interface-Emulator](https://github.com/DMTF/Redfish-Interface-Emulator): A more functional service that implements modification requests and actions.
* [Swordfish-API-Emulator](https://github.com/SNIA/Swordfish-API-Emulator): A SNIA extension to the previous tool with more built-in functionality supported.

## Requirements

To run the mockup server natively on your system:

* Install [Python 3](https://www.python.org/downloads/ "https://www.python.org/downloads/") and [pip](https://pip.pypa.io/en/stable/installing/ "https://pip.pypa.io/en/stable/installing").
* Install required Python packages: `pip install -r requirements.txt`

To run the mockup server as a Docker container:

* Install [Docker](https://www.docker.com/get-started "https://www.docker.com/get-started").

## Usage

The Redfish Mockup Server can be configured using either command-line arguments or a configuration file (config.ini).

### Configuration File

You can use a `config.ini` file in the current working directory with your settings. This is useful for repeated operations with the same configuration.

Example `config.ini`:

```ini
[Server]
host = 127.0.0.1
port = 8000

[Mockup]
Dir = /path/to/mockup
short-form = false

[SSL]
ssl = false
cert = 
key = 

[Options]
headers = false
time = 0
timefromjson = false
test-etag = false
ssdp = false
```

To use a configuration file in a different location, use the `--config` option:

```bash
python redfishMockupServer.py --config /path/to/myconfig.ini
```

**Note:** Command-line arguments always override configuration file settings, ensuring backward compatibility.

### Command-Line Arguments

```text
Redfish Mockup Server, version 1.1.4
usage: redfishMockupServer.py [-h] [-c CONFIG] [-H HOST] [-p PORT] [-D DIR]
                              [-E] [-X] [-t TIME] [-T] [-s] [--cert CERT]
                              [--key KEY] [-S] [-P]

Serve a static Redfish mockup.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to configuration file; defaults to 'config.ini'
                        in current directory
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

### Examples

Using command-line arguments only (backward compatible):

```bash
python redfishMockupServer.py -H 127.0.0.1 -p 8000 -D /home/user/redfish-mockup
```

Using a configuration file:

```bash
# Uses config.ini from current directory
python redfishMockupServer.py
```

Using a custom configuration file:

```bash
python redfishMockupServer.py --config /path/to/custom.ini
```

Mixing configuration file and command-line arguments (command-line overrides config):

```bash
# Uses settings from config.ini but overrides the port
python redfishMockupServer.py -p 9000
```

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
    docker build -t dmtf/redfish-mockup-server:latest https://github.com/DMTF/Redfish-Mockup-Server.git#main
    ```

This command runs the container with the built-in `public-rackmount1` mockup:

```bash
docker run --rm dmtf/redfish-mockup-server:latest
```

This command runs the container with a specified mockup, where `<path-to-mockup>` is the path to the mockup directory:

```bash
docker run --rm -v <path-to-mockup>:/mockup dmtf/redfish-mockup-server:latest -D /mockup
```

Or using compose:

```bash
docker compose up
```

## Release process

1. Go to the "Actions" page
2. Select the "Release and Publish" workflow
3. Click "Run workflow"
4. Fill out the form
5. Click "Run workflow"
