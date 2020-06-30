Copyright 2016-2020 DMTF. All rights reserved.

# The Redfish mockup server

The Redfish mockup server, `redfishMockupServer.py`, serves Redfish GET, PATCH, POST, and DELETE requests against a Redfish mockup bundle, and implements the `SubmitTestEvent` action.

The server runs at either:

* An IP address and port that you specify when you run the server.
* The default IP address and port, `127.0.0.1:8000`.

## Prerequisite software

You must install [Python 3.4 or later](#python-34-or-later), [pip](#pip), and [Python packages](#python-packages).

### Python 3.4 or later

1. Verify your Python installation:

    ```
    $ python --version
    ```

1. If Python 3.4 or later is not installed, [download Python](https://www.python.org/downloads/ "https://www.python.org/downloads/") for your operating system and verify the Python installation again.

1. Ensure that Python 3.4 or later is in your path:

    ```
    $ echo $PATH
    ```
### pip

1. Verify your pip installation:

    ```
    $ pip --version
    ```

1. If [pip](https://pip.pypa.io/en/stable/ "https://pip.pypa.io/en/stable/") is not installed, install it:

    ```
    $ curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    $ python3 get-pip.py
    ```

1. Upgrade pip and verify the installation again:

    ```
    $ pip install --upgrade pip
    $ pip --version
    ```

### Python packages

Install the Python packages:

```
$ pip install -r requirements.txt
```

## Get a Redfish mockup bundle

1. Go to [Redfish Mockup Bundle](https://www.dmtf.org/dsp/DSP2043 "https://www.dmtf.org/dsp/DSP2043") to get the Redfish mockup bundle.
1. Click the **Redfish Mockup Bundle** link and save the bundle to your preferred location.

## Start the server

To start the server, run `redfishMockupServer.py` from your command shell:

```
$ python3 redfishMockupServer.py -S -D <DIR>
```

where

* `-D <DIR>` is the absolute or relative path from the current working directory (CWD) to the directory where you placed the Redfish mockup bundle.

    Default is the CWD.
* `-S`. Runs the server in *short* form.

    The form determines whether the server expects the version resource or the service root resource at the top of the mockup directory structure:

    | Form  | At the top of the mockup directory structure |
    | :---  | :---        |
    | Tall  | The version resource, `/redfish`. | Default is tall form. |
    | Short | The service root resource, `/redfish/v1/`.<br/><br/>Use the `-S` option to run in short form. |

## Example

For example, if you copy the DSP2043_2019.1 bundle to a `DSP2043_2019.1` directory that is parallel with the `Redfish-Mockup-Server` directory, run this command to start the server in short form on port 8001:

```
$ cd Redfish-Mockup-Server
$ python3 redfishMockupServer.py -S -D ../DSP2043_2019.1/public-localstorage
```

## redfishMockupServer usage

```
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

## Release process

To create a release of the Redfish mockup server:

1. Update `CHANGELOG.md` with the list of changes since the last release.
2. Update the `tool_version` variable in `redfishMockupServer.py` to the new version of the tool.
3. Push changes to GitHub.
4. Create a release in GitHub.
