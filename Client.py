from socket import *
import select
import sys

def prompt():
    sys.stdout.write(">")
    sys.stdout.flush()
    
def client_program():
    host = "127.0.0.1"
    port = 13005  # socket server port number
    isLogged = False

    client_socket = socket(AF_INET, SOCK_STREAM)  # instantiate
    client_socket.connect((host, port))  # connect to the server
    client_socket.setblocking(False)

    print("Client starting...")

    while 1:
        socket_list = [sys.stdin, client_socket]
        read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
    
        for sock in read_sockets:
            if sock == client_socket:
                data = client_socket.recv(1024).decode()
                print (data),
                prompt()
            else:
                message = raw_input()
                client_socket.send(message.encode())
                prompt()
    
    client_socket.close()  # close the connection


if __name__ == '__main__':
    client_program()