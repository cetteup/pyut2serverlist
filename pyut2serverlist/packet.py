import struct


class Packet:
    header: bytes
    body: bytes

    def __init__(self, header: bytes = b'', body: bytes = b''):
        self.header = header
        self.body = body

    @classmethod
    def build(cls, body_data: bytes):
        return cls(struct.pack('<I', len(body_data)), body_data)

    def indicated_body_length(self) -> int:
        """
        Get length of packet body as indicated by header (total indicated length - header length)
        :return: Indicated and expected length of packet body
        """
        length, *_ = struct.unpack('<I', self.header)
        return length

    def data(self) -> bytes:
        """
        Get packet data (body without leading length indicator and trailing \x00 byte)
        """
        return self.body[1:int(self.body[0])]

    def __bytes__(self):
        return self.header + self.body
