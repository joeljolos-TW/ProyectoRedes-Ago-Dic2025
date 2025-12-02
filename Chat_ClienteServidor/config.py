import socket 

# config
HOST = '127.0.0.1'
PORT = 55555
MAX_CLIENTS = 5 
BUFSIZE = 1024

# cambio de protocolo
# cambia a false para usar udp y usa true para usar tcp 
USE_TCP = False

# determina el tipo de socket basado en la bandera
SOCKET_TYPE = socket.SOCK_STREAM if USE_TCP else socket.SOCK_DGRAM