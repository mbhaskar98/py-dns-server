import os
import socket
import _thread
import subprocess
import dns.resolver, dns.rdatatype, dns.rdataclass
from dns_server.dns_packet import DNSPacket
from dns_server.dns_response import DNSResponse


class DNSServer:
    def __init__(self, address: str = "127.0.0.1", port: int = 53) -> None:
        self.__udp_socet = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__address = address
        self.__port = int(port)
        self.__local_resolver: dns.resolver.Resolver = dns.resolver.Resolver()
        self.__networksetup_binary_location = "/usr/sbin/networksetup"

    def listen_and_serve(self):
        try:
            self.__udp_socet.bind((self.__address, self.__port))
            print(f"Dns server started on {self.__address}:{self.__port}")
            self.serve()
        except Exception as e:
            print(f"Cannont listen on:{self.__address}:{self.__port}, err:", e)

    def serve(self):
        print("########## Serving requests ##########")
        try:
            self.add_dns_servers_to_network_interfaces()
            while 1:
                data, addr = self.__udp_socet.recvfrom(1024)
                _thread.start_new_thread(
                    self.build_response_and_send_back,
                    (data, addr),
                )

        except KeyboardInterrupt:
            print("\nExiting!!!!!!!!")
            self.__udp_socet.close()
            self.reset_dns_servers_for_network_interfaces()
            os.abort()
        except Exception as e:
            print("\nError: %s" % e)
        finally:
            self.reset_dns_servers_for_network_interfaces()
            self.serve()

    def build_response_and_send_back(self, data: bytes, addr):
        try:

            dns_packet: DNSPacket = DNSPacket()
            dns_packet.parse_request(data=data)

            res = DNSResponse(local_resolver=self.__local_resolver).build_response(
                dns_packet=dns_packet
            )
            # res = self.build_response(dns_packet)

            self.__udp_socet.sendto(res, addr)
        except Exception as e:
            print(f"For domain:{dns_packet.queries} err:{e}")

    def add_dns_servers_to_network_interfaces(self):

        print(f"Changing dns server for interfaces to {self.__address}")
        interface_list = self.get_network_interfaces_list()
        for interface in interface_list:
            self.set_dns_server_for_interface(
                interface=interface,
                dns_server=self.__address,
            )

    def reset_dns_servers_for_network_interfaces(self):
        print(f"Resetting dns server of the interfaces")
        interface_list = self.get_network_interfaces_list()
        for interface in interface_list:
            self.set_dns_server_for_interface(
                interface=interface,
                dns_server="empty",
            )

    def set_dns_server_for_interface(self, interface: str, dns_server: str):
        ret = subprocess.run(
            [
                self.__networksetup_binary_location,
                "-setdnsservers",
                interface,
                dns_server,
            ]
        )
        print(f"Interface:{interface}, dns_server:{dns_server}, result:{ret}")

    def get_network_interfaces_list(self):
        cmd = f"{self.__networksetup_binary_location} -listallnetworkservices"
        result = (
            subprocess.check_output(cmd, shell=True).decode("UTF-8").splitlines()[1:]
        )
        return result
