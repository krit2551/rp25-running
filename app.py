from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'rp25_running_secret_key'  # จำเป็นต้องใช้เพื่อระบบเซสชันล็อกอิน

# ฟังก์ชันจัดการเชื่อมต่อฐานข้อมูล SQLite
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# ฟังก์ชันสร้างตารางฐานข้อมูล
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dorm_name TEXT NOT NULL,
            punctuality INTEGER DEFAULT 0,
            round1 INTEGER DEFAULT 0,
            round2 INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# รายชื่อหอนอนทั้งหมด
DORMS = [
    {'id': 'dorm1_b', 'name': 'หอนอน 1 ชาย'},
    {'id': 'dorm2_b', 'name': 'หอนอน 2 ชาย'},
    {'id': 'dorm3_b', 'name': 'หอนอน 3 ชาย'},
    {'id': 'dorm4_b', 'name': 'หอนอน 4 ชาย'},
    {'id': 'dorm5_b', 'name': 'หอนอน 5 ชาย'},
    {'id': 'dorm6_b', 'name': 'หอนอน 6 ชาย'},
    {'id': 'dorm1_g', 'name': 'หอนอน 1 หญิง'},
    {'id': 'dorm2_g', 'name': 'หอนอน 2 หญิง'},
    {'id': 'dorm3_g', 'name': 'หอนอน 3 หญิง'},
    {'id': 'dorm4_g', 'name': 'หอนอน 4 หญิง'},
    {'id': 'dorm5_g', 'name': 'หอนอน 5 หญิง'},
    {'id': 'dorm6_g', 'name': 'หอนอน 6 หญิง'},
    {'id': 'dorm7_g', 'name': 'หอนอน 7 หญิง'}
]

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # ตรวจสอบชื่อผู้ใช้และรหัสผ่านตรงนี้
        if username == 'admin' and password == 'rp25run':
            session['logged_in'] = True  # บันทึกสถานะว่าล็อกอินแล้ว
            return redirect(url_for('score'))
        else:
            return render_template('login.html', error="ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
            
    return render_template('login.html')

@app.route('/score', methods=['GET', 'POST'])
def score():
    # ป้องกันไม่ให้คนที่ไม่ได้ล็อกอินแอบเข้ามาหน้าฟอร์มกรอกคะแนน
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        conn = get_db_connection()
        for dorm in DORMS:
            punc = request.form.get(f"punc_{dorm['id']}", type=int, default=0)
            r1 = request.form.get(f"r1_{dorm['id']}", type=int, default=0)
            r2 = request.form.get(f"r2_{dorm['id']}", type=int, default=0)
            
            conn.execute('''
                INSERT INTO scores (dorm_name, punctuality, round1, round2)
                VALUES (?, ?, ?, ?)
            ''', (dorm['name'], punc, r1, r2))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
        
    return render_template('score.html', dorms=DORMS)

@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    results = conn.execute('''
        SELECT dorm_name, 
               ROUND(AVG(punctuality), 2) as avg_punc, 
               ROUND(AVG(round1), 2) as avg_r1, 
               ROUND(AVG(round2), 2) as avg_r2,
               ROUND((AVG(punctuality) + AVG(round1) + AVG(round2)), 2) as total
        FROM scores
        GROUP BY dorm_name
        ORDER BY total DESC
    ''').fetchall()
    conn.close()
    return render_template('dashboard.html', summary=results)

@app.route('/logout')
def logout():
    session.clear() # ล้างสถานะล็อกอิน
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
