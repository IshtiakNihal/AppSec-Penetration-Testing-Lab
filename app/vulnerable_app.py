#!/usr/bin/env python3
"""
VULNERABLE Web Application - Project C Phase 1
Contains 15 intentional OWASP Top 10 vulnerabilities
Built with Flask + PostgreSQL

DO NOT USE IN PRODUCTION - Educational purposes only
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import secrets
import jwt
import logging
from datetime import datetime, timedelta
import requests
import xml.etree.ElementTree as ET
import sqlite3
from functools import wraps

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'insecure-secret-key-change-me'  # VULNERABILITY: Hardcoded secret
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vulnerable.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SECURE'] = False  # VULNERABILITY: No secure flag
app.config['SESSION_COOKIE_HTTPONLY'] = False  # VULNERABILITY: Accessible to JS

db = SQLAlchemy(app)

# ============================================
# DATABASE MODELS
# ============================================

class User(db.Model):
    """User model with intentional vulnerabilities"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # VULNERABILITY: Weak hashing
    role = db.Column(db.String(50), default='user')  # VULNERABILITY: Mass assignment
    account_balance = db.Column(db.Float, default=1000)
    api_key = db.Column(db.String(255))  # VULNERABILITY: Exposed in API
    
    def __repr__(self):
        return f'<User {self.username}>'


