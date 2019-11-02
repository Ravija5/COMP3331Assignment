#coding: utf-8
from socket import *

serverName = 'localhost'
serverPort = 12003
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

#Global Declarations
isLogged = False

def login():
    uname = raw_input('USERNAME:')
    clientSocket.send(uname)
    password = raw_input('PASSWORD:')
    clientSocket.send(password)

    isReceived = clientSocket.recv(1024)
    if isReceived == "Credentials authenticated":
        print(isReceived)
        return True
    print(isReceived)
    return False


while 1:
    while isLogged == False:
        isLogged = login()
  
