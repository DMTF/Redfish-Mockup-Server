Copyright 2016-2020 DMTF. All rights reserved.

# Redfish mockup server

The Redfish mockup server serves Redfish API requests against a Redfish mockup bundle. The server runs at a specified IP address and port or at `127.0.0.1:8000`, which is the default IP address and port.

<a id="server-form"></a>The server runs in either *tall* or *short* form. In tall form, which is the default, the server expects the `/redfish` resource at the top of the directory structure. In short form, the server expects the `/redfish/v1` resource at the top of the directory structure. To run in short form, specify the `-S` option. For complete usage information, see [redfishMockupServer usage](#redfishmockupserver-usage).

If you update `redfishMockupServer.py`, you must push your changes to this repository and [create a Redfish mockup server release](#create-a-redfish-mockup-server-release).

## Contents

* [Step 1. Clone the server and save the mockup bundle](#step-1-clone-the-server-and-save-the-mockup-bundle)
* [Step 2a. Install and run the server inside Docker](#step-2a-install-and-run-the-server-inside-docker)
* [Step 2b. Install and run the server outside Docker](#step-2b-install-and-run-the-server-outside-docker)
* [redfishMockupServer usage](#redfishmockupserver-usage)
* [Create a Redfish mockup server release](#create-a-redfish-mockup-server-release)

## Step 1. Clone the server and save the mockup bundle

After you clone the server and save the mockup bundle, you can install and run the server either inside Docker or outside Docker.

1. Clone the [Redfish mockup server repository](https://github.com/dmtf/Redfish-Mockup-Server "https://github.com/dmtf/Redfish-Mockup-Server").
1. Go to the [All Published Versions of DSP2043](https://www.dmtf.org/dsp/DSP2043 "https://www.dmtf.org/dsp/DSP2043") page and in the **Title** column, click the **Redfish Mockup Bundle** link, and save the ZIP file to your preferred location.
1. Install and run the server either [inside Docker](#step-2a-install-and-run-the-server-inside-docker) or [outside Docker](#step-2b-install-and-run-the-server-outside-docker):

## Step 2a. Install and run the server inside Docker

1. [Install Docker for your operating system](https://www.docker.com/get-started "https://www.docker.com/get-started").
1. Navigate to the directory where you cloned the Redfish mockup server repository, install the server, and run the server:

    ```bash
    $ cd Redfish-Mockup-Server
    $ docker build -t redfish-mockup-server:latest .
    $ docker run --rm -it -v /<absolute-path-to-mockup>:/<mymockup> redfish-mockup-server:latest -D /<mymockup>
    ```

    where

    * `/<absolute-path-to-mockup>:/<mymockup>`. Absolute path to the mockup bundle.
    * `/<mymockup>`. Mockup directory.

## Step 2b. Install and run the server outside Docker

1. Install [Python 3](https://www.python.org/downloads/ "https://www.python.org/downloads/") and [pip](https://pip.pypa.io/en/stable/installing/ "https://pip.pypa.io/en/stable/installing/").
1. Install Python packages:

    ```bash
    $ pip install -r requirements.txt
    ```
1. Start the server in [*short form*](#server-form) against the mockup. For example, you can start the server in short form on port 8000, as follows:

    ```bash
    $ cd Redfish-Mockup-Server
    $ python3 redfishMockupServer.py -S -D ../DSP2043_2019.1/public-localstorage
    ```

    > **Note:** This step assumes that you saved the `DSP2043_2019.1` bundle to the `DSP2043_2019.1` directory, which is parallel with the `Redfish-Mockup-Server` directory.

## redfishMockupServer usage

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

## Create a Redfish mockup server release

If you update `redfishMockupServer.py`, you must create a Redfish mockup server release, as follows:

1. Update [`CHANGELOG.md`](https://github.com/DMTF/Redfish-Mockup-Server/blob/master/CHANGELOG.md "https://github.com/DMTF/Redfish-Mockup-Server/blob/master/CHANGELOG.md") with the list of changes since the last release.
1. Update the [`tool_version` variable in `redfishMockupServer.py`](https://github.com/DMTF/Redfish-Mockup-Server/blob/master/redfishMockupServer.py#L31 "https://github.com/DMTF/Redfish-Mockup-Server/blob/master/redfishMockupServer.py#L31") to the new version of the tool.
1. Push changes to the [GitHub Redfish-Mockup-Server repository](https://github.com/DMTF/Redfish-Mockup-Server "https://github.com/DMTF/Redfish-Mockup-Server").
1. [Create a release](https://docs.github.com/en/free-pro-team@latest/github/administering-a-repository/managing-releases-in-a-repository#creating-a-release "https://docs.github.com/en/free-pro-team@latest/github/administering-a-repository/managing-releases-in-a-repository#creating-a-release") in GitHub.