class Product(db.Model):
    """Product model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    file_path = db.Column(db.String(255))  # VULNERABILITY: Path traversal vector


class Comment(db.Model):
    """Comment model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    text = db.Column(db.Text)  # VULNERABILITY: No sanitization, allows XSS
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ============================================
# VULNERABILITY #1-2: SQL INJECTION
# ============================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    VULNERABILITY #1-2: SQL Injection (Blind + Error-based)
    Directly concatenates user input into SQL query
    """
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        # VULNERABILITY: Direct string concatenation - SQL injection
        query = f"SELECT * FROM user WHERE username='{username}' AND password='{password}'"
        logger.warning(f"Executing: {query}")  # Log the vulnerable query for demonstration
        
        # Execute vulnerable query
        try:
            user = db.session.execute(db.text(query)).fetchone()
            if user:
                session['user_id'] = user[0]
                return redirect(url_for('dashboard'))
        except Exception as e:
            # VULNERABILITY: Error message reveals database structure
            return f"Database Error: {str(e)}", 500
        
        return "Invalid credentials", 401
    
    return '''
    <form method="POST">
        <input type="text" name="username" placeholder="Username">
        <input type="password" name="password" placeholder="Password">
        <button type="submit">Login</button>
    </form>
    '''


# ============================================
# VULNERABILITY #3: BROKEN AUTHENTICATION (JWT None Algorithm)
# ============================================

@app.route('/api/auth/token', methods=['POST'])
def get_token():
    """
    VULNERABILITY #3: JWT with 'none' algorithm
    Allows forging tokens without signature
    """
    username = request.json.get('username')
    password = request.json.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        # VULNERABILITY: JWT with 'none' algorithm
        token = jwt.encode(
            {
                'sub': username,
                'role': user.role,
                'exp': datetime.utcnow() + timedelta(hours=24)
            },
            options={"algorithm": "none"}  # CRITICAL: None algorithm
        )
        return jsonify({'token': token})
    return jsonify({'error': 'Invalid credentials'}), 401


# ============================================
# VULNERABILITY #4: IDOR (Insecure Direct Object Reference)
# ============================================

@app.route('/user/profile/<int:user_id>')
def user_profile(user_id):
    """
    VULNERABILITY #4: IDOR
    No authorization check - any user can view any profile
    """
    # VULNERABILITY: No permission check
    user = User.query.get(user_id)
    if user:
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'account_balance': user.account_balance,  # Exposed sensitive data
            'api_key': user.api_key  # VULNERABILITY: API key exposed
        })
    return jsonify({'error': 'User not found'}), 404


# ============================================
# VULNERABILITY #5: CSRF (Cross-Site Request Forgery)
# ============================================

@app.route('/transfer', methods=['POST'])
def transfer_funds():
    """
    VULNERABILITY #5: CSRF
    No CSRF token validation
    """
    if 'user_id' not in session:
        return "Unauthorized", 401
    
    recipient = request.form.get('recipient')
    amount = float(request.form.get('amount', 0))
    
    # VULNERABILITY: No CSRF token check
    user = User.query.get(session['user_id'])
    if user and user.account_balance >= amount:
        user.account_balance -= amount
        # In real scenario, would transfer to recipient
        db.session.commit()
        return f"Transferred ${amount} to {recipient}"
    
    return "Transfer failed", 400


# ============================================
# VULNERABILITY #6: REFLECTED XSS
# ============================================

@app.route('/search')
def search():
    """
    VULNERABILITY #6: Reflected XSS
    Directly echoes user input in HTML
    """
    query = request.args.get('q', '')
    
    # VULNERABILITY: No HTML escaping
    return f'''
    <h1>Search Results</h1>
    <p>You searched for: {query}</p>
    <p>Found 0 results</p>
    '''


# ============================================
# VULNERABILITY #7: STORED XSS
# ============================================

@app.route('/comments', methods=['GET', 'POST'])
def comments():
    """
    VULNERABILITY #7: Stored XSS
    Comments are stored and displayed without sanitization
    """
    if request.method == 'POST':
        if 'user_id' not in session:
            return "Unauthorized", 401
        
        text = request.form.get('text', '')
        
        # VULNERABILITY: No sanitization or encoding
        comment = Comment(user_id=session['user_id'], text=text)
        db.session.add(comment)
        db.session.commit()
        
        return redirect(url_for('comments'))
    
    # VULNERABILITY: Render comments without escaping
    all_comments = Comment.query.all()
    html = '<h1>Comments</h1><form method="POST"><textarea name="text"></textarea><button>Post</button></form>'
    html += '<div id="comments">'
    for comment in all_comments:
        html += f'<p>{comment.text}</p>'  # No escaping!
    html += '</div>'
    return html


# ============================================
# VULNERABILITY #8: DOM XSS
# ============================================

@app.route('/settings')
def settings():
    """
    VULNERABILITY #8: DOM XSS
    Client-side DOM manipulation without sanitization
    """
    color = request.args.get('color', 'blue')
    
    return f'''
    <html>
    <body style="color: {color}">
    <h1>Theme Settings</h1>
    <p>Choose your theme color:</p>
    <div id="preview" style="color: {color}">Preview</div>
    <script>
        document.getElementById('preview').style.color = "{color}";
    </script>
    </body>
    </html>
    '''


# ============================================
# VULNERABILITY #9: ARBITRARY FILE UPLOAD RCE
# ============================================

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """
    VULNERABILITY #9: File Upload RCE
    No file type validation, executes uploaded files
    """
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part", 400
        
        file = request.files['file']
        
        # VULNERABILITY: No validation of file type
        filename = file.filename
        upload_dir = 'uploads'
        
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        # VULNERABILITY: Saves any file type, including executables
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        return f"File uploaded: {filename}"
    
    return '''
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="file">
        <button type="submit">Upload</button>
    </form>
    '''


# ============================================
# VULNERABILITY #10: PATH TRAVERSAL
# ============================================

@app.route('/download')
def download():
    """
    VULNERABILITY #10: Path Traversal
    No validation of file path parameter
    """
    filename = request.args.get('file', '')
    
    # VULNERABILITY: No path sanitization
    filepath = os.path.join('uploads', filename)
    
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    
    return "File not found", 404


# ============================================
# VULNERABILITY #11: XXE (XML External Entity)
# ============================================

@app.route('/api/xmlparser', methods=['POST'])
def xmlparser():
    """
    VULNERABILITY #11: XXE Injection
    Parses XML without disabling external entities
    """
    xml_data = request.data
    
    # VULNERABILITY: Parses XML without disabling XXE
    try:
        root = ET.fromstring(xml_data)  # No XXE protection
        return jsonify({'status': 'success', 'data': ET.tostring(root).decode()})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ============================================
# VULNERABILITY #12: SSRF (Server-Side Request Forgery)
# ============================================

@app.route('/fetch')
def fetch_url():
    """
    VULNERABILITY #12: SSRF
    Fetches URLs without validation
    """
    url = request.args.get('url', '')
    
    # VULNERABILITY: Fetches any URL without validation
    try:
        response = requests.get(url, timeout=5)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}", 400


# ============================================
# VULNERABILITY #13: MASS ASSIGNMENT
# ============================================

@app.route('/api/profile', methods=['POST'])
def update_profile():
    """
    VULNERABILITY #13: Mass Assignment
    Accepts all request parameters without validation
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get(session['user_id'])
    
    # VULNERABILITY: Mass assignment - accepts any parameter
    for key, value in request.json.items():
        if hasattr(user, key):
            setattr(user, key, value)  # Allows changing role, API key, etc.
    
    db.session.commit()
    return jsonify({'status': 'success'})


