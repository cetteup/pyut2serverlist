import re
import struct

from .buffer import Buffer

COLOR_REGEX = re.compile('\x1b...|[\x00-\x1a]')


def int_to_ip(packed: int) -> str:
    """Converts packed int into IP address string"""
    return "%d.%d.%d.%d" % struct.unpack("<BBBB", struct.pack("<I", packed))


def read_unreal_string(buffer: Buffer, strip_colors: bool = False) -> str:
    out = buffer.read_pascal_string(1)
    if strip_colors:
        out = COLOR_REGEX.sub('', out)

    return out
