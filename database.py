import sqlite3

# Connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('face_recognition.db')
cursor = conn.cursor()

# Create encoded_faces table
cursor.execute('''
CREATE TABLE IF NOT EXISTS encoded_faces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    college_id TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL,
    image BLOB NOT NULL
)
''')

# Modify the attendance table to add blob for unknown faces
cursor.execute('''
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    college_id TEXT NOT NULL,
    role TEXT NOT NULL,
    time_in DATETIME DEFAULT CURRENT_TIMESTAMP,
    time_out DATETIME,
    image BLOB
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()
