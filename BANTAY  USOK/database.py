import sqlite3

def init_db():
    conn = sqlite3.connect('reports.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            smoke_type TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT,
            photo_path TEXT,
            status TEXT DEFAULT 'pending',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def insert_report(smoke_type, location, description, photo_path):
    conn = sqlite3.connect('reports.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO reports (smoke_type, location, description, photo_path)
        VALUES (?, ?, ?, ?)
    ''', (smoke_type, location, description, photo_path))
    conn.commit()
    conn.close()

def update_status(report_id, new_status):
    conn = sqlite3.connect('reports.db')
    c = conn.cursor()
    c.execute("UPDATE reports SET status = ? WHERE id = ?", (new_status, report_id))
    conn.commit()
    conn.close()
