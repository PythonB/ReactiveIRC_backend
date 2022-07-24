import json
import socket
import threading
import random
import codecs

class IRC_client:
    def __init__(self, name, server, port, channel):
        self.name = name
        self.server = server
        self.port = port
        self.channel = channel
        self.channelList = []
        self.userList = []
        self.messagesBuffer = []
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.joined = False
        self.connected = False
    def connect(self):
        self.conn.connect((self.server, self.port))
        self.connected = True
    def getResponse(self):
        return self.conn.recv(512)
    def command(self, command, data):
        cmd = f"{command} {data}\r\n"
        self.conn.send(cmd.encode('ascii'))
    def sendMessage(self, message):
        self.command(f"PRIVMSG {channel}", f":{message}")
    def joinChannel(self, channel):
        self.command("JOIN", channel)
    def quit(self):
        client.command("QUIT", "Good bye!")
        client.conn.close()
        client.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def heavylifter(client):  # function that does all background jobs, all the heavy-lifitng, you get it.
    while True:
        if client.connected:
            response = codecs.decode(client.getResponse(), 'utf-8')
            if response and client.joined:
                msg = response.strip().split(":")
                print(msg[len(msg)-1])
            elif response:
                print(response.strip())
            if "PING" in response:
                client.command("PONG", response.split(':')[1])
            elif "376" in response:
                print(f"Joining {client.channel}")
                client.joinChannel(client.channel)
                client.joined = True
            elif "366" in response:
                print("Joined")
                client.joined = True
            elif "No Ident response" in response or "Found your hostname" in response:
                print("Registering")
                client.command("NICK", client.name)
                client.command("USER", f"{client.name} 0 * :{client.name}")

client = IRC_client(f"default_name{random.randint(10000, 99999)}", "irc.freenode.net", 6667, "#anonchat")
client.connect()
heavylifter(client)