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
    uname = self.conn.recv(1024).decode()
    self.lastActivityTime = time.time()
    print("[Thread - %d] username recd: %s" % (threading.currentThread().ident, str(uname)))

    while (isExists(uname) == False):
        self.conn.send("Username does not exist\nUsername:")
        uname = self.conn.recv(1024).decode()
        self.lastActivityTime = time.time()
        print("[Thread - %d] username recd: %s" % (threading.currentThread().ident, str(uname)))

    self.username = uname

    #Figure out if this client exists. If so, update the one obtained.
    client = None
    for aClient in client_list:
        if aClient.username == uname:
            client = aClient
            break
    if client is not None:
        #Client exists.
        client.lastActivityTime = self.lastActivityTime
        client.conn = self.conn
        client.address = self.address
        self = client
    else:
        #New client.
        client_list.append(self)

    if (userBlock[uname] != 0):
        elapsedTime = time.time() - userBlock[uname]
        print (elapsedTime)
        if (float(elapsedTime) < float(BLOCKED_DURATION)):
            self.conn.send("Your account is blocked due to multiple login failures. Please try again later\n")
            disconnectUser(self)
            return (uname, False, self)
        else:
            userBlock[uname] = 0
            userTries[uname] = 0

    # user is not blocked
    self.conn.send("Password:".encode())
    password = self.conn.recv(1024).decode()

    self.lastActivityTime = time.time()
    print("[Thread - %d] Password recd: %s" % (threading.currentThread().ident, str(password)))

    while (userTries[uname] < 3):
        userTries[uname] = userTries[uname] + 1
        if (userPass[uname] == password):
            userTries[uname] = 0
            self.conn.send("Credentials authenticated\n".encode())
            return (uname, True, self)
        elif (userTries[uname] <= 2):
            self.conn.send("Invalid Password\nPassword:")
            password = self.conn.recv(1024).decode()
            self.lastActivityTime = time.time()
            print("[Thread - %d] Password recd: %s" % (threading.currentThread().ident, str(password)))

    self.conn.send("Invalid Password. Your account has been blocked. Please try again later\n")
    userBlock[uname] = time.time()
    disconnectUser(self)
    return (uname, False, self)

def broadcast(self, message, isUserCommand):
    if (len(blockedFromDict[self.username]) != 0 and isUserCommand):
        self.conn.send("Your message could not be delivered to some recipients\n".encode())

    for clientThread in client_list:
        if (clientThread.loggedIn == True and clientThread.username != self.username and clientThread.username not in blockedFromDict[self.username]):
            clientThread.conn.send(message.encode())

def blockFrom(self, username):
    print("Checking for : {}".format(username))
    if (isExists(username) == False):
        self.conn.send("User does not exist in credentials\n".encode())
        return

    if (username == self.username):
        self.conn.send("Cannot block self\n".encode())
        return
    
    if(self.username in blockedFromDict[username]):
        self.conn.send("User is already blocked\n".encode())
    else:
        blockedFromDict[username].append(self.username.encode())
        self.conn.send("Blocked {}\n".format(username))

def unblockFrom(self, username):
    if (isExists(username) == False):
        self.conn.send("User does not exist in credentials\n".encode())
        return

    if (username == self.username):
        self.conn.send("Cannot unblock self\n".encode())
        return

    if(self.username not in blockedFromDict[username]):
        self.conn.send("User is already unblocked. No action required\n".encode())
    else:
        blockedFromDict[username].remove(self.username)
        self.conn.send("Unblocked {}\n".format(username))   

def whoelsesince(self, givenTime):
    lastOnline = []
    for clientThread in client_list:
        if (clientThread.username != self.username):
            currTime = time.time()
            elapsedTime = currTime - clientThread.loginTime
            if (int(elapsedTime) < int(givenTime)):  
                lastOnline.append(clientThread)

    return lastOnline

