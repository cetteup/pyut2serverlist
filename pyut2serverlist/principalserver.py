import socket
from enum import Enum
from hashlib import md5
from typing import List

from .buffer import Buffer
from .connection import Connection
from .exceptions import AuthError
from .packet import PrincipalPacket
from .server import Server
from .utils import int_to_ip


class Game(str, Enum):
    UT2003 = 'ut2003'
    UT2004 = 'ut2004'


class PrincipalServer:
    address: str
    port: int
    game: Game
    cd_key: bytes

    connection: Connection
    authenticated: bool

    def __init__(self, address: str, port: int, game: Game, cd_key: str, timeout: float = 2.0):
        self.address = address
        self.port = port
        self.game = game
        self.cd_key = cd_key.encode()
        self.connection = Connection(self.address, self.port, socket.SOCK_STREAM, PrincipalPacket, timeout=timeout)
        self.authenticated = False

    def __enter__(self):
        return self

    def __exit__(self, *excinfo):
        self.connection.close()

    def authenticate(self) -> None:
        challenge = self.connection.read()

        challenge_response = self.build_challenge_response_packet(
            self.game,
            self.cd_key,
            challenge.buffer().read_pascal_bytestring(1)
        )
        self.connection.write(challenge_response)

        approval = self.connection.read()
        if (approval_result := approval.buffer().read_pascal_string(1)) != 'APPROVED':
            raise AuthError(f'Authentication failed: {approval_result}')

        if self.game is Game.UT2003:
            return

        self.connection.write(self.build_verification_packet())

        verification = self.connection.read()
        if (verification_result := verification.buffer().read_pascal_string(1)) != 'VERIFIED':
            raise AuthError(f'Authentication failed: {verification_result}')

        self.authenticated = True

    def get_servers(self) -> List[Server]:
        if not self.authenticated:
            self.authenticate()

        # TODO Implement filters
        # Just get all servers with a non-empty gametype for now (should be all servers)
        query_packet = PrincipalPacket.build(b'\x00\x01\tgametype\x00\x01\x00\x04')
        self.connection.write(query_packet)

        result = self.connection.read()
        num_servers = result.buffer().read_uint()

        servers = []
        for _ in range(num_servers):
            server_packet = self.connection.read()
            buffer = server_packet.buffer()
            packed_ip, game_port, query_port = buffer.read_uint(), buffer.read_ushort(), buffer.read_ushort()
            servers.append(Server(int_to_ip(packed_ip), query_port, game_port))

        return servers

    @staticmethod
    def build_challenge_response_packet(game: Game, cd_key: bytes, challenge: bytes) -> PrincipalPacket:
        cd_key_hash = md5(cd_key).hexdigest()
        challenge_response_hash = md5(cd_key + challenge).hexdigest()

        if game is Game.UT2003:
            client, version = 'CLIENT', 2225
        else:
            client, version = 'UT2K4CLIENT', 3369

        buffer = Buffer()
        buffer.write_pascal_string(cd_key_hash)
        buffer.write_pascal_string(challenge_response_hash)
        buffer.write_pascal_string(client)
        buffer.write_uint(version)  # game version
        buffer.write_uchar(5)  # OS
        buffer.write_pascal_string('int')  # language

        if game is Game.UT2004:
            buffer.write_uint(2606)  # gpu device id
            buffer.write_uint(32902)  # gpu vendor id
            buffer.write_uint(20)  # cpu speed
            buffer.write_uchar(0)  # cpu type

        return PrincipalPacket.build(buffer.data)

    @staticmethod
    def build_verification_packet() -> PrincipalPacket:
        buffer = Buffer()
        buffer.write_pascal_string('0014e800000000000000000000000000')
        return PrincipalPacket.build(buffer.data)
