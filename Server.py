from socket import *
import threading
from threading import Thread
import sys
import time


def authenticateUser(self):
    self.conn.send("Username:".encode())
    uname= self.conn.recv(1024).decode()
    print("[Thread - %d] username recd: %s" %(threading.currentThread().ident, str(uname))) 
  
    while (isExists(uname) == False):
        self.conn.send("Username does not exist\nUsername")
        uname= self.conn.recv(1024).decode()
        print("[Thread - %d] username recd: %s" %(threading.currentThread().ident, str(uname))) 

    if(userBlock[uname] != 0):
        elapsedTime = time.time() - userBlock[uname]
        print elapsedTime
        if(float(elapsedTime) < float(blocked_duration)):
            self.conn.send("Your account is blocked due to multiple login failures. Please try again later\n")
            #TODO Disconnect user
            return (uname, False)
        else:
            userBlock[uname] = 0
            userTries[uname] = 0

    #user is not blocked
    self.conn.send("Password:".encode())
    password = self.conn.recv(1024).decode()
    print("[Thread - %d] Password recd: %s" %(threading.currentThread().ident, str(password)))

    while(userTries[uname] < 3):
        userTries[uname] = userTries[uname] + 1
        if(userPass[uname] == password):
            userTries[uname] = 0
            self.conn.send("Credentials authenticated\n")
            return (uname, True)
        elif(userTries[uname] <= 2):
            self.conn.send("Invalid Password\nPassword:")
            password = self.conn.recv(1024).decode()
            print("[Thread - %d] Password recd: %s" %(threading.currentThread().ident, str(password)))
    
    self.conn.send("Invalid Password. Your account has been blocked. Please try again later\n")
    userBlock[uname] =  time.time()
    return (uname, False)

def broadcast(self, message):
    for clientThread in clientThreads:
        if(clientThread.loggedIn == True and clientThread.username != self.username):
            clientThread.conn.send(message.encode())

class ClientThread(Thread):

    def __init__(self,conn,address):
        Thread.__init__(self)
        self.conn = conn
        self.address = address
        self.loggedIn = False
        print ("[Thread - %d] New socket thread started from:%s" %(threading.currentThread().ident, str(address)))


    def run(self):
        while 1:
            if(self.loggedIn == False):
                authResult = authenticateUser(self)
                if(authResult[1] == True):
                    self.username = authResult[0]
                    self.loginTime = time.time()
                    self.loggedIn = True
                    broadcast(self,"{} logged in \n".format(self.username))
                continue
            
            
            command = self.conn.recv(1024).decode()
            commands = command.split()
            if(commands[0] == "broadcast"):
                broadcast(self,"{}: {}\n".format(self.username, commands[1]))
                continue
            elif(commands[0] == "whoelse"):
                for clientThread in clientThreads:
                    if(clientThread.loggedIn == True and clientThread.username != self.username):
                        self.conn.send("{}\n".format(clientThread.username))
                continue
           

        self.conn.close()


#Open file 
creds = open("credentials.txt","r")
credLines = creds.readlines()
creds.close
print("File opened")

#To keep a track of user and tries
userTries = {}
#Usernames with passwords
userPass = {}
#To keep a track of user status (blocked/unblocked)
userBlock = {}
clientInfo = {}
blocked_duration = sys.argv[1]

for userCreds in credLines:
    user = userCreds.split()
    userTries[user[0]] = 0
    userPass[user[0]] = user[1]
    userBlock[user[0]] = 0

#To check if a username exists in database
def isExists(uname):
    for line in credLines:
        user = line.split()
        if(user[0] == uname):
            return True
            break
    return False

clientThreads = []

def server_program():
    # get the hostname
    host = "127.0.0.1"
    print("Host: " +host)
    port = 13005  # initiate port no above 1024

    server_socket = socket(AF_INET, SOCK_STREAM)  # get instance
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.bind((host, port))  
    #Store usernames and ports in a dictionary
    while True:
        server_socket.listen(20)
        conn, address = server_socket.accept()  # accept new connection
        print("Connection from: " + str(address))
        aThread = ClientThread(conn, address)
        aThread.start()
        clientThreads.append(aThread)
           

if __name__ == '__main__':
    server_program()
