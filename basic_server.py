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
            # Maybe later I am going to
            album_name = command.split(" ", 1)[1]
            album_path = os.path.join(album_folder, album_name)

        elif command.startswith("GET_PHOTOS"):
            _, album_name, photo_name = command.split(" ", 2)
            photo_path = os.path.join(album_folder, album_name, photo_name)

        elif command.startswith("UPLOAD_PHOTO"):
            # Working on it
            pass
    except:
        pass
    finally:
        pass

