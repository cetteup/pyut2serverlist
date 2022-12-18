import struct

from .exceptions import Error


class Buffer:
    data: bytes
    length: int
    index: int

    def __init__(self, data: bytes):
        self.data = data
        self.length = len(data)
        self.index = 0

    def get_buffer(self) -> bytes:
        return self.data[self.index:]

    def read(self, length: int = 1) -> bytes:
        if self.index + length > self.length:
            raise Error('Attempt to read beyond buffer length')

        data = self.data[self.index:self.index + length]
        self.index += length

        return data

    def peek(self, length: int = 1) -> bytes:
        return self.data[self.index:self.index + length]

    def skip(self, length: int = 1) -> None:
        self.index += length

    def read_pascal_bytestring(self, offset: int = 0) -> bytes:
        length = self.read_uchar()
        v = self.read(length)
        return v[:-offset]

    def read_pascal_string(self, offset: int = 0, encoding: str = 'latin1') -> str:
        return self.read_pascal_bytestring(offset).decode(encoding)

    def read_uchar(self) -> int:
        v, *_ = struct.unpack('<B', self.read(1))
        return v

    def read_ushort(self) -> int:
        v, *_ = struct.unpack('<H', self.read(2))
        return v

    def read_uint(self) -> int:
        v, *_ = struct.unpack('<I', self.read(4))
        return v
