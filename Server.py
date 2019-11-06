from socket import *
import threading
from threading import Thread
import sys
import time

def authenticateUser(self):
    uname= self.conn.recv(1024).decode()
    print("[Thread - %d] username recd: %s" %(threading.currentThread().ident, str(uname)))
    #self.conn.send("Password:".encode())
    #receive Password
    password = self.conn.recv(1024).decode()
    print("[Thread - %d] Password recd: %s" %(threading.currentThread().ident, str(password)))
    if(isExists(uname) == False):
        self.conn.send("Username does not exist")
        return

    if(userStatus[uname] == 0):
        #User is not blocked
        userTries[uname] = userTries[uname] + 1
        if(userPass[uname] == password):
            userTries[uname] = 0
            self.conn.send("Credentials authenticated")
        else:
            if (userTries[uname] == 3):
                #Block user
                self.conn.send("Invalid Password. Your account has been blocked. Please try again later")
                userStatus[uname] =  time.time()
                return
            self.conn.send("Password incorrect")
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
                self.conn.send("Credentials authenticated")
            else:
                self.conn.send("Password incorrect")
        else:
            self.conn.send("Your account is blocked due to multiple login failures. Please try again later")
            print("User still blocked")

class ClientThread(Thread):

    def __init__(self,conn,address):
        Thread.__init__(self)
        self.conn = conn
        self.address = address
        print ("[Thread - %d] New socket thread started from:%s" %(threading.currentThread().ident, str(address)))

    def run(self):
        while True:
            authenticateUser(self)

        #close connection upon some condition.
        conn.close()

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
userStatus = {}
blocked_duration = sys.argv[1]


for userCreds in credLines:
    user = userCreds.split()
    userTries[user[0]] = 0
    userPass[user[0]] = user[1]
    userStatus[user[0]] = 0
# print userTries
# print userPass
# print userStatus

#To check if a username exists in database
def isExists(uname):
    for line in credLines:
        user = line.split()
        if(user[0] == uname):
            return True
            break
    return False

threads = []
def server_program():
    # get the hostname
    host = "127.0.0.1"
    print("Host: " +host)
    port = 13002  # initiate port no above 1024

    server_socket = socket(AF_INET, SOCK_STREAM)  # get instance
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    # look closely. The bind() function takes tuple as argument
    server_socket.bind((host, port))  # bind host address and port together

    # configure how many client the server can listen simultaneously

    while True:
        server_socket.listen(20)
        conn, address = server_socket.accept()  # accept new connection
        print("Connection from: " + str(address))
        aThread = ClientThread(conn, address).start()
        threads.append(aThread)



if __name__ == '__main__':
    server_program()
