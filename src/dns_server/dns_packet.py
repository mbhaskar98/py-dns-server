import struct


class DNSPacket:
    def __init__(self) -> None:
        pass

    def parse_request(self, data: bytes):
        assert len(data) > 12
        header = data[:12]
        payload = data[12:]

        header_bytes = struct.unpack("!6H", header)

        self.id = header_bytes[0]
        self.flags = header_bytes[1]
        self.q_count = header_bytes[2]
        self.ans_count = header_bytes[3]
        self.auth_count = header_bytes[4]
        self.add_count = header_bytes[5]

        self.queries: list[bytes] = []

        for _ in range(self.q_count):
            j = (
                payload.index(0) + 1 + 4
            )  ## domain, 1 bytes null 0x00, 4 bytes for type and class
            self.queries.append(payload[:j])
            payload = payload[j:]
        self.add_records: bytes = payload
