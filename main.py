import http.server
import socketserver
import socket
import threading
import json
from datetime import datetime
from pymongo import MongoClient
from urllib.parse import urlparse, parse_qs
import os

client = MongoClient("mongodb://mongo:27017/")
db = client["message_db"]
collection = db["messages"]

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "/index.html"
        elif self.path == "/message.html":
            self.path = "/message.html"
        elif self.path == "/style.css":
            self.path = "/style.css"
        elif self.path == "/logo.png":
            self.path = "/logo.png"
        else:
            self.path = "/error.html"
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == "/message":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = parse_qs(post_data.decode('utf-8'))
            username = data['username'][0]
            message = data['message'][0]
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(json.dumps({
                "username": username,
                "message": message
            }).encode('utf-8'), ("localhost", 5000))

            self.send_response(302)
            self.send_header('Location', '/message.html')
            self.end_headers()

def socket_server():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("0.0.0.0", 5000))
    print("UDP Socket Server is up and listening")

    while True:
        data, addr = udp_socket.recvfrom(1024)
        message = json.loads(data.decode('utf-8'))
        message["date"] = datetime.now().isoformat()
        collection.insert_one(message)
        print(f"Received message: {message}")

httpd = socketserver.TCPServer(("0.0.0.0", 3000), MyHttpRequestHandler)
http_thread = threading.Thread(target=httpd.serve_forever)
http_thread.daemon = True
http_thread.start()

socket_server()