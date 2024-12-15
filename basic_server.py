import socket
import os
import face_recognition # CR: this should be in the requirements.txt file
from socket_app_utils import JSONSocket

# CR: Typing! use python typing. it makes the code much more understandable and much less error prone.

album_folder = "albums"

def find_matching_photos(album_name: str, face_image_path: str):
    """
    This method receives the album name and the path to the face image. then, the method compares the
    face data to all the faces in the photos in the specific album. The method returns a list of
    the names of all the photos.
    right now, the logic is that `the client will need only the names of the photos, after that the
    method get_photos() can be used to get all these photos if needed.
    """
    album_path = os.path.join(album_folder, album_name)
    if not os.path.exists(album_path):
        return "Error: Album not found" # CR: multiple return types is bad python. you should return an option.

    
    # Load the provided face image to the library face_recognition
    target_image = face_recognition.load_image_file(face_image_path)
    target_encoding = face_recognition.face_encodings(target_image)[0]

    # Storing here all the photos to be returned
    matching_photos = []
    for photo_name in os.listdir(album_path):
        # Analyzing each of the photos in the album
        photo_path = os.path.join(album_path, photo_name)
        image = face_recognition.load_image_file(photo_path) 
        encodings = face_recognition.face_encodings(image)

        # Comparing the face data to the target
        for encoding in encodings:
            match = face_recognition.compare_faces([target_encoding], encoding)
            if match[0]:
                matching_photos.append(photo_name)
                break

    return matching_photos if matching_photos else ["Error: no matching photos"]


def handle_client(client_socket):
    """
    This method recieves the client socket, casts it to be JSONSocket, a custom class that
    I wrote to handle JSON data over the socket. Based on the action that the client sends 
    through JSON, the method will perform the appropriate action.
    """

    try:
        clinet_json = JSONSocket(client_socket)

        command = clinet_json.receive_json() # CR: what if multiple commands were sent? this would read all of them.
        action = command.get("action")

        if action == "CREATE_ALBUM":
            album_name = command.get("album_name")
            album_path = os.path.join(album_folder, album_name)
            os.makedirs(album_path, exist_ok=True)
            clinet_json.send_json(f"Album '{album_name}' created.")

        elif action == "GET_PHOTO":
            album_name = command.get("album_name")
            photo_name = command.get("photo_name")
            photo_path = os.path.join(album_folder, album_name, photo_name)

            clinet_json.send_photo(photo_path)

        elif action == "UPLOAD_PHOTO":
            album_name = command.get("album_name")
            photo_name = command.get("photo_name")
            album_path = os.path.join(album_folder, album_name)

            # Checking if the album exists
            if os.path.exists(album_path):
                clinet_json.send_json("Album found")
            else:
                clinet_json.send_json("Error: Album not found")
                return

            photo_path = os.path.join(album_path, photo_name)
            clinet_json.receive_photo(photo_path)
            
        elif action == "SEARCH_FACE":

            album_name = command.get("album_name")
            target_face = command.get("target_photo")

            target_face_path = os.path.join(album_folder, album_name, target_face)

            if os.path.exists(target_face_path):
                result = find_matching_photos(album_name, target_face_path)
                if result[0].startswith("Error"):
                    clinet_json.send_json(result[0])
                    return
                else:
                    clinet_json.send_json("Face recognition process completed successfully")
                    clinet_json.send_json(result)
            else:
                clinet_json.send_json("Error: Photo not found")

    except Exception as e:
        clinet_json.send_json(f"Error: {str(e)}")
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

