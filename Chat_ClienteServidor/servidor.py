import socket
import threading
from datetime import datetime
import config 

clients = []    
addresses = []  
nicknames = []  

server = socket.socket(socket.AF_INET, config.SOCKET_TYPE)
server.bind((config.HOST, config.PORT))

if config.USE_TCP:
    server.listen()
    print(f"Servidor TCP iniciado en {config.HOST}:{config.PORT}")
else:
    print(f"Servidor UDP iniciado en {config.HOST}:{config.PORT}")

def get_timestamp():
    return datetime.now().strftime('%d/%m %H:%M')

def broadcast(message, sender_nickname=None):
    if config.USE_TCP:
        for client in clients:
            client.send(message)
    else:
        for addr in addresses:
            server.sendto(message, addr)

def send_private(message, target_nick, sender_nick):
    msg_formatted = f"[PRIVADO de {sender_nick}]: {message}"
    
    if target_nick in nicknames:
        index = nicknames.index(target_nick)
        if config.USE_TCP:

            clients[index].send(msg_formatted.encode('utf-8'))
        else:

            server.sendto(msg_formatted.encode('utf-8'), addresses[index])
    else:
        print(f"Usuario {target_nick} no encontrado.")

def process_message(message_str, sender_nick, sender_addr_or_client):
    timestamp = get_timestamp()
    
    if message_str.startswith('@'):
        parts = message_str.split(' ', 1)
        if len(parts) > 1:
            target_nick = parts[0][1:] 
            content = parts[1]
            send_private(f"({timestamp}) {content}", target_nick, sender_nick)
    else:
        full_msg = f'[{timestamp}] {sender_nick}: {message_str}'
        broadcast(full_msg.encode('utf-8'))

# logica TCP
def handle_tcp(client):
    while True:
        try:
            message = client.recv(config.BUFSIZE)
            if not message: break
            
            index = clients.index(client)
            nick = nicknames[index]
            
            process_message(message.decode('utf-8'), nick, client)
            
        except:
            if client in clients:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                broadcast(f'{nickname} salió del chat.'.encode('utf-8'))
                nicknames.remove(nickname)
            break

def receive_tcp():
    while True:
        client, address = server.accept()
        
        if len(clients) >= config.MAX_CLIENTS:
            client.send("REFUSED: Sala llena".encode('utf-8'))
            client.close()
            continue

        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(config.BUFSIZE).decode('utf-8')
        
        if nickname in nicknames:
            client.send("REFUSED: Nickname en uso".encode('utf-8'))
            client.close()
            continue

        nicknames.append(nickname)
        clients.append(client)

        print(f"Nick: {nickname} | IP: {address}")
        broadcast(f"{nickname} se unió al chat!".encode('utf-8'))
        client.send('Conectado al servidor!'.encode('utf-8'))

        thread = threading.Thread(target=handle_tcp, args=(client,))
        thread.start()

# logica UDP
def receive_udp():
    while True:
        try:
            data, addr = server.recvfrom(config.BUFSIZE)
            decoded_data = data.decode('utf-8')

            if decoded_data.startswith("JOIN:"):
                nickname = decoded_data.split(":")[1]
                
                if len(addresses) >= config.MAX_CLIENTS:
                    server.sendto("REFUSED: Sala llena".encode('utf-8'), addr)
                elif nickname in nicknames:
                    server.sendto("REFUSED: Nickname en uso".encode('utf-8'), addr)
                else:
                    nicknames.append(nickname)
                    addresses.append(addr)
                    print(f"UDP Join: {nickname} desde {addr}")
                    broadcast(f"{nickname} se unió!".encode('utf-8'))
            else:
                if addr in addresses:
                    index = addresses.index(addr)
                    nick = nicknames[index]
                    process_message(decoded_data, nick, addr)
        except Exception as e:
            print(f"Error UDP: {e}")

if __name__ == "__main__":
    if config.USE_TCP:
        receive_tcp()
    else:
        receive_udp()