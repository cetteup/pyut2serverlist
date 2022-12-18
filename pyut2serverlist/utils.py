import re
import struct

from .buffer import Buffer

COLOR_REGEX = re.compile('\x1b...|[\x00-\x1a]')


def pack(data: bytes) -> bytes:
    """Pack a byte-length-prefixed string"""
    data += b'\x00'
    return chr(min(255, len(data))).encode() + data


def int_to_ip(packed: int) -> str:
    """Converts packed int into IP address string"""
    return "%d.%d.%d.%d" % struct.unpack("<BBBB", struct.pack("<I", packed))


def read_unreal_string(buffer: Buffer, strip_colors: bool = False) -> str:
    length = buffer.read_uchar()
    encoding = 'latin1'
    # See https://github.com/gamedig/node-gamedig/blob/70ec2a45a793b95ff4cfb00257f806fe4ea77afe/protocols/unreal2.js#L97
    if length >= 0x80:
        length = (length & 0x7f) * 2
        encoding = 'utf16'

        if buffer.peek(1) == 1:
            buffer.read(1)

    v = buffer.read(length)
    out = v.decode(encoding, errors='replace')

    if out[-1:] == chr(0):
        out = out[:-1]

    if strip_colors:
        out = COLOR_REGEX.sub('', out)

    return out
