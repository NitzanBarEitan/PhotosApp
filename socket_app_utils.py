import socket
import json
import os

class JSONSocket:
    def __init__(self, server_address: tuple, sock=None):
        """The constructor of this class initializes a socket if the user of this class 
        did not provide one"""
        self.server_address = server_address
        self.sock = sock or socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __enter__(self):
        self.connect(self.server_address)
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        if self.sock:
            self.close()

    def connect(self, address: tuple):
        self.sock.connect(address)

    def bind(self, address):
        self.sock.bind(address)

    def listen(self, backlog=5):
        self.sock.listen(backlog)

    def accept(self):
        client_sock, address = self.sock.accept()
        return JSONSocket(client_sock), address

    def send_json(self, data):
        try:
            json_data = json.dumps(data).encode()
            # First, the socket sends the size of the JSON data
            self.sock.send(len(json_data).to_bytes(4, byteorder='big'))
            # Then, the socket sends the JSON data. As I understand, the sendall() method sends
            # the data over the socket and handles cases when only part of the data could be sent.
            self.sock.sendall(json_data)
        except (OSError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Error sending JSON data: {e}")

    def receive_json(self):
        try:
            # First, recieve the size of the JSON data
            size_data = self.sock.recv(4) # CR: next comment applies here, just matters less
            if not size_data:
                raise RuntimeError("No JSON-size data sent")
            size = int.from_bytes(size_data, byteorder='big')

            # Then receive the actual JSON data
            json_data = self.sock.recv(size).decode() # CR: recv might not receive all of the bytes requested, this should be a for loop
            return json.loads(json_data)
        except (OSError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Error receiving JSON data: {e}")
    
    def send_photo(self, photo_path: str):
        """
        This method recieves the photo path to be sent,
         and sends the photo in chunks over the socket using json.
        """
        try:
            # First, send the size of the photo

            if os.path.exists(photo_path):
                photo_size = os.path.getsize(photo_path)
                self.send_json(photo_size)
                with open(photo_path, "rb") as photo_file:
                    while True:
                        chunk = photo_file.read(4096)
                        if not chunk:
                            break
                        self.send_json(chunk)
                self.send_json("Photo downloaded")
            else:
                self.send_json(b"Error: Photo not found") # CR: once you send bytes, the other time a string, this should be the same
        except(OSError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Error sending photo: {e}")
        
    def receive_photo(self, photo_path: str):
        """
        This method recieves the path in which the photo will be saved, and recieves
        the photo from the socket using json. The photo is sent in chunks.
        """
        try:
            # First, receive the size of the photo
            photo_size = self.receive_json()
            with open(photo_path, "wb") as photo_file:
                remaining = photo_size
                while remaining > 0:
                    chunk = self.receive_json() # CR: this while loop should not be here, it should be in receive_json. The underlying protocol supports sending arbitrary size messages
                    if not chunk:
                        break
                    photo_file.write(chunk)
                    remaining -= len(chunk)
        except(OSError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Error receiving photo: {e}")

    def close(self):
        self.sock.close()
