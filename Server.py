from socket import *
import threading
from threading import Thread
import sys
import time

    
def disconnectUser(self):
    print ("In disconnect: {} ".format(self.username))
    self.conn.send("Bye".encode())
    self.socketStatus = False
    self.conn.close()

def authenticateUser(self):
    self.conn.send("Username:".encode())
    uname= self.conn.recv(1024).decode()
    print("[Thread - %d] username recd: %s" %(threading.currentThread().ident, str(uname))) 
  
    while (isExists(uname) == False):
        self.conn.send("Username does not exist\nUsername")
        uname= self.conn.recv(1024).decode()
        print("[Thread - %d] username recd: %s" %(threading.currentThread().ident, str(uname))) 

    self.username = uname
    if(userBlock[uname] != 0):
        elapsedTime = time.time() - userBlock[uname]
        print elapsedTime
        if(float(elapsedTime) < float(blocked_duration)):
            self.conn.send("Your account is blocked due to multiple login failures. Please try again later\n")
            #TODO Disconnect user
            disconnectUser(self)
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
            self.conn.send("Credentials authenticated\n".encode())
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

def blockFrom(self, username):
    print("Checkking for : {}".format(username))
    if(isExists(username) == False):
        self.conn.send("User does not exist in credentials\n".encode())
        return

    if( username == self.username ):
        self.conn.send("Cannot block self\n".encode())
        return 

    #Hans said -> Block yoda => yoda has hansi n his blocked form list => output is: blocked yoda
    for clientThread in clientThreads:
        #Proabbly an encoding decoding issue
        
        if((clientThread.username == username)):      
            print(clientThread.username)
            print(username)      
            if (self.username not in clientThread.blockedFrom):
                clientThread.blockedFrom.append(self.username.encode())
                #print (clientThread.blockedFrom)
            else:
                self.conn.send("User is already blocked\n".encode())
                return
            break
            
    self.conn.send("Blocked {}\n".format(username))

def unblockFrom(self, username):
    if(isExists(username) == False):
        self.conn.send("User does not exist in credentials\n".encode())
        return 
        
    if( username == self.username ):
        self.conn.send("Cannot unblock self\n".encode())
        return 

    #hans says unblock yoda => remove hans from yoda's block from list
    for clientThread in clientThreads:
         if(clientThread.username == username):
            try:
                clientThread.blockedFrom.remove(self.username)
                print (clientThread.blockedFrom)
                break
            except ValueError:
                self.conn.send("User is already unblocked. No action required\n".encode())

    self.conn.send("Unblocked {}\n".format(username))

def whoelsesince(self, givenTime):
    print ("In whoelse since")
    lastOnline = []
    for clientThread in clientThreads:
        if(clientThread.loggedIn == True and clientThread.username != self.username):
            elapsedTime = time.time() - clientThread.loginTime 
            print (elapsedTime)
            if(elapsedTime < givenTime):
                lastOnline.append(clientThread)

    return lastOnline

def sendOfflineMessages(self):
    if(len(self.offlineMsgs) == 0):
        self.conn.send("You received no offline messages\n".encode())
        return

    self.conn.send("Your offline messages are:\n".encode())
    for msg in self.offlineMsgs:
        self.conn.send("{}\n".format(msg))

def messageUser(self, username, message):
    if(isExists(username) == False):
        self.conn.send("User does not exist in credentials\n".encode())
    
    if( username == self.username ):
        self.conn.send("Cannot send message to self\n".encode())

    #Checking for all users
    for clientThread in clientThreads:
        if(clientThread.username == username):
            if(clientThread.loggedIn == True):
                clientThread.conn.send("{}: {}\n".format(self.username,message ).encode())
            else:
                #Add to offline messages for clientThread
                clientThread.offlineMsgs.append(message)

class InactiveUserbooter(Thread):
    def __init__(self):
        Thread.__init__(self)
    
    def run(self):
        while 1:
            #Scroll through list of inavtiev users and disconnect them
            time.sleep(1)


class ClientThread(Thread):

    def __init__(self,conn,address):
        Thread.__init__(self)
        self.conn = conn
        self.address = address
        self.loggedIn = False
        self.socketStatus = True
        self.blockedFrom = []
        self.offlineMsgs = []
        print ("[Thread - %d] New socket thread started from:%s" %(threading.currentThread().ident, str(address)))


    def run(self):
        while 1:
            if(self.socketStatus == False):
                return
            if(self.loggedIn == False):
                authResult = authenticateUser(self)
                if(authResult[1] == True):
                    self.username = authResult[0]
                    self.loginTime = time.time()
                    self.loggedIn = True
                    broadcast(self,"{} logged in \n".format(self.username))
                    #Send all offline messages and empty list
                    sendOfflineMessages(self)
                continue
            
            #prompt()
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
            elif(commands[0] == "whoelsesince"):
                lastOnline = whoelsesince(self, commands[1])
                for client in lastOnline:
                    self.conn.send("{}\n".format(client.username))
                continue
            elif(commands[0] == "message"):
                msg = ' '.join(commands[2:])
                messageUser(self, commands[1], msg)
                continue
            elif(commands[0] == "block"):
                blockFrom(self, commands[1])
                continue
            elif(commands[0] == "unblock"):
                unblockFrom(self, commands[1])
                continue
            elif(commands[0] == "logout"):
                self.loggedIn = False
                self.conn.send("Logging out...\n".encode())
                #disconnectUser(self)
                continue
            else:
                self.conn.send("Command does not exist. Try again\n")
                continue

        


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
    port = 13007  # initiate port no above 1024

    server_socket = socket(AF_INET, SOCK_STREAM)  # get instance
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.bind((host, port))  
    #Store usernames and ports in a dictionary

    InactiveUserbooter().start()

    while True:
        server_socket.listen(20)
        conn, address = server_socket.accept()  # accept new connection
        print("Connection from: " + str(address))
        aThread = ClientThread(conn, address)
        aThread.start()
        clientThreads.append(aThread)
    
    

if __name__ == '__main__':
    server_program()
#clientThread.blockedFrom =  ([str(clientThread.blockedFrom[x]) for x in range(len(clientThread.blockedFrom))])