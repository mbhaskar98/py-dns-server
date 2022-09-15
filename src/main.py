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


def main():
    args = parser.parse_args()
    dns_server = DNSServer(address=args.address, port=args.port)
    dns_server.listen_and_serve()


if __name__ == "__main__":
    main()
