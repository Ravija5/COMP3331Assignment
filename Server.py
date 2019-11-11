from socket import *
import threading
from threading import Thread
import sys
import time


def disconnectUser(self):
    print ("In disconnect: {} ".format(getattr(self, 'username', 'NONE')))
    self.conn.send("Bye\n".encode())
    self.socketStatus = False
    time.sleep(1)
    self.conn.close()

def authenticateUser(self):
    self.conn.send("Username:".encode())
    uname= self.conn.recv(1024).decode()
    self.lastActivityTime = time.time()
    print("[Thread - %d] username recd: %s" %(threading.currentThread().ident, str(uname)))

    while (isExists(uname) == False):
        self.conn.send("Username does not exist\nUsername:")
        uname= self.conn.recv(1024).decode()
        self.lastActivityTime = time.time()
        print("[Thread - %d] username recd: %s" %(threading.currentThread().ident, str(uname)))

    self.username = uname
    if(userBlock[uname] != 0):
        elapsedTime = time.time() - userBlock[uname]
        print elapsedTime
        if(float(elapsedTime) < float(BLOCKED_DURATION)):
            self.conn.send("Your account is blocked due to multiple login failures. Please try again later\n")
            disconnectUser(self)
            return (uname, False)
        else:
            userBlock[uname] = 0
            userTries[uname] = 0

    #user is not blocked
    self.conn.send("Password:".encode())
    password = self.conn.recv(1024).decode()
    self.lastActivityTime = time.time()
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
            self.lastActivityTime = time.time()
            print("[Thread - %d] Password recd: %s" %(threading.currentThread().ident, str(password)))

    self.conn.send("Invalid Password. Your account has been blocked. Please try again later\n")
    userBlock[uname] =  time.time()
    disconnectUser(self)
    return (uname, False)

def broadcast(self, message):
    if(len(self.blockedFrom) != 0):
        self.conn.send("Your message could not be delivered to some recipients\n".encode())

    for clientThread in clientThreads:
        if(clientThread.loggedIn == True and clientThread.username != self.username and clientThread.username not in self.blockedFrom):
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
        if(clientThread.username != self.username):
            print("{} logged in at {}\n".format(clientThread.username,clientThread.loginTime ))
            elapsedTime = time.time() - clientThread.loginTime
            #print (elapsedTime)
            print("Elasped time = {}".format(elapsedTime))
            if(elapsedTime < givenTime):
                lastOnline.append(clientThread)

    return lastOnline

def sendOfflineMessages(self):

    offline = []
    if(len(self.offlineMsgs) == 0):
        #self.conn.send("You received no offline messages\n".encode())
        return offline

    self.conn.send("Your offline messages are:\n".encode())
    for msg in self.offlineMsgs:
        offline.append(msg)
        #self.conn.send("{}\n".format(msg))
    self.offlineMsgs = []
    return offline

def messageUser(self, username, message):
    if(isExists(username) == False):
        self.conn.send("User does not exist in credentials\n".encode())

    if( username == self.username ):
        self.conn.send("Cannot send message to self\n".encode())

    if(username in self.blockedFrom):
        self.conn.send("You cannot message {} as you have been blocked by them\n".format(username).encode())
        return

    #Checking for all users
    for clientThread in clientThreads:
        if(clientThread.username == username):
            if(clientThread.loggedIn == True):
                clientThread.conn.send("{}: {}\n".format(self.username,message ).encode())
            else:
                #Add to offline messages for clientThread
                clientThread.offlineMsgs.append(message)


class InactiveUserBooter(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True

    def run(self):
        while 1:
            #Scroll through list of inactive users and disconnect them
            timeNow = time.time()
            for clientThread in clientThreads:
                if(clientThread.socketStatus == False):
                    continue
                elapsedTime = timeNow - clientThread.lastActivityTime
                # print ("[Thread - %d] InactiveUserBooter thread. Client: %s, Elasped: %d." %(threading.currentThread().ident, getattr(clientThread, 'username', 'NONE'), elapsedTime))
                if(elapsedTime >= MAX_INACTIVE_TIME_SECONDS):
                    disconnectUser(clientThread)

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
        self.lastActivityTime = time.time()
        print ("[Thread - %d] New socket thread started from:%s" %(threading.currentThread().ident, str(address)))


    def run(self):
        try:
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
                        offline = sendOfflineMessages(self)
                        if(len(offline) == 0):
                            self.conn.send("You received no offline messages\n".encode())
                        for msg in offline:
                            self.conn.send("{}\n".format(msg).encode())
                        self.lastActivityTime = time.time()
                    continue

                #prompt()
                command = self.conn.recv(1024).decode()
                self.lastActivityTime = time.time()
                commands = command.split()
                if(commands[0] == "broadcast"):
                    msg = ' '.join(commands[1:])
                    broadcast(self,"{}: {}\n".format(self.username, msg))
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
                    disconnectUser(self)
                    continue
                else:
                    self.conn.send("Command does not exist. Try again\n")
                    continue
        except Exception:
            print("Client thread terminated.")




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

PORT = int (sys.argv[1])
BLOCKED_DURATION = int (sys.argv[2])
MAX_INACTIVE_TIME_SECONDS = int (sys.argv[3])

def server_program():
    # get the hostname
    host = "127.0.0.1"
    print("Host: " +host)

    server_socket = socket(AF_INET, SOCK_STREAM)  # get instance
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.bind((host, PORT))
    #Store usernames and ports in a dictionary

    InactiveUserBooter().start()

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
