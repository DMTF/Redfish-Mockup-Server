# Serv
import socket
import sys


# based on https://github.com/ZeWaren/python-upnp-ssdp-example/blob/master/lib/ssdp.py
class RfSDDPServer():
    def __init__(self, ip=None, port=1900, timeout=5):
        """__init__

        Initialize an SDDP server

        :param ip: address to bind to (IPV4 only?)
        :param port: port for server to exist on, default port 1900
        :param timeout: int for packet timeout
        """
        ip = ip if ip is not None else "0.0.0.0"
        self.ip, self.port = ip, port
        # initiate multicast socket
        # rf-spec:
        #   must use TTL 2
        #   must use port 1900
        #   optional MSEARCH messages: Notify, Alive, Shutdown
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        addr = socket.inet_aton('239.255.255.250')
        interface = socket.inet_aton(self.ip)
        cmd = socket.IP_ADD_MEMBERSHIP
        sock.setsockopt(socket.IPPROTO_IP, cmd, addr + interface)
        sock.bind((self.ip, self.port))
        sock.settimeout(timeout)
        """
        Redfish Service Search Target (ST): "urn:dmtf-org:service:redfish-rest:1"
        For ssdp, "ssdp:all".
        For UPnP compatibility, the managed device should respond to MSEARCH
        queries searching for Search Target (ST) of "upnp:rootdevice"
        """
        self.sock = sock

    def start(self):
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                self.check(data, addr)

            except socket.timeout:
                continue
        pass

"""
example return payload
HTTP/1.1 200 OK
CACHE-CONTROL:max-age=<seconds, at least 1800>
ST:urn:dmtf-org:service:redfish-rest:1:<minor>
USN:uuid:<UUID of Manager>::urn:dmtf-org:service:redfish-rest:1:<minor>
AL:<URL of Redfish service root>
EXT:
"""

def main(argv=None):
    """
    main program
    """
    hostname = "127.0.0.1"
    port = 8000

    server = RfSDDPServer()

    try:
        server.start()
    except KeyboardInterrupt:
        pass

    print("Shutting down http server")
    sys.stdout.flush()


# the below is only executed if the program is run as a script
if __name__ == "__main__":
    sys.exit(main())
