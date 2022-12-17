import struct


def pack(data: bytes) -> bytes:
    """Pack a byte-length-prefixed string"""
    data += b'\x00'
    return chr(min(255, len(data))).encode() + data


def int_to_ip(packed: int) -> str:
    """Converts packed int into IP address string"""
    return "%d.%d.%d.%d" % struct.unpack("<BBBB", struct.pack("<I", packed))
