import socket
import os

# For now, that will be localhost and port 5000
server_address = ("127.0.0.1", 5000)

library_path = "client_library"

def send_command(command):
    """
    In this method I am defining a socket, so that I do not have to do that everytime I need to
    send a specific message. Right now only one method sends and receives basic text message, but
    this method is here for the future.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as my_socket:
        my_socket.connect(server_address)
        my_socket.send(command.encode())
        response = my_socket.recv(4096).decode()
        print(response)

    def create_album(album_name):
        send_command(f"CREATE_ALBUM {album_name}")

    def get_photo(album_name, photo_name):
        """This method gets only one photo at a time."""

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as my_socket:
            my_socket.connect(server_address)

            # First, the socket asks for the specific photo
            my_socket.send(f"GET_PHOTOS {album_name} {photo_name}".encode())

            # The server sends the requested photo's size as a response
            response = my_socket.recv(4096).decode()
            photo_size = 0
            if response.startswith("Error"):
                print(response)
            else:
                photo_size = int(response)

                photo_path = os.path.join(library_path, photo_name)
                with open(photo_path, "wb") as photo_file:
                    remaining = photo_size
                    while remaining > 0:
                        chunk = my_socket.recv(min(4096, remaining))
                        if not chunk:
                            break
                        photo_file.write(chunk)
                        remaining -= len(chunk)





    def upload_photo(album_name, photo_path):
        """
        I am trying to figure out if this way the best way to send photos through sockets.
        I saw another similar way. For now, this method slices the photo into chunks, and then
        sends each chunk to the server.
        """
        photo_size = os.path.getsize(photo_path)
        photo_name = os.path.basename(photo_path)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect(server_address)
            command = f"UPLOAD_PHOTO {album_name} {photo_name} {photo_size}"
            client.send(command.encode())

        response = client.recv(4096).decode()
        if response.startswith("Error"):
            print("response")
        else:
            # Send photo data
            with open(photo_path, "rb") as photo_file:
                while chunk := photo_file.read(4096):
                    client.send(chunk)

            response = client.recv(4096).decode()
            print(response)