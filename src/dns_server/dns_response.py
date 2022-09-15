import os
import struct
import dns, dns.rdatatype, dns.rdataclass, dns.resolver, dns.rrset
from dns_server.dns_packet import DNSPacket


class DNSResponse:
    def __init__(self, local_resolver: dns.resolver.Resolver) -> None:
        self.__local_resolver = local_resolver

    def build_response(self, dns_packet: DNSPacket) -> bytes:
        dns_packet.flags = self.set_flags(dns_packet.flags)

        answers_list: list[bytes] = self.get_answers(dns_packet.queries)

        dns_packet.ans_count = len(answers_list)

        response_header = struct.pack(
            ">6H",
            dns_packet.id,
            dns_packet.flags,
            dns_packet.q_count,
            dns_packet.ans_count,
            dns_packet.auth_count,
            dns_packet.add_count,
        )

        answers: bytes = b"".join(answers_list)
        queries: bytes = b"".join(dns_packet.queries)

        response = response_header + queries + answers + dns_packet.add_records

        return response

    def set_flags(self, flags: int) -> int:
        """
        QR = 1
        OPCODE = 0000
        AA = 0
        TC = 0
        RD = 1
        RA = 1
        Z = 0
        RCODE = 0

        """
        flags |= 0x8180
        return flags

    ## TODO: Add support for othet query types
    def get_answers(self, queries: list[bytes]) -> list[bytes]:
        res_answers: list[bytes] = []
        for query in queries:
            domain, q_type, q_class = self.parse_questions(questions=query)
            q_type_int = int.from_bytes(q_type, byteorder="big")
            q_class_int = int.from_bytes(q_class, byteorder="big")

            answers: dns.resolver.Answer = self.__local_resolver.resolve(
                domain,
                rdtype=q_type_int,
                rdclass=q_class_int,
                raise_on_no_answer=False,
                # search=True
            )

            ttl_bytes: int = 0

            if hasattr(answers, "rrset") and hasattr(answers.rrset, "ttl"):
                ttl_bytes: int = answers.rrset.ttl.to_bytes(4, "big")

            answer: dns.rrset.RRset
            for answer in answers.rrset:
                answer_bytes: bytes = self.domain_name_to_bytes(domain=domain)
                try:
                    type_int: int = answer.rdtype.value
                    class_int: int = answer.rdclass.value
                    length_int: int = len(answer.to_wire())

                    fixed_field_bytes: bytes = struct.pack(">2H", type_int, class_int)

                    fixed_field_bytes += ttl_bytes
                    fixed_field_bytes += length_int.to_bytes(2, "big")

                    # result_bytes: bytes = bytes.fromhex(answer.to_text().encode("utf-8").hex())
                    result_bytes: bytes = answer.to_wire()

                    answer_bytes += fixed_field_bytes + result_bytes

                    res_answers.append(answer_bytes)

                    print(
                        f"QRY:{dns.rdatatype.RdataType.to_text(type_int)} TYPE:{dns.rdataclass.RdataClass.to_text(class_int)} Domain:{domain} ---> {answer}"
                    )
                except Exception as e:
                    print(f"Error for {domain}--->{answer.to_text()}: err{e}")

        return res_answers

    def parse_questions(self, questions: bytes) -> tuple[str, bytes, bytes]:
        domain = ""
        q_type = b""
        q_class = b""
        if questions is not None:
            try:
                # extract domain from a query
                domain = []
                temp_questions = questions
                while True:
                    l = temp_questions[0]
                    temp_questions = temp_questions[1:]
                    if l == 0:
                        break
                    domain.append(temp_questions[:l])
                    temp_questions = temp_questions[l:]
                domain = [x.decode("ascii") for x in domain]
                domain = ".".join(domain)

                q_type = temp_questions[:2]

                temp_questions = temp_questions[2:]

                q_class = temp_questions[:2]

            except Exception as e:
                print(f"Error while parsing the query:{questions}, error{e}")
        else:
            print(f"Got empty query:{questions}")

        return domain, q_type, q_class

    def domain_name_to_bytes(self, domain: str) -> bytes:
        # return 0xC00C.to_bytes(2, "big")
        parts: list[str] = domain.split(".")
        if parts[-1] == ".":
            print("trailing . not supported yet")
            os.abort()
        ret = b""
        for part in parts:
            length = len(part)
            ret += length.to_bytes(1, "big")
            for c in part:
                temp = ord(c)
                ret += temp.to_bytes(1, "big")

        ret += (0x00).to_bytes(1, "big")
        return ret
