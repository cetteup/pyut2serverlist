import socket
from dataclasses import dataclass
from enum import IntEnum
from typing import List

from .buffer import Buffer
from .connection import Connection
from .packet import ServerPacket
from .utils import read_unreal_string


class ServerQueryType(IntEnum):
    INFO = 0


@dataclass
class ServerInfo:
    id: int
    ip: str
    game_port: int
    query_port: int
    name: str
    map: str
    game_type: str
    num_players: int
    max_players: int


class Server:
    ip: str
    query_port: int
    game_port: int

    def __init__(self, ip: str, query_port: int, game_port: int = -1):
        self.ip = ip
        self.query_port = query_port
        self.game_port = game_port

    def __iter__(self):
        yield 'ip', self.ip
        yield 'query_port', self.query_port
        yield 'game_port', self.game_port

    def get_info(self, timeout: float = 1.0, strip_colors: bool = True):
        buffer, *_ = self.query(ServerQueryType.INFO, timeout=timeout)
        """
        Packet structure should be
        server id (uint, 4 bytes)
        server ip (str, n bytes, usually 1 byte because it's empty)
        game port (uint, 4 bytes)
        query port (uint, 4 bytes, usually 0)
        server name (str, n bytes)
        map name (str, n bytes)
        game type (str, n bytes)
        current players (uint, 4 bytes)
        max players (uint, 4 bytes)
        ...
        """
        info = ServerInfo(
            id=buffer.read_uint(),
            ip=buffer.read_pascal_string(1),
            game_port=buffer.read_uint(),
            query_port=buffer.read_uint(),
            name=read_unreal_string(buffer, strip_colors=strip_colors),
            map=read_unreal_string(buffer, strip_colors=strip_colors),
            game_type=read_unreal_string(buffer, strip_colors=strip_colors),
            num_players=buffer.read_uint(),
            max_players=buffer.read_uint()
        )

        # Update game port if unknown
        if self.game_port == -1:
            self.game_port = info.game_port

        return info

    def query(self, *args: ServerQueryType, timeout: float) -> List[Buffer]:
        connection = Connection(self.ip, self.query_port, socket.SOCK_DGRAM, ServerPacket, timeout=timeout)

        buffers = []
        for query_type in args:
            query = ServerPacket.build(query_type)
            connection.write(query)
            buffers.append(connection.read().buffer())

        del connection

        return buffers
