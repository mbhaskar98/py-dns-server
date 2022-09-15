import os
import socket
import _thread
import dns.resolver, dns.rdatatype, dns.rdataclass
from dns_server.dns_packet import DNSPacket
from dns_server.dns_response import DNSResponse


class DNSServer:
    def __init__(
        self, address: str = "127.0.0.1", port: int = 53, name_servers: list[str] = [""]
    ) -> None:
        self.__udp_socet = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__address = address
        self.__port = int(port)
        self.__local_resolver: dns.resolver.Resolver = dns.resolver.Resolver()
        self.__local_resolver.nameservers = name_servers

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
            while 1:
                data, addr = self.__udp_socet.recvfrom(1024)
                _thread.start_new_thread(
                    self.build_response_and_send_back,
                    (data, addr),
                )

        except KeyboardInterrupt:
            print("\nExiting!!!!!!!!")
            self.__udp_socet.close()
            os.abort()
        except Exception as e:
            print("\nError: %s" % e)
        finally:
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


# #!/usr/bin/env python3

# # This is free and unencumbered software released into the public domain.
# #
# # Anyone is free to copy, modify, publish, use, compile, sell, or
# # distribute this software, either in source code form or as a compiled
# # binary, for any purpose, commercial or non-commercial, and by any
# # means.
# #
# # In jurisdictions that recognize copyright laws, the author or authors
# # of this software dedicate any and all copyright interest in the
# # software to the public domain. We make this dedication for the benefit
# # of the public at large and to the detriment of our heirs and
# # successors. We intend this dedication to be an overt act of
# # relinquishment in perpetuity of all present and future rights to this
# # software under copyright law.
# #
# # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# # EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# # MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# # IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# # OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# # ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# # OTHER DEALINGS IN THE SOFTWARE.
# #
# # For more information, please refer to <http://unlicense.org/>

# """
# dns_server.py:
# Bare bones Python 3 DNS server that answers queries with "no such name".
# """

# __author__    = "Philip Huppert"
# __license__   = "Unlicense"
# __version__   = "1.0"


# import os
# import socket
# import struct
# import traceback


# def parse_query(data:bytes):
#     header = data[:12]
#     payload = data[12:]

#     # parse DNS header
#     tmp = struct.unpack(">6H", header)
#     transaction_id = tmp[0]
#     flags = tmp[1]
#     num_queries = tmp[2]
#     num_answer = tmp[3]
#     num_authority = tmp[4]
#     num_additional = tmp[5]

#     # extract several flags
#     is_query = flags & 0x8000 == 0
#     opcode = flags & 0x7800 >> 11
#     is_truncated = flags & 0x0200 != 0

#     # verify query structure
#     assert num_queries > 0
#     assert num_answer == 0
#     assert num_authority == 0
#     assert is_query
#     assert opcode == 0
#     assert not is_truncated

#     # extract queries
#     queries = []
#     for i in range(num_queries):
#         print(payload.index(0) + 1 + 5)
#         j = payload.index(0) + 1 + 4 ## Find index for 0x00, 1 bytes for 0x00, 4 bytes for type and class
#         queries.append(payload[:j])
#         payload = payload[j:]

#     return transaction_id, queries


# def build_response(transaction_id, queries):
#     # assemble flags
#     flags = 0
#     flags |= 0x8000 # response
#     flags |= 0x0400 # authorative server
#     flags |= 0x0003 # reply: no such name

#     # assembler header
#     header = struct.pack(">6H", transaction_id, flags, len(queries), 0, 0, 0)

#     # build query section
#     payload = b"".join(queries)

#     return header + payload


# def get_domain(query):
#     # extract domain from a query
#     domain = []
#     while True:
#         l = query[0]
#         query = query[1:]
#         if l == 0:
#             break
#         domain.append(query[:l])
#         query = query[l:]
#     domain = [x.decode("ascii") for x in domain]
#     domain = ".".join(domain)
#     return domain


# def main():


#     # listen for UDP datagrams
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     sock.bind(('127.0.0.1', 53))

#     while True:
#         # receive and parse query
#         data, addr = sock.recvfrom(1024)
#         try:
#             transaction_id, queries = parse_query(data)
#         except:
#             traceback.print_exc()
#             continue

#         # answer query
#         resp = build_response(transaction_id, queries)
#         sock.sendto(resp, addr)

#         # print queried domain names
#         for query in queries:
#             domain = get_domain(query)
#             print(domain)


# if __name__ == "__main__":
#     try:
#         main()
#     except KeyboardInterrupt:
#         pass
