#!/usr/bin/env python3
"""
VULNERABLE Web Application - Project C Phase 1 (SIMPLIFIED)
Contains core OWASP Top 10 vulnerabilities for demonstration
Built with Flask + SQLite

DO NOT USE IN PRODUCTION - Educational purposes only
"""

from flask import Flask, request, jsonify, render_template_string
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'insecure-secret-key'  # VULNERABILITY: Hardcoded secret

DB_PATH = 'vulnerable.db'

def init_db():
    """Initialize SQLite database with sample data"""
    if os.path.exists(DB_PATH):
        return
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create users table
    c.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT,
            api_key TEXT
        )
    ''')
    
    # Insert sample users  
    c.execute("INSERT INTO users VALUES (1, 'admin', 'admin123', 'admin@app.com', 'secret-api-key-123')")
    c.execute("INSERT INTO users VALUES (2, 'user1', 'password1', 'user1@app.com', 'user-api-key-456')")
    c.execute("INSERT INTO users VALUES (3, 'user2', 'password2', 'user2@app.com', 'user-api-key-789')")
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """Home page"""
    html = '''
    <html>
    <head><title>Vulnerable App - Project C</title></head>
    <body>
        <h1>Vulnerable Web Application Lab</h1>
        <p>Project C - AppSec Exploitation Lab</p>
        <h2>Vulnerable Endpoints:</h2>
        <ul>
            <li><a href="/login">Login (SQL Injection)</a></li>
            <li><a href="/user/1">User Profile /user/1 (IDOR)</a></li>
            <li><a href="/user/2">User Profile /user/2 (IDOR)</a></li>
            <li><a href="/search?q=test">Search (Reflected XSS)</a></li>
            <li><a href="/api/users">API Users (Sensitive Data)</a></li>
        </ul>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login endpoint with SQL injection vulnerability"""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        # VULNERABILITY: SQL Injection - direct string concatenation
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute(query)
            user = c.fetchone()
            conn.close()
            
            if user:
                return f"<h2>Welcome {user[1]}!</h2><p>Email: {user[3]}</p><p>API Key: {user[4]}</p>"
            else:
                return "<h2>Login Failed</h2>"
        except Exception as e:
            # VULNERABILITY: Error-based SQL Injection - shows error to attacker
            return f"<h2>Error:</h2><p>{str(e)}</p>"
    
    html = '''
    <html>
    <body>
        <h2>Login</h2>
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        <p>Try: admin' OR '1'='1</p>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/user/<int:user_id>')
def user_profile(user_id):
    """User profile endpoint with IDOR vulnerability"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = c.fetchone()
    conn.close()
    
    if user:
        # VULNERABILITY: IDOR - returns sensitive data without authorization check
        html = f'''
        <html>
        <body>
            <h2>User Profile</h2>
            <p>Username: {user[1]}</p>
            <p>Email: {user[2]}</p>
            <p>API Key: {user[4]}</p>
            <p><a href="/user/1">User 1</a> | <a href="/user/2">User 2</a> | <a href="/user/3">User 3</a></p>
        </body>
        </html>
        '''
        return render_template_string(html)
    return "User not found", 404

@app.route('/search')
def search():
    """Search endpoint with reflected XSS"""
    query = request.args.get('q', '')
    
    # VULNERABILITY: Reflected XSS - user input directly in HTML
    html = f'''
    <html>
    <body>
        <h2>Search Results for: {query}</h2>
        <p>No results found for your search.</p>
        <form action="/search" method="GET">
            <input type="text" name="q" placeholder="Search...">
            <button type="submit">Search</button>
        </form>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/api/users')
def api_users():
    """API endpoint with sensitive data exposure"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    conn.close()
    
    # VULNERABILITY: Sensitive Data Exposure - returns passwords and API keys
    users_list = []
    for user in users:
        users_list.append({
            'id': user[0],
            'username': user[1],
            'password': user[2],  # EXPOSED!
            'email': user[3],
            'api_key': user[4]  # EXPOSED!
        })
    
    return jsonify(users_list)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'running', 'app': 'Vulnerable App - Project C'})

if __name__ == '__main__':
    init_db()
    print("=" * 50)
    print("Vulnerable Web Application - Project C")
    print("=" * 50)
    print("\n✓ Flask app starting on http://127.0.0.1:5000")
    print("\nVulnerable endpoints:")
    print("  - /login (SQL Injection)")
    print("  - /user/1, /user/2 (IDOR)")
    print("  - /search?q=test (Reflected XSS)")
    print("  - /api/users (Sensitive Data Exposure)")
    print("\nPress Ctrl+C to stop\n")
    print("=" * 50)
    
    app.run(host='127.0.0.1', port=5000, debug=False)
