import sqlite3


def init_db():
    conn = sqlite3.connect('reports.db')
    c = conn.cursor()
    c.execute('''
              CREATE TABLE IF NOT EXISTS reports
              (
                  id
                  INTEGER
                  PRIMARY
                  KEY
                  AUTOINCREMENT,
                  smoke_type
                  TEXT
                  NOT
                  NULL,
                  location
                  TEXT
                  NOT
                  NULL,
                  description
                  TEXT,
                  photo_path
                  TEXT,
                  status
                  TEXT
                  DEFAULT
                  'pending',
                  timestamp
                  DATETIME
                  DEFAULT
                  CURRENT_TIMESTAMP
              )
              ''')

    # Add 'name' column if not exists
    c.execute("PRAGMA table_info(reports)")
    columns = [col[1] for col in c.fetchall()]
    if "name" not in columns:
        c.execute("ALTER TABLE reports ADD COLUMN name TEXT")

    conn.commit()
    conn.close()


def insert_report(name, smoke_type, location, description, photo_path):
    conn = sqlite3.connect('reports.db')
    c = conn.cursor()
    c.execute('''
              INSERT INTO reports (name, smoke_type, location, description, photo_path)
              VALUES (?, ?, ?, ?, ?)
              ''', (name, smoke_type, location, description, photo_path))
    conn.commit()
    conn.close()


def update_status(report_id, new_status):
    conn = sqlite3.connect('reports.db')
    c = conn.cursor()
    c.execute("UPDATE reports SET status = ? WHERE id = ?", (new_status, report_id))
    conn.commit()
    conn.close()
