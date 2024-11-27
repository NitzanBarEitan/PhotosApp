import socket
import os

# I am running the app on localhost for now, so the albums path will be on the same computer
# as the server and client
album_folder = "albums"


def handle_client(client_socket):
    """
    I tried to create with this method some kind of custom communication. This method receives the
    socket, decodes the message sent by the client, and based on the command in the message decides
    on one of three actions: creating an album, storing a photo or sending back all photos in a
    specific album.
    """

    try:
        command = client_socket.recv(1024).decode().strip()
        if command.startswith("CREATE_ALBUM"):
            album_name = command.split(" ", 1)[1]
            album_path = os.path.join(album_folder, album_name)
            os.makedirs(album_path, exist_ok=True)
            client_socket.send(f"Album '{album_name}' created.".encode())

        elif command.startswith("GET_PHOTOS"):
            # Splitting the command into parts
            _, album_name, photo_name = command.split(" ", 2)
            photo_path = os.path.join(album_folder, album_name, photo_name)

            # Again, I am doing it here in the method of sending chunks of the photo
            if os.path.exists(photo_path):
                photo_size = os.path.getsize(photo_path)
                client_socket.send(str(photo_size).encode())
                with open(photo_path, "rb") as photo_file:
                    while True:
                        chunk = photo_file.read(4096)
                        if not chunk:
                            break
                        client_socket.send(chunk)
                client_socket.send(b"Photo downloaded")
            else:
                client_socket.send(b"Error: Photo not found")

        elif command.startswith("UPLOAD_PHOTO"):

            # Splitting the command into parts
            _, album_name, photo_name, photo_size = command.split(" ", 3)
            album_path = os.path.join(album_folder, album_name)

            # Checking if the album exists
            if os.path.exists(album_path):
                client_socket.send(b"All good")
            else:
                client_socket.send(b"Error: Album not found")
                return

            # Preparing to receive the photo
            photo_size = int(photo_size)
            photo_path = os.path.join(album_path, photo_name)

            # Receiving the photo as chunks and writing them to a file
            with open(photo_path, "wb") as photo_file:
                remaining = photo_size
                while remaining > 0:
                    chunk = client_socket.recv(min(4096, remaining))
                    if not chunk:
                        break
                    photo_file.write(chunk)
                    remaining -= len(chunk)
                client_socket.send(f"Photo {photo_name} uploaded".encode())
    except Exception as e:
        client_socket.send(f"Error: {str(e)}".encode())
    finally:
        client_socket.close()

def main():
    os.makedirs(album_folder, exist_ok=True)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", 5000))
    server.listen(5)

    print("Server started on port 5000")
    while True:
        client_socket, client_address = server.accept()
        print(f"Connection from {client_address}")
        handle_client(client_socket)

if __name__ == "__main__":
    main()

