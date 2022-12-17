import struct

from .buffer import Buffer
from .constants import UDP_MAX_DATA_SIZE


class Packet:
    header: bytes
    body: bytes

    HEADER_LENGTH: int
    INDICATES_LENGTH: bool

    def __init__(self, header: bytes = b'', body: bytes = b''):
        self.header = header
        self.body = body

    def __bytes__(self):
        return self.header + self.body

    def header_buflen(self) -> int:
        """Number of bytes to read until header is complete"""
        return self.HEADER_LENGTH - len(self.header)

    def body_buflen(self) -> int:
        """Number of bytes to read until body is complete"""
        pass

    def buflen(self) -> int:
        """Number of bytes to read until entire packet is complete"""
        # Remaining body buffer length may be unkown until we have a complete header, so complete that first
        if (header_buflen := self.header_buflen()) > 0:
            return header_buflen

        return self.body_buflen()

    def buffer(self, skip_header: bool = True) -> Buffer:
        buffer = Buffer(self.header + self.body)

        if skip_header:
            buffer.skip(self.HEADER_LENGTH)

        return buffer


class PrincipalPacket(Packet):
    HEADER_LENGTH = 4
    INDICATES_LENGTH = True

    @classmethod
    def build(cls, body_data: bytes):
        return cls(struct.pack('<I', len(body_data)), body_data)

    def body_buflen(self) -> int:
        return self.indicated_body_length() - len(self.body)

    def indicated_body_length(self) -> int:
        """
        Get length of packet body as indicated by header (total indicated length - header length)
        :return: Indicated and expected length of packet body
        """
        length, *_ = struct.unpack('<I', self.header)
        return length


class ServerPacket(Packet):
    HEADER_LENGTH = 5
    INDICATES_LENGTH = False

    @classmethod
    def build(cls, query_type: int, body_data: bytes = b''):
        return cls(b'\x79\x00\x00\x00' + struct.pack('<B', query_type), body_data)

    def body_buflen(self) -> int:
        # Max UDP packet data size minus header length
        return UDP_MAX_DATA_SIZE - self.HEADER_LENGTH