def sendOfflineMessages(self):
    offline = []
    if (len(offLineMsgDict[self.username]) == 0):
        #self.conn.send("You received no offline messages\n".encode())
        return offline

    self.conn.send("Your offline messages are:\n".encode())
    #Usernames and passwords
    v = offLineMsgDict[self.username]
    for sender, msg in v:
        text = ("{}: {}".format(sender, msg))
        offline.append(text)

    print("Cleaning offline dict")
    offLineMsgDict[self.username] = []
    print(offLineMsgDict)
    return offline


def messageUser(self, username, message):
    if (isExists(username) == False):
        self.conn.send("User does not exist in credentials\n".encode())
        return

    if (username == self.username):
        self.conn.send("Cannot send message to self\n".encode())
        return

    if (username in blockedFromDict[self.username]):
        self.conn.send("You cannot message {} as you have been blocked by them\n".format(username).encode())
        return

    # Checking for all users
    for clientThread in client_list:
        if (clientThread.username == username and clientThread.loggedIn == True):
            clientThread.conn.send("{}: {}\n".format(self.username, message).encode())
            return

    print("In msg user")
    print(offLineMsgDict)
    # Add to offline messages for clientThread
    offLineMsgDict[username].append((self.username.encode(), message.encode()))
    print (offLineMsgDict)


