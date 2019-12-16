# COMP3331Assignment
This application is an instant messaging application simulator (like WhatsApp, Facebook Messenger).
It's based on a client server model consisting of one server and multiple messaging clients. The clients communicate with the server using TCP. The server is mainly used to authenticate the clients and direct the messages (online or offline) between
clients. Besides, the server can also support certain additional functions (presence notification
blacklisting, timeout, etc.). Peer to peer functionality is also implemented where clients can talk among themselves bypassing the server.

## Getting Started
These instructions will get you a copy of the project up and running on your local machine.
Install Python Version 2.1.7

Clone the repo
```
git clone https://github.com/Ravija5/COMP3331Assignment.git

```

Start up the server
```
python server.py server_port block_duration timeout

```

Start up any number of clients
```
python client.py server_IP server_port

```

## Author
Ravija Maheshwari 






