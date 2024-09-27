import cv2
import numpy as np
import sqlite3
import face_recognition
from datetime import datetime


class FaceRecognitionSystem:
    def __init__(self, db_path):
        self.db_path = db_path
        self.encoded_faces, self.names, self.college_ids, self.roles = self.load_encoded_faces()

    def load_encoded_faces(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name, college_id, role, image FROM encoded_faces")
        rows = cursor.fetchall()

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

        conn.close()
        return encoded_faces, names, college_ids, roles

    def save_time_out(self, name, college_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE attendance SET time_out=? WHERE name=? AND college_id=? AND time_out IS NULL",
            (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), name, college_id)
        )

        conn.commit()
        conn.close()

    def check_and_save_unknown_face(self, frame, face_encoding):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM attendance WHERE name='Unknown'")
        result = cursor.fetchone()[0]

        if result == 0:
            _, buffer = cv2.imencode('.jpg', frame)
            face_blob = buffer.tobytes()

            cursor.execute(
                '''
                INSERT INTO attendance (name, college_id, role, time_in, image)
                VALUES (?, ?, ?, ?, ?)
                ''',
                ('Unknown', 'N/A', 'N/A', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), face_blob)
            )

        conn.commit()
        conn.close()

    def recognize_faces_in_video(self, video_path):
        video_capture = cv2.VideoCapture(video_path)

        while True:
            ret, frame = video_capture.read()
            if not ret:
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(self.encoded_faces, face_encoding)
                name = "Unknown"
                college_id = ""
                role = ""

                if True in matches:
                    first_match_index = matches.index(True)
                    name = self.names[first_match_index]
                    college_id = self.college_ids[first_match_index]
                    role = self.roles[first_match_index]

                    self.save_time_out(name, college_id)
                else:
                    self.check_and_save_unknown_face(frame[top:bottom, left:right], face_encoding)

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                label = f"{name} (ID: {college_id}, Role: {role})"
                cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

            cv2.imshow('Out Camera', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        video_capture.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    db_path = 'face_recognition.db'
    video_path_out = "/home/kareem/fr-tasks/attendance2/whatsapp.mp4"  # Update with your video file path

    face_recognition_system = FaceRecognitionSystem(db_path)
    face_recognition_system.recognize_faces_in_video(video_path_out)
