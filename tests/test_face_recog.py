from utils.camera import Camera
from utils.face_recog import FaceRecognition
from models.database import Database
import cv2

print("Starting face rec test...")
cam = Camera()
frame = cam.get_frame()
if frame is None:
    print("No camera frame available. Is the camera free and allowed? Test aborted.")
else:
    print("Captured frame shape:", frame.shape)
    db = Database()
    fr = FaceRecognition(db)
    # Try to find faces and encodings
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    faces = fr
    encs = None
    try:
        encs = __import__('face_recognition').face_encodings(rgb)
    except Exception as e:
        print("face_recognition failed:", e)
    if encs and len(encs) > 0:
        print("Found face encodings. Length:", len(encs))
    else:
        print("No faces detected in captured frame.")

print("Test finished.")