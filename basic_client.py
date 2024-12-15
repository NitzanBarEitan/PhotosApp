import socket
import os
from socket_app_utils import JSONSocket

# For now, that will be localhost and port 5000
server_address = ("127.0.0.1", 5000)

library_path = "client_library"

def create_album(album_name):
    with JSONSocket(server_address) as my_socket:
        command = {
            "action": "CREATE_ALBUM",
            "album_name": album_name
        }
        my_socket.send_json(command)
        response = my_socket.receive_json()
        print(response)

def get_photo(album_name, photo_name):
    """This method gets only one photo at a time."""

    with JSONSocket(server_address) as my_socket:

        command = {
            "action": "GET_PHOTO",
            "album_name": album_name,
            "photo_name": photo_name
        }
        my_socket.send_json(command)

        my_socket.receive_photo(os.path.join(library_path, photo_name))

def upload_photo(album_name, photo_path):

    photo_size = os.path.getsize(photo_path)
    photo_name = os.path.basename(photo_path)
    with JSONSocket(server_address) as client:
        command = {
            "action": "UPLOAD_PHOTO",
            "album_name": album_name,
            "photo_name": photo_name
        }
        client.send_json(command)
        response = client.receive_json()
        if response.startswith("Error"):
            print(response)
            return
        client.send_photo(photo_path)

    
def find_faces(album_name, target_photo):
    with JSONSocket(server_address) as client:
        command = {
            "action": "SEARCH_FACE",
            "album_name": album_name,
            "target_photo": target_photo
        }
        client.send_json(command)

        response = client.receive_json()
        if response.startswith("Error"):
            print(response)
            return
        matching_lst = client.receive_json()
        for photo in matching_lst:
            get_photo(album_name, photo)

def main():
    # Create the library folder if it does not already exist
    os.makedirs(library_path, exist_ok=True)
    create_album("first_album")
    find_faces("first_album", "PXL_20241202_121514389.PORTRAIT.jpg")

if __name__ == "__main__":
    main()