class InactiveUserBooter(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True

    def run(self):
        while 1:
            # Scroll through list of inactive users and disconnect them
            timeNow = time.time()
            for clientThread in client_list:
                if (clientThread.socketStatus == False):
                    continue
                elapsedTime = timeNow - clientThread.lastActivityTime
                # print ("[Thread - %d] InactiveUserBooter thread. Client: %s, Elasped: %d." %(threading.currentThread().ident, getattr(clientThread, 'username', 'NONE'), elapsedTime))
                if (elapsedTime >= MAX_INACTIVE_TIME_SECONDS):
                    disconnectUser(clientThread)

            time.sleep(1)


def openp2p(self, to_user):
    if (isExists(to_user) == False):
        self.conn.send("User does not exist.\n".encode())
        return

    client = None
    for aClient in client_list:
        if (aClient.username == to_user):
            client = aClient
            break

    if (client == None):
        self.conn.send("User is not logged in.\n".encode())
        return

    if (client.loggedIn == False):
        self.conn.send("User is not logged in.\n".encode())
        return

    if (client.username == self.username):
        self.conn.send("User is same as you.\n".encode())
        return

    if (client.username in self.blockedFrom):
        self.conn.send("You are blocked by this user.\n".encode())
        return

    # P2PREQUEST b a
    message = "P2PREQUEST {} {}".format(self.username, to_user)
    print("Sending message: " + message)
    client.conn.send(message.encode())


def sendback_port(self, fromuser, touser, ip, port):
    # P2PPORT b a IP 55001
    client = None
    for aClient in client_list:
        if (aClient.username == fromuser):
            client = aClient
            break
    if (client == None):
        print("User {} not found".format(fromuser))
        return
    message = "P2PACCEPTED {} {} {} {}".format(fromuser, touser, ip, port)
    print("Sending message: " + message)
    client.conn.send(message.encode())

def runthread(self):
    print ("[Thread - %d] New socket thread started from:%s" % (threading.currentThread().ident, str(self.address)))
    try:
        while 1:
            if (self.socketStatus == False):
                return
            if (self.loggedIn == False):
                authResult = authenticateUser(self)
                self = authResult[2]
                if (authResult[1] == True):
                    self.username = authResult[0]
                    self.loginTime = time.time()
                    self.loggedIn = True
                    self.socketStatus = True
                    time.sleep(1)
                    broadcast(self, "{} logged in \n".format(self.username),False)
                    offline = sendOfflineMessages(self)
                    if (len(offline) == 0):
                        self.conn.send("You received no offline messages\n".encode())
                    for msg in offline:
                        self.conn.send("{}\n".format(msg).encode())
                    self.lastActivityTime = time.time()
                continue

            # prompt()
            command = self.conn.recv(1024).decode()
            self.lastActivityTime = time.time()
            commands = command.split()
            if (commands[0] == "broadcast"):
                msg = ' '.join(commands[1:])
                broadcast(self, "{}: {}\n".format(self.username, msg), True)
                continue
            elif (commands[0] == "whoelse"):
                for clientThread in client_list:
                    if (clientThread.loggedIn == True and clientThread.username != self.username):
                        self.conn.send("{}\n".format(clientThread.username))
                continue
            elif (commands[0] == "whoelsesince"):
                lastOnline = whoelsesince(self, commands[1])
                for client in lastOnline:
                    self.conn.send("{}\n".format(client.username))
                continue
            elif (commands[0] == "message"):
                msg = ' '.join(commands[2:])
                messageUser(self, commands[1], msg)
                continue
            elif (commands[0] == "block"):
                blockFrom(self, commands[1])
                continue
            elif (commands[0] == "unblock"):
                unblockFrom(self, commands[1])
                continue
            elif (commands[0] == "logout"):
                self.loggedIn = False
                broadcast(self, "{} logged out\n".format(self.username), False)
                break
            elif (commands[0] == "startprivate"):
                # startprivate a
                openp2p(self, commands[1])
                continue
            elif (commands[0] == "P2PPORT"):
                # P2PPORT b a 55001
                print(commands)
                sendback_port(self, commands[1], commands[2], self.address[0], commands[3])
                continue
            else:
                self.conn.send("Command does not exist. Try again\n")
                continue
        disconnectUser(self)
    except Exception:
        print ("[Thread - %d] Client thread terminated exceptionally." % (threading.currentThread().ident))
    print ("[Thread - %d] Client thread terminated." % (threading.currentThread().ident))


def printClientList():
    for clientThread in client_list:
        message = "user: {}, loggedIn: {}".format(clientThread.username, clientThread.loggedIn)
        print(message)


class Client():

    def __init__(self, conn, address):
        self.conn = conn
        self.address = address
        self.loggedIn = False
        self.socketStatus = True
        self.blockedFrom = []
        self.offlineMsgs = []
        self.lastActivityTime = time.time()


# Open file
creds = open("credentials.txt", "r")
credLines = creds.readlines()
creds.close
print("File opened")

# To keep a track of user and tries
userTries = {}
# Usernames with passwords
userPass = {}
# To keep a track of user status (blocked/unblocked)
userBlock = {}
#Username -> blocked from users
blockedFromDict = {}
offLineMsgDict = {}

for userCreds in credLines:
    user = userCreds.split()
    userTries[user[0]] = 0
    userPass[user[0]] = user[1]
    userBlock[user[0]] = 0
    blockedFromDict[user[0]] = []
    offLineMsgDict[user[0]] = []

# To check if a username exists in database
def isExists(uname):
    for line in credLines:
        user = line.split()
        if (user[0] == uname):
            return True
            break
    return False


client_list = []

PORT = int(sys.argv[1])
BLOCKED_DURATION = int(sys.argv[2])
MAX_INACTIVE_TIME_SECONDS = int(sys.argv[3])


def server_program():
    # get the hostname
    host = "127.0.0.1"
    print("Host: " + host)

    server_socket = socket(AF_INET, SOCK_STREAM)  # get instance
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.bind((host, PORT))
    # Store usernames and ports in a dictionary

    InactiveUserBooter().start()

    while True:
        server_socket.listen(20)
        conn, address = server_socket.accept()  # accept new connection
        print("Connection from: " + str(address))
        aClient = Client(conn, address)
        threading.Thread(target=runthread, args=(aClient,)).start()


if __name__ == '__main__':
    server_program()
# clientThread.blockedFrom =  ([str(clientThread.blockedFrom[x]) for x in range(len(clientThread.blockedFrom))])
