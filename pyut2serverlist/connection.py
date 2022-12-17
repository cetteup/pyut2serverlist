import socket
import time
from typing import Type

from .buffer import Buffer
from .constants import UDP_MAX_DATA_SIZE
from .exceptions import ConnectionError, TimeoutError
from .logger import logger
from .packet import Packet


class Connection:
    address: str
    port: int
    protocol: int
    packet_type: Type[Packet]
    timeout: float

    sock: socket.socket
    is_connected: bool

    def __init__(self, address: str, port: int, protocol: socket.SocketKind, packet_type: Type[Packet], timeout: float):
        self.address = address
        self.port = port
        self.protocol = protocol
        self.packet_type = packet_type
        self.timeout = timeout

        self.is_connected = False

    def connect(self) -> None:
        if self.is_connected:
            return

        self.sock = socket.socket(socket.AF_INET, self.protocol)
        self.sock.settimeout(self.timeout)

        try:
            self.sock.connect((self.address, self.port))
            self.is_connected = True
        except socket.timeout:
            self.is_connected = False
            raise TimeoutError(f'Connection attempt to {self.address}:{self.port} timed out')
        except socket.error as e:
            self.is_connected = False
            raise ConnectionError(f'Failed to connect to {self.address}:{self.port} ({e})')

    def write(self, packet: Packet) -> None:
        if not self.is_connected:
            logger.debug('Socket is not connected yet, connecting now')
            self.connect()

        logger.debug('Writing to socket')

        try:
            self.sock.sendall(bytes(packet))
        except socket.error:
            raise ConnectionError('Failed to send data to server')

        logger.debug(bytes(packet))

    def read(self) -> Packet:
        if not self.is_connected:
            logger.debug('Socket is not connected yet, connecting now')
            self.connect()

        logger.debug('Reading from socket')

        packet = self.packet_type()
        last_received = time.time()
        timed_out = False
        while (packet_buflen := packet.buflen() > 0) and not timed_out:
            # We can read partial data on a TCP connection, but have to read all available data when using UDP
            # (any data left on a UDP socket will be discarded)
            buflen = packet_buflen if self.protocol == socket.SOCK_STREAM else UDP_MAX_DATA_SIZE

            try:
                iteration_buffer = self.read_safe(buflen)
            except TimeoutError:
                """
                Treat as timeout if we
                a) did not receive a complete header
                b) did not receive a complete body of known length
                c) did not receive any body data
                """
                if packet.header_buflen() > 0 or \
                        packet.body_buflen() > 0 and packet.INDICATES_LENGTH or \
                        len(packet.body) == 0:
                    timed_out = True
                break

            # Append whatever data is missing from the head to it
            if (header_buflen := packet.header_buflen()) > 0:
                packet.header += iteration_buffer.read(min(header_buflen, iteration_buffer.length))
                # Log packet header once complete
                if packet.header_buflen() == 0:
                    logger.debug(f'Received header: {packet.header}')

            # Append any remaining data to body
            packet.body += iteration_buffer.get_buffer()

            # Update timestamp if any data was retrieved during current iteration
            if iteration_buffer.length > 0:
                last_received = time.time()
            timed_out = time.time() > last_received + self.timeout

        if timed_out:
            raise TimeoutError('Timed out while receiving server data')

        logger.debug(f'Received body: {packet.body}')

        return packet

    def read_safe(self, buflen: int) -> Buffer:
        try:
            return Buffer(self.sock.recv(buflen))
        except socket.timeout:
            raise TimeoutError('Timed out while receiving server data')
        except (socket.error, ConnectionResetError) as e:
            raise ConnectionError(f'Failed to receive data from server ({e})')

    def __del__(self):
        self.close()

    def close(self) -> bool:
        if hasattr(self, 'sock') and isinstance(self.sock, socket.socket):
            if self.is_connected:
                self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
            self.is_connected = False
            return True

        return False
