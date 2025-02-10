from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import bcrypt

app = Flask(__name__)

# ✅ Database connection function
def get_db_connection():
    conn = sqlite3.connect('database.db')  # Connect to SQLite database
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn  

# ✅ Create users table if it doesn't exist
def create_table():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS food_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

# ✅ Initialize database
create_table()

# Home route (index page)
@app.route('/')
def index():
    return render_template('index.html')

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        if password == confirm_password:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            conn = get_db_connection()
            cur = conn.cursor()
            
            # Check if email already exists
            cur.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cur.fetchone()

            if user:
                conn.close()
                return render_template('signup.html', error="Email already registered!")
            else:
                # Insert new user
                cur.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed_password))
                conn.commit()
                conn.close()

                print(f"User signed up with email {email}")
                return redirect(url_for('login'))
        else:
            return render_template('signup.html', error="Passwords do not match!")

    return render_template('signup.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cur.fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):  
            return redirect(url_for('index'))  
        else:
            return render_template('login.html', error="Invalid credentials!")

    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
