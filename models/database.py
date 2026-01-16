import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name="attendance.db"):
        self.db_name = db_name
        self.create_tables()

    def connect(self):
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        with self.connect() as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                roll_number TEXT UNIQUE NOT NULL,
                department TEXT,
                face_encoding BLOB
                
            )''')
            c.execute('''CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                date TEXT,
                time TEXT,
                status TEXT,
                FOREIGN KEY (student_id) REFERENCES students(id)
            )''')
            conn.commit()

    def add_student(self, name, roll, dept, encoding):
        with self.connect() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO students (name, roll_number, department, face_encoding) VALUES (?, ?, ?, ?)",
                      (name, roll, dept, encoding))
            conn.commit()
            return c.lastrowid

    def get_all_students(self):
        with self.connect() as conn:
            return conn.execute("SELECT * FROM students").fetchall()

    def get_student_by_id(self, student_id):
        with self.connect() as conn:
            return conn.execute("SELECT * FROM students WHERE id=?", (student_id,)).fetchone()

    def mark_attendance(self, student_id, status="Present"):
        today = datetime.now().strftime("%Y-%m-%d")
        now = datetime.now().strftime("%H:%M:%S")
        with self.connect() as conn:
            c = conn.cursor()
            exists = c.execute("SELECT * FROM attendance WHERE student_id=? AND date=?", 
                               (student_id, today)).fetchone()
            if not exists:
                c.execute("INSERT INTO attendance (student_id, date, time, status) VALUES (?, ?, ?, ?)",
                          (student_id, today, now, status))
                conn.commit()
