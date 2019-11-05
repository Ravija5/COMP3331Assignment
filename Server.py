#coding: utf-8
#Python version - 2.7.10
import sys
from socket import *
import time

serverPort = 12004
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('localhost', serverPort))
serverSocket.listen(1)

print "The server is ready to receive"

#Open file 
creds = open("credentials.txt","r")
credLines = creds.readlines()
creds.close

#To keep a track of user and tries
userTries = {}
#Usernames with passwords
userPass = {}
#To keep a track of user status (blocked/unblocked)
userStatus = {}
blocked_duration = sys.argv[1]

for userCreds in credLines:
    user = userCreds.split()
    userTries[user[0]] = 0
    userPass[user[0]] = user[1]
    userStatus[user[0]] = 0

#To check if a username exists in database
def isExists(uname):
    for line in credLines:
        user = line.split()
        if(user[0] == uname):
            return True
            break
    return False
    
def authenticateUser():
    uname = connectionSocket.recv(1024)
    password = connectionSocket.recv(1024)

    if(isExists(uname) == False):
        connectionSocket.send("Username does not exist")
        return
    
    if(userStatus[uname] == 0):
        #User is not blocked
        userTries[uname] = userTries[uname] + 1
        if(userPass[uname] == password):
            userTries[uname] = 0
            connectionSocket.send("Credentials authenticated")
        else:
            if (userTries[uname] == 3):
                #Block user
                connectionSocket.send("Invalid Password. Your account has been blocked. Please try again later")
                userStatus[uname] =  time.time()
                return
            connectionSocket.send("Password incorrect")
    else:
        #User still blocked
        elapsedTime = time.time() - userStatus[uname]
        print userStatus
        print ("Elapsed time = ", elapsedTime)
        print ("Blocked duration = ", blocked_duration)
        if(float(elapsedTime) > float(blocked_duration)):
            #Unblocked
            print("Unblocked now")
            userStatus[uname] = 0
            if(userPass[uname] == password):
                userTries[uname] = 0
                connectionSocket.send("Credentials authenticated")
            else:
                connectionSocket.send("Password incorrect")
        else:
            connectionSocket.send(">Your account is blocked due to multiple login failures. Please try again later")
            print("User still blocked")
while 1:
    connectionSocket, addr = serverSocket.accept()
    try:
        while 1:
            authenticateUser()
           
    except IOError:
        connectionSocket.send('there was some issue with connection try again\n\n')
    finally:
        
        connectionSocket.close()