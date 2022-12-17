class Error(Exception):
    pass


class ConnectionError(Error):
    pass


class TimeoutError(Error):
    pass


class AuthError(Error):
    pass
