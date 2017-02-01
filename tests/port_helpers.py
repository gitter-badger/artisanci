import socket

__all__ = [
    'find_unused_port',
    'bind_port'
]


def find_unused_port(family=socket.AF_INET, socktype=socket.SOCK_STREAM):
    tempsock = socket.socket(family, socktype)
    port = bind_port(tempsock)
    tempsock.close()
    del tempsock
    return port


def bind_port(sock, host='127.0.0.1'):
    if sock.family == socket.AF_INET and sock.type == socket.SOCK_STREAM:
        if hasattr(socket, 'SO_REUSEADDR'):
            if sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR) == 1:
                raise ValueError('tests should never set the SO_REUSEADDR '
                                 'socket option on TCP/IP sockets!')
        if hasattr(socket, 'SO_REUSEPORT'):
            if sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT) == 1:
                raise ValueError('tests should never set the SO_REUSEPORT '
                                 'socket option on TCP/IP sockets!')
        if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)

    sock.bind((host, 0))
    port = sock.getsockname()[1]
    return port
