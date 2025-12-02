import socket
import threading
import sys
import config 

nickname = input("Elige un apodo: ")

client = socket.socket(socket.AF_INET, config.SOCKET_TYPE)

if config.USE_TCP:
    try:
        client.connect((config.HOST, config.PORT))
    except:
        print("No se pudo conectar al servidor.")
        sys.exit()

def receive():
    while True:
        try:
            if config.USE_TCP:

                message = client.recv(config.BUFSIZE).decode('utf-8')
                
                if message == 'NICK':
                    client.send(nickname.encode('utf-8'))
                    continue
                elif message.startswith('REFUSED'):
                    print(f"Conexion rechazada: {message}")
                    client.close()
                    sys.exit() 
            else:
                data, _ = client.recvfrom(config.BUFSIZE)

                message = data.decode('utf-8')
                if message.startswith('REFUSED'):
                    print(f"Error: {message}")
                    sys.exit()

            print(message)
        except:
            print("Ocurrio un error o se cerro la conexion.")
            client.close()
            break

def write():
    if not config.USE_TCP:

        client.sendto(f"JOIN:{nickname}".encode('utf-8'), (config.HOST, config.PORT))

    while True:
        try:
            text = input("")
            if config.USE_TCP:

                client.send(text.encode('utf-8'))
            else:

                client.sendto(text.encode('utf-8'), (config.HOST, config.PORT))
        except:
            break

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()