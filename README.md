Copyright 2016-2020 DMTF. All rights reserved.

# The Redfish mockup server

The Redfish mockup server, `redfishMockupServer.py`, runs at a specified IP address and port or at the default IP address and port, `127.0.0.1:8000`, and serves Redfish GET, PATCH, POST, and DELETE requests and implements the `SubmitTestEvent` action.

---

* [Install prerequisite software](#install-prerequisite-software)
* [Install the Redfish mockup server](#install-the-redfish-mockup-server)
* [Start the server](#start-the-server)
* [redfishMockupServer usage](#redfishMockupServer-usage)
* [Release process](#release-process)

## Install prerequisite software

* **Python&nbsp;3.4&nbsp;or&nbsp;later**

    If Python 3.4 or later is not already installed, [download Python](https://www.python.org/downloads/ "https://www.python.org/downloads/") for your operating system.

    Verify the Python installation:
        
    ```
    $ python --version
    ```

    Ensure that Python 3.4 or later is in your path.
* **[pip](https://pip.pypa.io/en/stable/ "https://pip.pypa.io/en/stable/")**

    If pip is not installed, install it:
    
    ```
    $ curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    $ python get-pip.py
    ```

    Upgrade pip and then verify the pip installation:
    
    ```
    $ pip install --upgrade pip
    $ pip --version
    ```
* **Required Python packages**

    Install the required Python packages:

    ```
    $ pip install -r requirements.txt
    ```

## Install the Redfish mockup server

Copy `redfishMockupServer.py` into the root of a Redfish mockup directory structure.

> **Note:** Although a mockup directory structure normally starts with `/redfish`, `/redfish` must be a subdirectory of the mockup directory structure.

## Start the server

To start the server, run `redfishMockupServer.py` from your command shell:

```
$ python redfishMockupServer.py -D <DIR>
```

where

* `-D <DIR>` is the absolute or relative path to the mockup directory from the current working directory (CWD).

For example, if you copy `redfishMockupServer.py` to the `MyServerMockup9` folder, run this command to start the server on port 8001:

```
$ python redfishMockupServer.py -p 8001 -D ./MyServerMockup9
```

> **Note:** You can run the server in *tall* or *short* mode:
> 
> | Mode | Description | Note |
> |:-----|:------------|:-----|
> | Tall  | Includes `/redfish/v1` at the top of the mockup directory structure. | Default is tall mode. |
> | Short | Does not include `/redfish/v1` at the top of the mockup directory structure. | Use the `-S` option to run in short mode. |

## redfishMockupServer usage

```
redfishMockupServer.py [-h] [-H <HOST>] [-p <PORT>] [-D <DIR>] [-E] [-X]
                       [-t <TIME>] [-T] [-s --cert <CERT> -key <KEY>]
                       [-S] [-P]
```

where

<table>
  <thead>
    <tr align="left" valign="top">
      <th>Option&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</th>
      <th>Description</th>
      <th>Default</th>
    </tr>
  </thead>
  <tbody>
    <tr align="left" valign="top">
      <td><code>-h</code></td>
      <td>Show usage information and exit.</td>
      <td></td>
    </tr>
    <tr align="left" valign="top">
      <td><code>-H &lt;HOST&gt;</code></td>
      <td>Host name or IP address.</td>
      <td><code>localhost</code><br /><code>127.0.0.1</code></td>
    </tr>
    <tr align="left" valign="top">
      <td><code>-p &lt;PORT&gt;</code></td>
      <td>Port or ports. You can specify the <code>p</code> option multiple times to create multiple mockup servers that run on different ports.</td>
      <td><code>8000</code></td>
    </tr>
    <tr align="left" valign="top">
      <td><code>-D &lt;DIR&gt;</code></td>
      <td>Absolute or relative path to the mockup directory from the current working directory (CWD).</td>
      <td></td>
    </tr>
    <tr align="left" valign="top">
      <td><code>-E</code></td>
      <td>Not implemented. ETag testing.</td>
      <td></td>
    </tr>
    <tr align="left" valign="top">
      <td><code>-X</code></td>
      <td>Send headers from the <code>headers.json</code> file.</td>
      <td>Send&nbsp;standard&nbsp;headers&nbsp;&nbsp;</td>
    </tr>
    <tr align="left" valign="top">
      <td><code>-t &lt;TIME&gt;</code></td>
      <td>Delay, in seconds, added to each response. Value must be a float or an integer.</td>
      <td><code>0</code></td>
    </tr>
    <tr align="left" valign="top">
      <td><code>-T</code></td>
      <td>Response delay from the <code>time.json</code> file.</td>
      <td></td>
    </tr>
    <tr align="left" valign="top">
      <td><code>-s --cert &lt;CERT&gt; -key &lt;KEY&gt;</code></td>
      <td>Run server in Secure Sockets Layer (SSL) or HTTPS mode, where
        <ul>
          <li><code>--cert &lt;CERT&gt;</code>. The certificate file for SSL.</li>
          <li><code>--key &lt;KEY&gt;</code>. The key file for SSL.</li>
        </ul>
      </td>
      <td>Non-SSL or HTTP mode</td>
    </tr>
    <tr align="left" valign="top">
      <td><code>-S</code></td>
      <td>Run in short mode, or omit the <code>/redfish/v1</code> file path.</td>
      <td>Long mode</td>
    </tr>
    <tr align="left" valign="top">
      <td><code>-P</code></td>
      <td>Make the mockup Simple Service Discovery Protocol (SSDP) discoverable.</td>
      <td></td>
    </tr>
  </tbody>
</table>

## Release process

To create a release of the Redfish mockup server:

1. Update `CHANGELOG.md` with the list of changes since the last release.
1. Update the `tool_version` variable in `redfishMockupServer.py` to the new version of the tool.
1. Push changes to GitHub.
1. Create a release in GitHub.
