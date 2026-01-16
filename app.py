from flask import Flask, render_template, Response, jsonify, request, redirect, url_for, session
import cv2, pickle
from models.database import Database
from utils.face_recog import FaceRecognition
from utils.camera import Camera
import face_recognition

app = Flask(__name__)
app.secret_key = "supersecretkey"

db = Database()
face_recog = FaceRecognition(db)
camera = Camera()

@app.route('/')
def root():
    return redirect(url_for('login'))

@app.route('/index')
def index():
    return render_template('index_v2.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        roll = request.form['roll']
        dept = request.form['department']

        # Capture one frame from webcam
        frame = camera.get_frame()
        if frame is None:
            return render_template('register_v2.html', message="Could not access camera. Try again.")
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = face_recognition.face_encodings(rgb)
        if faces:
            enc = pickle.dumps(faces[0])
            student_id = db.add_student(name, roll, dept, enc)
            # Add encoding in-memory so the new student can be recognized immediately
            face_recog.add_encoding(student_id, name, faces[0])
            return render_template('register_v2.html', message="Student Registered Successfully!")
        else:
            return render_template('register_v2.html', message="No face detected!")
    return render_template('register_v2.html')


@app.route('/students')
def students():
    all_students = db.get_all_students()
    result = []
    for s in all_students:
        result.append({
            'id': s[0],
            'name': s[1],
            'roll': s[2],
            'department': s[3],
            'present': 'Present' if s[0] in present else 'Absent'
        })
    return jsonify(result)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Simple hardcoded admin credentials
        if username == "admin" and password == "12345":
            session['user'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login_v2.html', message="Invalid credentials. Try again.")
    return render_template('login_v2.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

present = dict()
@app.route('/video_feed')
def video_feed():
    def gen():
        while True:
            frame = camera.get_frame()
            if frame is None:
                continue
            student_id, name = face_recog.recognize_face(frame)
            if student_id:
                present[student_id] = True
                db.mark_attendance(student_id, 'present')
                cv2.putText(frame, f"Marked Present: {name}", (30, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            ret, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/attendance')
def attendance():
    records = db.get_all_students()
    print(type(records))
    return jsonify(records)

@app.route('/clear_session', methods=['POST'])
def clear_session():
    """Clear the in-memory attendance session (reset present dictionary)"""
    global present
    present = dict()
    return jsonify({'status': 'success', 'message': 'Session cleared successfully'})

@app.route('/delete_student/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Delete a student and their attendance records"""
    try:
        db.delete_student(student_id)
        # Remove from in-memory present dict if exists
        if student_id in present:
            del present[student_id]
        # Remove encoding from face_recog
        face_recog.remove_encoding(student_id)
        return jsonify({'status': 'success', 'message': 'Student deleted successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
