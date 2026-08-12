from sqlite3 import connect

def init_db():
    conn = connect('trade_data.db')
    cursor = conn.cursor()
    
    # Create signals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            price REAL,
            rsi REAL,
            ema_20 REAL,
            ema_50 REAL,
            signal TEXT,
            reason TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
