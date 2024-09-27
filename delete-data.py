import sqlite3

class FaceRecognitionDatabase:
    def __init__(self, db_name='face_recognition.db'):
        self.db_name = db_name

    # Method to establish a connection to the database
    def connect(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    # Method to close the connection to the database
    def close(self):
        if self.conn:
            self.conn.close()

    # Method to delete all records from both tables
    def delete_all_data(self):
        try:
            self.connect()
            # Delete all records from the encoded_faces table
            self.cursor.execute('DELETE FROM encoded_faces')
            # Delete all records from the attendance table
            self.cursor.execute('DELETE FROM attendance')

            # Commit the changes
            self.conn.commit()
            print("All data has been deleted from the database.")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            self.close()

# Instantiate the class and call the method to delete all data
db_manager = FaceRecognitionDatabase()
db_manager.delete_all_data()
