from flask import Flask, request
from flask_cors import CORS
import json
import socket
import threading
import random
import codecs
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

pause = False

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
        try:
            self.conn.shutdown(socket.SHUT_RDWR)
            self.conn.close()
        except:
            # do nothing
            pass
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.server, self.port))
        print(self.server)
        self.connected = True
    def getResponse(self):
        return self.conn.recv(512)
    def command(self, command, data):
        cmd = f"{command} {data}\r\n"
        try:
            self.conn.send(cmd.encode('ascii'))
        except:
            pass
    def sendMessage(self, message):
        self.command(f"PRIVMSG {self.channel}", f":{message}")
        now = datetime.now()
        self.messagesBuffer.append([self.name, message, now.strftime("%H:%M:%S")])
    def joinChannel(self, channel):
        self.command("JOIN", channel)
    def quit(self):
        client.command("QUIT", "Good bye!")
        try:
            client.conn.shutdown(socket.SHUT_RDWR)
            client.conn.close()
        except:
            pass
        client.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def heavylifter(client):  # function that does all background jobs, all the heavy-lifitng, you get it.
    while not pause:
        if client.connected:
            response = codecs.decode(client.getResponse(), 'utf-8')
            #print(response)
            if response and client.joined and not ("353" in response):
                msg = response.strip().split(":")
                now = datetime.now()
                if "JOIN" in response:
                    r = response.strip().split(":")
                    u = r[1].split("!")[0]
                    client.messagesBuffer.append(["", f"{u} has joined {r[2]}", now.strftime("%H:%M:%S")])
                    client.user_list = []
                    client.command("NAMES", "")
                elif "QUIT" in response:
                    r = response.strip().split(":")
                    u = r[1].split("!")[0]
                    client.messagesBuffer.append(["", f"{u} has quit: \"{r[3]}\"", now.strftime("%H:%M:%S")])
                    client.user_list = []
                    client.command("NAMES", "")
                else:
                    client.messagesBuffer.append([msg[1].split("!")[0], msg[len(msg)-1], now.strftime("%H:%M:%S")])
            if "PING" in response:
                client.command("PONG", response.split(':')[1])
            elif "376" in response:
                client.joinChannel(client.channel)
                msg = response.strip().split(":")
                now = datetime.now()
                client.joined = True
            elif "366" in response:
                client.joined = True
                client.messagesBuffer = []
                client.messagesBuffer.append(["", f"Joined {client.channel} as {client.name}", now.strftime("%H:%M:%S")])
            elif "353" in response:
                client.userList.extend(response.split(":")[2].split(" "))
                print(client.userList)
            elif "No Ident response" in response or "Found your hostname" in response:
                client.command("NICK", client.name)
                client.command("USER", f"{client.name} 0 * :{client.name}")

client = IRC_client(f"default_name{random.randint(10000, 99999)}", "irc.freenode.net", 6667, "#anonchat")

def form_response(error, data):
    return json.dumps({
        'error': error,
        'data': data
    })

@app.route("/ircgateway", methods=['POST'])
def irc_gateway():
    global client
    content = request.get_json()
    print(content)
    if content['command'] == 'connect':
        if(client.connected):
            pause = True
            client.connected = False
            client.messagesBuffer = []
            client.userList = []
            client.joined = False
            client.quit()
        nickname = content['data'][0]
        ip = content['data'][1]
        channel = content['data'][2]
        port = int(content['data'][3])
        client.name = nickname
        client.server = ip
        client.port = port
        client.channel = channel
        print(f"{client.name} {client.server} {client.port} {client.channel}")
        client.connect()
        return form_response("none", "connection performed")
    elif content['command'] == 'fetch':
        if content['data'][0] == 'messages':
            return form_response("none", json.dumps(client.messagesBuffer))
        elif content['data'][0] == 'users':
            return form_response("none", json.dumps(client.userList))
    elif content['command'] == 'send':
        print(content['data'])
        client.sendMessage(content['data'][1])
    elif content['command'] == 'end':
        client.quit()
    return form_response("none", "none")

class App1(threading.Thread):
    def run(self):
        print("Starting server")
        app.run(host="0.0.0.0", port=3001, debug=False, ssl_context=('/certs/cert.pem', '/certs/privkey.pem'))
class App2(threading.Thread):
    def run(self):
        print("Starting heavylifter")
        while True:
            heavylifter(client)
            while pause:
                pass

if __name__ == '__main__':
    server = App1()
    lifter = App2()
    server.start()
    lifter.run()