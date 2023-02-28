from dataclasses import dataclass
from enum import IntEnum

from .buffer import Buffer


class Comparator(IntEnum):
    Equals = 0
    NotEquals = 1
    LessThan = 2
    LessThanEquals = 3
    GreaterThan = 4
    GreaterThanEquals = 5
    Disabled = 6


@dataclass
class Filter:
    field: str
    comparator: Comparator
    value: str

    def __bytes__(self) -> bytes:
        buffer = Buffer()
        buffer.write_pascal_string(self.field)
        buffer.write_pascal_string(self.value)
        buffer.write_uchar(self.comparator)
        return buffer.get_buffer()

