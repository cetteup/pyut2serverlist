class Server:
    ip: str
    game_port: int
    query_port: int

    def __init__(self, ip: str, game_port: int, query_port: int):
        self.ip = ip
        self.game_port = game_port
        self.query_port = query_port

    def __iter__(self):
        yield 'ip', self.ip
        yield 'game_port', self.game_port
        yield 'query_port', self.query_port
