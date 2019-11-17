from random import randint
from socket import *
import select
import sys
from threading import Thread

showPrompt = False
p2p_list = []
HOST = "127.0.0.1"


def prompt():
    if (showPrompt == True):
        sys.stdout.write(">")
        sys.stdout.flush()
    else:
        sys.stdout.write("")
        sys.stdout.flush()


class P2P_Thread(Thread):
    def __init__(self, my_socket, username, ip, port, starts_socket):
        Thread.__init__(self)
        self.my_socket = my_socket
        self.username = username
        self.ip = ip
        self.port = port
        self.starts_socket = starts_socket

        self.daemon = True
        # self.socketStatus = False
        self.byeFlag = False

    def run(self):
        if self.starts_socket:
            print("Waiting for connection...")
            client_socket, addr = self.my_socket.accept()  # Establish connection with client.
            self.client_socket = client_socket
            self.addr = addr
            self.sending_socket = client_socket
            print("P2P establisbed with {}".format(self.username))
            eventloop(self.client_socket)
            terminateBoth(self.my_socket, self.client_socket)
        else:
            print("Connecting to Peer...")
            self.my_socket.connect((self.ip, int(self.port)))
            print("P2P establisbed with {}".format(self.username))
            self.sending_socket = self.my_socket
            eventloop(self.my_socket)
            terminate(self.my_socket)
        removeuser(self.username)


def eventloop(client_socket):
    while 1:
        try:
            socket_list = [client_socket]
            read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
        except Exception as ex:
            print("Connection error.")

        for sock in read_sockets:
            if sock == client_socket:
                data = client_socket.recv(1024).decode()
                print(data)
                if (data.startswith("BYE")):
                    client_socket.sendall("BYE".encode())  # Say BYE to remote.
                    print("Disconnecting.")
                    return

                prompt()

def terminateBoth(server_socket, client_socket):
    client_socket.shutdown(1)
    client_socket.close()
    server_socket.close()


def terminate(client_socket):
    try:
        client_socket.shutdown(1)
        client_socket.close()
    except Exception as ex:
        print ("Client socket already closed")


def sendprivatemessage(to, data):
    toP2PThread = None
    for aThread in p2p_list:
        if (aThread.username == to):
            toP2PThread = aThread
            break
    if (toP2PThread == None):
        print("Try `startprivate {}` command first.".format(to))
        return

    toP2PThread.sending_socket.sendall(data.encode())


def removeuser(name):
    toP2PThread = None
    for aThread in p2p_list:
        if (aThread.username == name):
            toP2PThread = aThread
            break

    if (toP2PThread != None):
        p2p_list.remove(toP2PThread)


def sayBye(to):
    sendprivatemessage(to, "BYE")
    removeuser(to)

def disconnectAllP2P():
    for aThread in p2p_list:
        sayBye(aThread.username)

def client_program():
    port = 13007  # socket server port number
    isLogged = False

    client_socket = socket(AF_INET, SOCK_STREAM)  # instantiate
    client_socket.connect((HOST, port))  # connect to the server
    client_socket.setblocking(False)

    print("Client starting...")

    while 1:
        global showPrompt

        socket_list = [sys.stdin, client_socket]
        read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])

        for sock in read_sockets:
            if sock == client_socket:
                data = client_socket.recv(1024).decode()

                print (data),

                if (data.encode() == ("Credentials authenticated\n")):
                    # print("prompt set to true")
                    showPrompt = True

                if (data.startswith("P2PREQUEST")):
                    # P2PREQUEST b a
                    s = socket(AF_INET, SOCK_STREAM)
                    host = ''
                    port = randint(10000, 63000)
                    s.bind((HOST, port))
                    s.listen(2)  # Now wait for client connection.
                    fromuser = data.split()[1]
                    touser = data.split()[2]
                    aThread = P2P_Thread(s, fromuser, None, None, True)
                    p2p_list.append(aThread)
                    aThread.start()
                    # P2PPORT b a 55001
                    message = "P2PPORT {} {} {}".format(fromuser, touser, port)
                    print("Sending message to server: " + message)
                    client_socket.send(message.encode())

                if (data.startswith("P2PACCEPTED")):
                    # P2PACCEPTED b a 127.0.0.1 55001
                    fromuser = data.split()[1]
                    touser = data.split()[2]
                    ip = data.split()[3]
                    port = data.split()[4]
                    s = socket(AF_INET, SOCK_STREAM)
                    print("Socket created")
                    aThread = P2P_Thread(s, touser, ip, port, False)
                    p2p_list.append(aThread)
                    aThread.start()

                if (data.startswith("Bye")):
                    print("Disconnecting")
                    client_socket.close()
                    #Close all P2P
                    disconnectAllP2P()
                    return

                prompt()
            else:
                message = raw_input()
                if (message.startswith("private")):
                    # private a Hello, How are you?
                    parts = message.split(" ", 2)
                    if len(parts) <=2:
                        print("Usage: private <user> <message>")
                    else:
                        to = parts[1]
                        data = parts[2]
                        sendprivatemessage(to, data)
                elif (message.startswith("stopprivate")):
                    # stopprivate a
                    parts = message.split()
                    to = parts[1]
                    sayBye(to)
                else:
                    client_socket.send(message.encode())

                prompt()

    client_socket.close()  # close the connection


if __name__ == '__main__':
    client_program()
