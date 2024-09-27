import sqlite3
import face_recognition
import numpy as np

class FaceRecognitionDB:
    def __init__(self, db_name='face_recognition.db'):
        # Initialize the connection to the SQLite database
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def create_table(self):
        # Create the encoded_faces table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS encoded_faces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                college_id TEXT,
                role TEXT,
                image BLOB
            )
        ''')
        self.conn.commit()

    def insert_encoded_face(self, name, college_id, role, face_blob):
        # Insert the encoded face into the encoded_faces table
        self.cursor.execute('''
            INSERT INTO encoded_faces (name, college_id, role, image)
            VALUES (?, ?, ?, ?)
        ''', (name, college_id, role, face_blob))
        self.conn.commit()

    def close_connection(self):
        # Close the database connection
        self.conn.close()

class FaceEncoder:
    @staticmethod
    def encode_face(image_path):
        # Load the image and return the face encoding if a face is detected
        image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(image)
        
        if len(face_encodings) > 0:
            print(f"{len(face_encodings)} face(s) detected.")
            return face_encodings[0]  # Return the first encoding
        else:
            print("No faces detected in the image.")
            return None

    @staticmethod
    def face_encoding_to_blob(face_encoding):
        # Convert the face encoding to BLOB format
        return face_encoding.tobytes()

class FaceRecognitionApp:
    def __init__(self):
        # Initialize the database and ensure the table is created
        self.db = FaceRecognitionDB()
        self.db.create_table()

    def run(self):
        # Get user inputs
        name = input("Enter name: ")
        college_id = input("Enter college ID: ")
        role = input("Enter role: ")
        image_path = input("Enter the path to the image file: ")

        # Encode the face from the provided image
        try:
            face_encoding = FaceEncoder.encode_face(image_path)
            
            if face_encoding is not None:
                # Convert face encoding to BLOB format and insert into database
                face_blob = FaceEncoder.face_encoding_to_blob(face_encoding)
                self.db.insert_encoded_face(name, college_id, role, face_blob)
                print("Data inserted successfully into encoded_faces table.")
            else:
                print("No data inserted because no faces were detected.")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            # Close the database connection after operation
            self.db.close_connection()

# Run the application
if __name__ == '__main__':
    app = FaceRecognitionApp()
    app.run()
