import socket
import os
import face_recognition # CR: this should be in the requirements.txt file
import json

# CR: Typing! use python typing. it makes the code much more understandable and much less error prone.


# I am running the app on localhost for now, so the albums path will be on the same computer
# as the server and client
album_folder = "albums"

def find_matching_photos(album_name, face_image_path):
    """
    This method receives the album name and the path to the face image. then, the method compares the
    face data to all the faces in the photos in the specific album. The method returns a list of
    the names of all the photos.
    right now, the logic is that the client will need only the names of the photos, after that the
    method get_photos() can be used to get all these photos if needed.
    """
    album_path = os.path.join(album_folder, album_name)
    if not os.path.exists(album_path):
        return "Error: Album not found" # CR: multiple return types is bad python. you should return an option.

    try:
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

        return matching_photos if matching_photos else "Error: No matching photos found."

    except Exception as e: # CR: blanket catching all errors is bad code. catch only the specific errors you want to handle.
        return f"Error: {str(e)}"

def handle_client(client_socket):
    """
    I tried to create with this method some kind of custom communication. This method receives the
    socket, decodes the message sent by the client, and based on the command in the message decides
    on one of three actions: creating an album, storing a photo or sending back all photos in a
    specific album.
    """

    try:
        command = client_socket.recv(1024).decode().strip() # CR: what if multiple commands were sent? this would read all of them.
        if command.startswith("CREATE_ALBUM"):
            album_name = command.split(" ", 1)[1]
            album_path = os.path.join(album_folder, album_name)
            os.makedirs(album_path, exist_ok=True)
            client_socket.send(f"Album '{album_name}' created.".encode())

        elif command.startswith("GET_PHOTO"):
            # Splitting the command into parts
            _, album_name, photo_name = command.split(" ", 2)
            photo_path = os.path.join(album_folder, album_name, photo_name)

            # Again, I am doing it here in the method of sending chunks of the photo
            if os.path.exists(photo_path):
                photo_size = os.path.getsize(photo_path)
                client_socket.send(photo_size.to_bytes(8, byteorder='big')) # Very good. Sending the size before the message is a much more generic method, that you should use everywhere in the code. Move it to a different function, that sends the size of the data to be sent first before sending the data.
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
                    chunk = client_socket.recv(min(4096, remaining)) # CR: this is something you will do a lot in the client and server. export it to a function in a different file.
                    if not chunk:
                        break
                    photo_file.write(chunk)
                    remaining -= len(chunk)
                client_socket.send(f"Photo {photo_name} uploaded".encode())
        elif command.startswith("SEARCH_FACE"):
            _, album_name, target_face = command.split(" ", 2)
            target_face_path = os.path.join(album_folder, album_name, target_face)

            if os.path.exists(target_face_path):
                result = find_matching_photos(album_name, target_face_path)
                if result.startswith("Error"):
                    client_socket.send(result.encode())
                    return
                else:
                    # I am using json right now to pack the list of matching photos, maybe there is a better way
                    json_data = json.dumps(result)
                    client_socket.send(json_data.encode())
            else:
                client_socket.send(b"Error: Target face image not found")

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

