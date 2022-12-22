import struct

from .exceptions import Error


class Buffer:
    data: bytes
    length: int
    index: int

    def __init__(self, data: bytes = b''):
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
        length = self.read_compact_int()
        # At least one server returns a seemingly incorrectly built length indicator,
        # equal to negative half the real value
        if length < 0:
            length *= -2
        v = self.read(length)
        return v[:-offset]

    def read_pascal_string(self, offset: int = 0, encoding: str = 'latin1') -> str:
        return self.read_pascal_bytestring(offset).decode(encoding, errors='replace')

    def read_uchar(self) -> int:
        v, *_ = struct.unpack('<B', self.read(1))
        return v

    def read_ushort(self) -> int:
        v, *_ = struct.unpack('<H', self.read(2))
        return v

    def read_uint(self) -> int:
        v, *_ = struct.unpack('<I', self.read(4))
        return v

    def read_compact_int(self) -> int:
        # https://wiki.beyondunreal.com/Legacy:Package_File_Format/Data_Details#Index.2FCompactIndex_values
        v = 0
        signed = False
        for i in range(0, 5):
            x = self.read_uchar()
            if i == 0:
                if (x & 0x80) > 0:
                    signed = True
                v |= x & 0x3f
                if (x & 0x40) == 0:
                    break
            elif i == 4:
                v |= (x & 0x1f) << (6 + (3 * 7))
            else:
                v |= (x & 0x7f) << (6 + ((i - 1) * 7))
                if (x & 0x80) == 0:
                    break

        if signed:
            v *= -1

        return v

    def write(self, v: bytes) -> None:
        self.data += v
        self.length += len(v)

    def write_pascal_bytestring(self, v: bytes) -> None:
        v += b'\x00'
        self.write_compact_int(len(v))
        self.write(v)

    def write_pascal_string(self, v: str, encoding: str = 'latin1') -> None:
        self.write_pascal_bytestring(v.encode(encoding))

    def write_uchar(self, v: int) -> None:
        self.write(struct.pack('<B', v))

    def write_ushort(self, v: int) -> None:
        self.write(struct.pack('<H', v))

    def write_uint(self, v: int) -> None:
        self.write(struct.pack('<I', v))

    def write_compact_int(self, v: int) -> None:
        v_abs = abs(v)
        for i in range(0, 5):
            x = 0
            last = False
            if i == 0:
                if v < 0:
                    x |= 0x80
                x |= (v_abs & 0x3f)
                if v_abs >= 0x40:
                    x |= 0x40
                else:
                    last = True
            elif i == 4:
                v_abs >>= 7
                x |= (v_abs & 0x1f)
            else:
                v_abs >>= min(6 + (i - 1), 7)
                x |= (v_abs & 0x7f)
                if v_abs >= 0x80:
                    x |= 0x80
                else:
                    last = True

            self.write_uchar(x)

            if last:
                break
