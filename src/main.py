import argparse
from dns_server.dns_server import DNSServer


parser = argparse.ArgumentParser()

parser.add_argument(
    "--address",
    "-a",
    help="IP address on which dns server will run",
    type=str,
    required=False,
    default="127.0.0.1",
)

parser.add_argument(
    "--port",
    "-p",
    help="Port to be used by dns server",
    type=int,
    required=False,
    default=53,
)


parser.add_argument(
    "--name_servers",
    "-n",
    help="List of self.name_servers present on the machine",
    nargs="+",
    required=False,
    # default=["192.168.1.1"],
)


def main():
    args = parser.parse_args()
    dns_server = DNSServer(
        address=args.address, port=args.port, name_servers=args.name_servers
    )
    dns_server.listen_and_serve()


if __name__ == "__main__":
    main()
