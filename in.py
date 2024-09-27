import cv2
import numpy as np
import sqlite3
import face_recognition

# Class for handling database operations
class FaceRecognitionDB:
    def __init__(self, db_name='face_recognition.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def load_encoded_faces(self):
        # Load the encoded faces from the database
        self.cursor.execute("SELECT name, college_id, role, image FROM encoded_faces")
        rows = self.cursor.fetchall()

        encoded_faces = []
        names = []
        college_ids = []
        roles = []

        for row in rows:
            name = row[0]
            college_id = row[1]
            role = row[2]
            image_blob = row[3]

            # Convert BLOB back to numpy array
            face_encoding = np.frombuffer(image_blob, dtype=np.float64)

            encoded_faces.append(face_encoding)
            names.append(name)
            college_ids.append(college_id)
            roles.append(role)

        return encoded_faces, names, college_ids, roles

    def save_attendance(self, name, college_id, role, image_blob=None):
        # Save the attendance entry into the database
        self.cursor.execute("SELECT * FROM attendance WHERE name=? AND college_id=? AND time_out IS NULL", 
                            (name, college_id))
        existing_entry = self.cursor.fetchone()

        # Insert new attendance entry if not found
        if not existing_entry:
            self.cursor.execute("INSERT INTO attendance (name, college_id, role, image) VALUES (?, ?, ?, ?)", 
                                (name, college_id, role, image_blob))
        self.conn.commit()

    def close(self):
        # Close the database connection
        self.conn.close()


# Class for handling face recognition from video
class FaceRecognitionInCamera:
    def __init__(self, db: FaceRecognitionDB, video_path):
        self.db = db
        self.video_path = video_path
        self.encoded_faces, self.names, self.college_ids, self.roles = self.db.load_encoded_faces()

    def recognize_faces(self):
        # Open video file
        video_capture = cv2.VideoCapture(self.video_path)

        while True:
            ret, frame = video_capture.read()
            if not ret:
                break

            # Process frame for face recognition
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(self.encoded_faces, face_encoding)
                name, college_id, role = "Unknown", "", ""

                if True in matches:
                    first_match_index = matches.index(True)
                    name = self.names[first_match_index]
                    college_id = self.college_ids[first_match_index]
                    role = self.roles[first_match_index]
                else:
                    # If no match, save the unknown face
                    unknown_face_image = frame[top:bottom, left:right]
                    _, img_encoded = cv2.imencode('.jpg', unknown_face_image)
                    image_blob = img_encoded.tobytes()
                    self.db.save_attendance("Unknown", "Unknown", "Unknown", image_blob)

                self.db.save_attendance(name, college_id, role)

                # Draw bounding box and label on the frame
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                label = f"{name} (ID: {college_id}, Role: {role})"
                cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            # Show the video frame
            cv2.imshow('In Camera', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        video_capture.release()
        cv2.destroyAllWindows()


# Main class to manage the face recognition and attendance process
class FaceRecognitionApp:
    def __init__(self, video_path_in):
        self.db = FaceRecognitionDB()
        self.face_recognizer_in = FaceRecognitionInCamera(self.db, video_path_in)

    def run(self):
        try:
            self.face_recognizer_in.recognize_faces()
        finally:
            self.db.close()


# Run the application
if __name__ == '__main__':
    video_path_in = "/home/kareem/fr-tasks/attendance2/whatsapp.mp4"  # Update with your video file path
    app = FaceRecognitionApp(video_path_in)
    app.run()
