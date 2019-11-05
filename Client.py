#coding: utf-8
#Python version - 2.7.10
from socket import *

serverName = 'localhost'
serverPort = 12004
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

#Global Declarations
isLogged = False

def login():
    isReceived = "Password incorrect"
    uname = raw_input('Username:')
    i = 0
    
    while (i < 3 and isReceived == "Password incorrect"):
        clientSocket.send(uname)
        password = raw_input('Password:')
        clientSocket.send(password)
        isReceived = clientSocket.recv(1024)

        if isReceived == "Credentials authenticated":
            print("Welcome to the greatest messaging application ever!")
            return True
        elif isReceived == "Password incorrect":
            print ("Invalid Password. Please try again")
        i = i + 1
    print(isReceived)
    return False

while 1:
    while isLogged == False:
        isLogged = login()
  
