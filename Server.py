#coding: utf-8
from socket import *

serverPort = 12003
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('localhost', serverPort))
serverSocket.listen(1)

print "The server is ready to receive"

#Open file 
creds = open("credentials.txt","r")
credLines = creds.readlines()
creds.close

#Initialize dictionary
userTries = {}
for userCreds in credLines:
    user = userCreds.split()
    userTries[user[0]] = 0
    
def authenticateUser():
    uname = connectionSocket.recv(1024)
    password = connectionSocket.recv(1024)
    found = False
    for line in credLines:
        user = line.split()

        if user[0] == uname:
            found = True
            userTries[uname] = userTries[uname] + 1
            print userTries
            if(user[1] == password):
                connectionSocket.send("Credentials authenticated")
                break
            else:
                connectionSocket.send("Password incorrect")
                if (userTries[uname] == 3):
                    print("User blocked for timeout duration")
                    

    if found == False:
        connectionSocket.send("Username does not exist in the database\n")

while 1:
    connectionSocket, addr = serverSocket.accept()
    try:
        while 1:
            authenticateUser()
           
    except IOError:
        connectionSocket.send('there was some issue with connection try again\n\n')
    finally:
        connectionSocket.close()