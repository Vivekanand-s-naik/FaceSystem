import face_recognition
import numpy as np
import cv2
import pickle

class FaceRecognition:
    def __init__(self, db):
        self.db = db
        self.known_encodings = []
        self.known_names = []
        self.load_encodings()

    def load_encodings(self):
        # Clear existing in-memory encodings before loading from DB
        self.known_encodings = []
        self.known_names = []
        students = self.db.get_all_students()
        for s in students:
            if s[4] is not None:
                encoding = pickle.loads(s[4])
                self.known_encodings.append(encoding)
                self.known_names.append((s[0], s[1]))  # id, name

    def add_encoding(self, student_id, name, encoding):
        """Add a single encoding to memory to allow immediate recognition without reloading DB."""
        self.known_encodings.append(encoding)
        self.known_names.append((student_id, name))

    def remove_encoding(self, student_id):
        """Remove a student's encoding from memory."""
        for i, (sid, name) in enumerate(self.known_names):
            if sid == student_id:
                del self.known_encodings[i]
                del self.known_names[i]
                break

    def recognize_face(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = face_recognition.face_locations(rgb_frame)
        encodings = face_recognition.face_encodings(rgb_frame, faces)
        for enc in encodings:
            matches = face_recognition.compare_faces(self.known_encodings, enc)
            face_dist = face_recognition.face_distance(self.known_encodings, enc)
            if len(face_dist) > 0:
                best_match = np.argmin(face_dist)
                if matches[best_match]:
                    student_id, name = self.known_names[best_match]
                    return student_id, name
        return None, None
