from socket import *


def client_program():
    host = "127.0.0.1"
    port = 13003  # socket server port number
    isLogged = False

    client_socket = socket(AF_INET, SOCK_STREAM)  # instantiate
    client_socket.connect((host, port))  # connect to the server

    print("Client starting...")

    while 1:
        data = client_socket.recv(1024).decode()
        print (data),
        message = raw_input()
        client_socket.send(message.encode())
    
    client_socket.close()  # close the connection


if __name__ == '__main__':
    client_program()