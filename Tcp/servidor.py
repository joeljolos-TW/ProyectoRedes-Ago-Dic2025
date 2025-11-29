import socket
import threading

# Configuración del servidor
HOST = '127.0.0.1' # localhost - solo acepta conexiones locales
PORT = 55555 # Puerto donde el servidor recibirá peticiones

# Crear el socket del servidor
# AF_INET indica que usaremos IPv4
# SOCK_STREAM indica que usaremos TCP
server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Se vincula el host y puerto al socket
server.bind((HOST, PORT))

# El servidor comienza a escuchar conexiones entrantes 
# si se agrega un parametro numerico a la funcion, inicara la cola de conexiones
# si se agrega un parametro de caracteres, dara error
# el valor por defecto depende del sistema operativo (Windows tiene un valor variable, linux mint posee 128)
server.listen()

clients= []
nicknames= []

def broadcast(message):
    """Envía un mensaje a todos los clientes conectados excepto al remitente."""
    for client in clients:
        client.send(message)

def handle(client):
    """Maneja la comunicación con un cliente específico."""
    while True:
        try:
            # Recibe mensajes del cliente
            message = client.recv(1024)
            broadcast(message)
        except:
            # Si ocurre un error, elimina al cliente
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} se ha desconectado.'.encode('ascii'))
            nicknames.remove(nickname)
            break

def receive():
    """Acepta nuevas conexiones de clientes."""
    while True:
        # Acepta una nueva conexión
        client, address = server.accept()
        print(f'Conectado con {str(address)}')

        # Solicita y almacena el apodo del cliente
        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')
        nicknames.append(nickname)
        clients.append(client)

        print(f'El apodo del cliente es {nickname}')
        broadcast(f'{nickname} se ha unido al chat!'.encode('ascii'))
        client.send('Conectado al servidor!'.encode('ascii'))

        # Inicia un hilo para manejar la comunicación con el cliente
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print(f'Servidor escuchando en {HOST}:{PORT}')
receive()