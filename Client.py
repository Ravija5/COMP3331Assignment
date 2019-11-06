from socket import *


def client_program():
    # host = socket.gethostname()  # as both code is running on same pc
    host = "127.0.0.1"
    port = 13002  # socket server port number
    isLogged = False

    client_socket = socket(AF_INET, SOCK_STREAM)  # instantiate
    client_socket.connect((host, port))  # connect to the server

    print("Client starting...")

    
    def login(client_socket):
        isReceived = "Password incorrect"
        uname = raw_input('Username:')
        i = 0
        
        while (i < 3 and isReceived == "Password incorrect"):
            client_socket.send(uname)
            password = raw_input('Password:')
            client_socket.send(password)
            isReceived = client_socket.recv(1024)

            if isReceived == "Credentials authenticated":
                print("Welcome to the greatest messaging application ever!")
                return True
            elif isReceived == "Password incorrect":
                print ("Invalid Password. Please try again")
            i = i + 1
        print(isReceived)
        return False

    while isLogged == False:
        isLogged = login(client_socket)
        



    client_socket.close()  # close the connection


if __name__ == '__main__':
    client_program()

#receive string "Username: "
        # data = client_socket.recv(1024)
        # print(data, " ")  # show in terminal
        # uname = raw_input('Username:')
        # client_socket.send(uname)
        # password = raw_input('Password:')
        # client_socket.send(password)
        # #Take in UserName & send
        # message = raw_input()  # again take input
        # client_socket.send(message)  # send message

        # #receive string "Password: "
        # data = client_socket.recv(1024)  # receive response
        # print(data, " ")  # show in terminal
        # #

        # #Take in Password & send
        # message = raw_input()  # again take input
        # client_socket.send(message)  # send message