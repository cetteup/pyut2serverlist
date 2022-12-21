import unittest
from dataclasses import dataclass
from typing import List

from pyut2serverlist.buffer import Buffer


class BufferTest(unittest.TestCase):
    def test_read_compact_int(self):
        @dataclass
        class ReadCompactIntTestCase:
            name: str
            data: bytes
            expected: int

        tests: List[ReadCompactIntTestCase] = [
            ReadCompactIntTestCase(
                name='reads negative 5 byte int',
                data=b'\xff\xff\xff\xff\x1f',
                expected=-(pow(2, 32) - 1),
            ),
            ReadCompactIntTestCase(
                name='reads negative 4 byte int',
                data=b'\xff\xff\xff\x7f',
                expected=-(pow(2, 27) - 1),
            ),
            ReadCompactIntTestCase(
                name='reads negative 3 byte int',
                data=b'\xff\xff\x7f',
                expected=-(pow(2, 20) - 1),
            ),
            ReadCompactIntTestCase(
                name='reads negative 2 byte int',
                data=b'\xff\x7f',
                expected=-(pow(2, 13) - 1),
            ),
            ReadCompactIntTestCase(
                name='reads negative 1 byte int',
                data=b'\xbf',
                expected=-(pow(2, 6) - 1),
            ),
            ReadCompactIntTestCase(
                name='reads zero',
                data=b'\x00',
                expected=0,
            ),
            ReadCompactIntTestCase(
                name='reads positive 1 byte int',
                data=b'?',
                expected=pow(2, 6) - 1,
            ),
            ReadCompactIntTestCase(
                name='reads positive 2 byte int',
                data=b'\x7f\x7f',
                expected=pow(2, 13) - 1,
            ),
            ReadCompactIntTestCase(
                name='reads positive 3 byte int',
                data=b'\x7f\xff\x7f',
                expected=pow(2, 20) - 1,
            ),
            ReadCompactIntTestCase(
                name='reads positive 4 byte int',
                data=b'\x7f\xff\xff\x7f',
                expected=pow(2, 27) - 1,
            ),
            ReadCompactIntTestCase(
                name='reads positive 5 byte int',
                data=b'\x7f\xff\xff\xff\x1f',
                expected=pow(2, 32) - 1,
            )
        ]

        for t in tests:
            # GIVEN
            buffer = Buffer(t.data)

            # WHEN
            actual = buffer.read_compact_int()

            # THEN
            self.assertEqual(t.expected, actual, f'"{t.name}" failed\nexpected: {t.expected}\nactual: {actual}')

    def test_write_compact_int(self):
        @dataclass
        class WriteCompactIntTestCase:
            name: str
            value: int
            expected: bytes

        tests: List[WriteCompactIntTestCase] = [
            WriteCompactIntTestCase(
                name='writes negative 5 byte int',
                value=-(pow(2, 32) - 1),
                expected=b'\xff\xff\xff\xff\x1f',
            ),
            WriteCompactIntTestCase(
                name='writes negative 4 byte int',
                value=-(pow(2, 27) - 1),
                expected=b'\xff\xff\xff\x7f',
            ),
            WriteCompactIntTestCase(
                name='writes negative 3 byte int',
                value=-(pow(2, 20) - 1),
                expected=b'\xff\xff\x7f',
            ),
            WriteCompactIntTestCase(
                name='writes negative 2 byte int',
                value=-(pow(2, 13) - 1),
                expected=b'\xff\x7f',
            ),
            WriteCompactIntTestCase(
                name='writes negative 1 byte int',
                value=-(pow(2, 6) - 1),
                expected=b'\xbf',
            ),
            WriteCompactIntTestCase(
                name='writes zero',
                value=0,
                expected=b'\x00',
            ),
            WriteCompactIntTestCase(
                name='writes positive 1 byte int',
                value=pow(2, 6) - 1,
                expected=b'?',
            ),
            WriteCompactIntTestCase(
                name='writes positive 2 byte int',
                value=pow(2, 13) - 1,
                expected=b'\x7f\x7f',
            ),
            WriteCompactIntTestCase(
                name='writes positive 3 byte int',
                value=pow(2, 20) - 1,
                expected=b'\x7f\xff\x7f',
            ),
            WriteCompactIntTestCase(
                name='writes positive 4 byte int',
                value=pow(2, 27) - 1,
                expected=b'\x7f\xff\xff\x7f',
            ),
            WriteCompactIntTestCase(
                name='writes positive 5 byte int',
                value=pow(2, 32) - 1,
                expected=b'\x7f\xff\xff\xff\x1f',
            )
        ]

        for t in tests:
            # GIVEN
            buffer = Buffer()

            # WHEN
            buffer.write_compact_int(t.value)

            # THEN
            self.assertEqual(
                t.expected,
                buffer.get_buffer(),
                f'"{t.name}" failed\nexpected: {t.expected}\nactual: {buffer.get_buffer()}'
            )


if __name__ == '__main__':
    unittest.main()