# ============================================
# VULNERABILITY #14: BROKEN RATE LIMITING
# ============================================

login_attempts = {}

@app.route('/api/login', methods=['POST'])
def api_login():
    """
    VULNERABILITY #14: Broken Rate Limiting
    No protection against brute force
    """
    username = request.json.get('username')
    password = request.json.get('password')
    
    # VULNERABILITY: No rate limiting
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return jsonify({'token': 'valid_token_here'})
    
    return jsonify({'error': 'Invalid credentials'}), 401


# ============================================
# VULNERABILITY #15: SENSITIVE DATA EXPOSURE
# ============================================

@app.route('/api/users')
def get_users():
    """
    VULNERABILITY #15: Sensitive Data Exposure
    Exposes sensitive data in API response
    """
    users = User.query.all()
    
    # VULNERABILITY: Exposes sensitive data
    return jsonify([{
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'password': u.password,  # Never expose passwords!
        'api_key': u.api_key,  # Never expose API keys!
        'account_balance': u.account_balance,
        'role': u.role
    } for u in users])


# ============================================
# GENERAL ROUTES
# ============================================

@app.route('/')
def index():
    """Homepage"""
    return '''
    <h1>Vulnerable Web Application Lab</h1>
    <p>This is an intentionally vulnerable application for security testing.</p>
    <nav>
        <a href="/login">Login</a> |
        <a href="/search">Search</a> |
        <a href="/comments">Comments</a> |
        <a href="/upload">Upload</a> |
        <a href="/api/users">Users API</a> |
        <a href="/register">Register</a>
    </nav>
    '''


@app.route('/dashboard')
def dashboard():
    """User dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if user:
        return f'''
        <h1>Dashboard</h1>
        <p>Welcome, {user.username}!</p>
        <p>Account Balance: ${user.account_balance}</p>
        <a href="/logout">Logout</a>
        '''
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            return "Username already exists", 400
        
        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            api_key=secrets.token_hex(16)
        )
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('login'))
    
    return '''
    <form method="POST">
        <input type="text" name="username" placeholder="Username" required>
        <input type="email" name="email" placeholder="Email" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Register</button>
    </form>
    '''


@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('index'))


# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    return "Page not found", 404


@app.errorhandler(500)
def internal_error(error):
    # VULNERABILITY: Exposes stack trace
    import traceback
    return f"<pre>{traceback.format_exc()}</pre>", 500


# ============================================
# INITIALIZATION
# ============================================

def init_db():
    """Initialize database with sample data"""
    with app.app_context():
        db.create_all()
        
        # Add sample users
        if User.query.count() == 0:
            admin = User(
                username='admin',
                email='admin@example.com',
                password=generate_password_hash('admin123'),
                role='admin',
                account_balance=100000,
                api_key='sk-admin-key-12345'
            )
            user1 = User(
                username='alice',
                email='alice@example.com',
                password=generate_password_hash('alice123'),
                role='user',
                account_balance=5000,
                api_key='sk-alice-key-67890'
            )
            user2 = User(
                username='bob',
                email='bob@example.com',
                password=generate_password_hash('bob123'),
                role='user',
                account_balance=12500,
                api_key='sk-bob-key-99999'
            )
            
            db.session.add_all([admin, user1, user2])
            db.session.commit()
            
            logger.info("Database initialized with sample data")


if __name__ == '__main__':
    init_db()
    logger.info("Starting vulnerable Flask application on 0.0.0.0:5000")
    logger.warning("WARNING: This application contains intentional vulnerabilities!")
    logger.warning("DO NOT USE IN PRODUCTION")
    app.run(host='0.0.0.0', port=5000, debug=True)
