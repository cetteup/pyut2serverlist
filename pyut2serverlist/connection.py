import socket
import time

from .constants import HEADER_LENGTH
from .exceptions import ConnectionError, TimeoutError
from .logger import logger
from .packet import Packet


class Connection:
    address: str
    port: int
    protocol: int
    timeout: float

    sock: socket.socket
    is_connected: bool

    def __init__(self, address: str, port: int, protocol: socket.SocketKind = socket.SOCK_STREAM, timeout: float = 2.0):
        self.address = address
        self.port = port
        self.protocol = protocol
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

        logger.debug(packet)

    def read(self) -> Packet:
        if not self.is_connected:
            logger.debug('Socket is not connected yet, connecting now')
            self.connect()

        logger.debug('Reading from socket')

        packet = Packet()

        logger.debug('Reading packet header')
        last_received = time.time()
        timed_out = False
        while len(packet.header) < HEADER_LENGTH and not timed_out:
            iteration_buffer = self.read_safe(HEADER_LENGTH - len(packet.header))
            packet.header += iteration_buffer

            # Update timestamp if any data was retrieved during current iteration
            if len(iteration_buffer) > 0:
                last_received = time.time()
            timed_out = time.time() > last_received + self.timeout

        logger.debug(packet.header)

        if timed_out:
            raise TimeoutError('Timed out while reading packet header')

        # Read number of bytes indicated by packet header
        logger.debug('Reading packet body')
        last_received = time.time()
        timed_out = False
        while len(packet.body) < packet.indicated_body_length() and not timed_out:
            iteration_buffer = self.read_safe(packet.indicated_body_length() - len(packet.body))
            packet.body += iteration_buffer

            # Update timestamp if any data was retrieved during current iteration
            if len(iteration_buffer) > 0:
                last_received = time.time()
            timed_out = time.time() > last_received + self.timeout

        logger.debug(packet.body)

        return packet

    def read_safe(self, buflen: int) -> bytes:
        try:
            buffer = self.sock.recv(buflen)
        except socket.timeout:
            raise TimeoutError('Timed out while receiving server data')
        except (socket.error, ConnectionResetError) as e:
            raise ConnectionError(f'Failed to receive data from server ({e})')

        return buffer

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
