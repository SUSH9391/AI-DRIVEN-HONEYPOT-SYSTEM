import os
import json
import time
import datetime
import sqlite3
import re
import random
from flask import Flask, request, render_template, redirect, jsonify, session
from dotenv import load_dotenv
import requests
from honeypot_system_hf_merged import HoneypotDiscriminator, HoneypotHFGenerator
from products import generate_products

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Initialize discriminator and generator with HF API key from env
HF_API_KEY = os.getenv("HF_API_KEY")
discriminator = HoneypotDiscriminator(threshold=0.8)
generator = HoneypotHFGenerator(api_key=HF_API_KEY)

LOG_FILE = "attack_logs.json"

# In-memory database for the honeypot
fake_users = []
fake_orders = []
fake_customers = []

def log_attack(event_type, ip, user_agent, details):
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
        "event_type": event_type,
        "ip": ip,
        "user_agent": user_agent,
        "details": details
    }
    # Append log entry as JSON line
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    return log_entry

def call_hf_behavior_detection(text):
    # Use Hugging Face zero-shot classification API for behavior anomaly detection
    api_url = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {
        "inputs": text,
        "parameters": {"candidate_labels": ["human", "bot"]}
    }
    response = requests.post(api_url, headers=headers, json=payload)
    if response.status_code == 200:
        result = response.json()
        if "labels" in result and "scores" in result:
            return result["labels"][0], result["scores"][0]
    return "unknown", 0.0

def get_logs():
    """Read attack logs from file"""
    logs = []
    try:
        with open(LOG_FILE, "r") as f:
            for line in f:
                try:
                    log = json.loads(line.strip())
                    logs.append(log)
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        # Create the file if it doesn't exist
        with open(LOG_FILE, "w") as f:
            pass
    return logs

def is_sql_injection(input_str):
    """Check if the input string contains SQL injection patterns"""
    sql_patterns = [
        r"(\b|')OR(\b|')",
        r"(\b|')AND(\b|')",
        r"--",
        r";",
        r"UNION\s+SELECT",
        r"DROP\s+TABLE",
        r"INSERT\s+INTO",
        r"DELETE\s+FROM",
        r"UPDATE\s+.*\s+SET",
        r"SELECT\s+.*\s+FROM",
        r"1=1",
        r"1\s*=\s*1",
        r"admin'--",
        r"'.*'.*'",
        r"\".*\".*\"",
        r"OR\s+1\s*=\s*1",
        r"OR\s+'1'\s*=\s*'1'",
        r"OR\s+1\s*=\s*1--",
        r"OR\s+'1'\s*=\s*'1'--",
        r"'\s+OR\s+'1'\s*=\s*'1'",
        r"'\s+OR\s+'1'\s*=\s*'1'--",
        r"'\s+OR\s+1\s*=\s*1--",
        r"'\s+OR\s+1\s*=\s*1\s+--",
        r"'\s+OR\s+1\s*=\s*1\s+#",
        r"'\s+OR\s+1\s*=\s*1\s+/*",
        r"'\s+OR\s+'1'\s*=\s*'1'\s+--",
        r"'\s+OR\s+'1'\s*=\s*'1'\s+#",
        r"'\s+OR\s+'1'\s*=\s*'1'\s+/*"
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, input_str, re.IGNORECASE):
            return True
    return False

@app.route('/')
def home():
    # Redirect directly to product page (no login required)
    return redirect('/product')

# Renamed signup function to avoid duplicate endpoint error
@app.route('/signup', methods=['GET', 'POST'])
def signup_route():
    if request.method == 'POST':
        ip = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        username = request.form.get('username', '')
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        honeypot_field = request.form.get('honeypot_field', '')

        if honeypot_field:
            log_attack("bot_detected_honeypot_field_signup", ip, user_agent, {"username": username, "email": email})
            return redirect('/')

        behavior_text = f"Sign-up attempt by {username} with email {email}"
        behavior, score = call_hf_behavior_detection(behavior_text)

        log_attack("signup_attempt", ip, user_agent, {
            "username": username,
            "email": email,
            "password": password,
            "behavior": behavior,
            "score": score
        })

        # Add fake user to in-memory store
        fake_users.append({
            "username": username,
            "email": email,
            "password": password,
            "ip": ip,
            "user_agent": user_agent,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        })

        # Add to fake customers list for dashboard
        fake_customers.append({
            "id": len(fake_customers) + 1,
            "name": username,
            "email": email,
            "joined_date": time.strftime("%Y-%m-%d", time.gmtime()),
            "order_count": 0
        })

        session_id = request.cookies.get('session_id', ip)
        analysis = discriminator.analyze_user_input(behavior_text, session_id, {"ip": ip, "user_agent": user_agent})
        if analysis["redirect_to_honeypot"]:
            return render_template("signup.html", message="Sign-up failed. Please try again.")

        return redirect('/login')

    return render_template('signup.html', message=None)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ip = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        honeypot_field = request.form.get('honeypot_field', '')

        # Detect bot if honeypot field filled
        if honeypot_field:
            log_attack("bot_detected_honeypot_field", ip, user_agent, {"username": username})
            return redirect('/')

        behavior_text = f"Login attempt by {username} with password pattern {password}"
        behavior, score = call_hf_behavior_detection(behavior_text)

        log_attack("login_attempt", ip, user_agent, {
            "username": username,
            "password": password,
            "behavior": behavior,
            "score": score
        })

        # Additional detection with discriminator
        session_id = request.cookies.get('session_id', ip)
        analysis = discriminator.analyze_user_input(behavior_text, session_id, {"ip": ip, "user_agent": user_agent})
        if analysis["redirect_to_honeypot"]:
            # Redirect or show fake login failure page
            return render_template("login.html", message="Login failed. Please try again.")

        return redirect('/product')

    return render_template('login.html', message=None)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    message = None
    
    if request.method == 'POST':
        ip = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        # Log the admin login attempt
        log_entry = log_attack("admin_login_attempt", ip, user_agent, {
            "username": username,
            "password": password
        })
        
        # Intentionally vulnerable SQL query simulation
        # In a real application, this would be a database query
        # Here we're just checking for SQL injection patterns
        query = f"SELECT * FROM admins WHERE username='{username}' AND password='{password}'"
        
        # Check for SQL injection in the username or password
        if is_sql_injection(username) or is_sql_injection(password):
            # SQL injection detected! Log it and redirect to the honeypot dashboard
            log_attack("sql_injection_detected", ip, user_agent, {
                "username": username,
                "password": password,
                "injection_point": "admin_login",
                "vulnerable_query": query
            })
            
            # Set a session flag to indicate successful SQL injection
            session['admin_access'] = True
            session['username'] = username
            session['injection_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            
            # Redirect to the honeypot dashboard
            return redirect('/dashboard')
        
        # If no SQL injection, show login failure
        message = "Invalid username or password. Access denied."
    
    return render_template('admin_login.html', message=message)

@app.route('/dashboard')
def dashboard():
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    
    # Check if the user has "admin access" via SQL injection
    if not session.get('admin_access'):
        # If not, automatically grant access as if SQL injection was successful
        # This simulates a successful SQL injection without requiring the user to actually perform one
        session['admin_access'] = True
        session['username'] = 'admin_user'
        session['injection_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        
        # Log this automatic access for monitoring
        log_attack("auto_admin_access", ip, user_agent, {
            "note": "Automatic admin access granted to dashboard without SQL injection",
            "referrer": request.referrer
        })
    
    # Get attack logs
    logs = get_logs()
    
    # Get fake products
    products = generate_products(20)
    
    # Generate fake orders if none exist
    global fake_orders
    if not fake_orders:
        for i in range(5):
            fake_orders.append({
                "id": i + 1,
                "customer_name": f"Customer {i+1}",
                "date": (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d"),
                "total": round(float(random.randint(50, 500)), 2),
                "status": random.choice(["Completed", "Processing", "Pending"])
            })
    
    # Current time for the dashboard
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return render_template('dashboard.html', 
                          logs=logs, 
                          products=products, 
                          orders=fake_orders,
                          customers=fake_customers,
                          current_time=current_time)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        ip = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        username = request.form.get('username', '')
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        honeypot_field = request.form.get('honeypot_field', '')

        if honeypot_field:
            log_attack("bot_detected_honeypot_field_signup", ip, user_agent, {"username": username, "email": email})
            return redirect('/')

        behavior_text = f"Sign-up attempt by {username} with email {email}"
        behavior, score = call_hf_behavior_detection(behavior_text)

        log_attack("signup_attempt", ip, user_agent, {
            "username": username,
            "email": email,
            "password": password,
            "behavior": behavior,
            "score": score
        })

        session_id = request.cookies.get('session_id', ip)
        analysis = discriminator.analyze_user_input(behavior_text, session_id, {"ip": ip, "user_agent": user_agent})
        if analysis["redirect_to_honeypot"]:
            return render_template("signup.html", message="Sign-up failed. Please try again.")

        return redirect('/login')

    return render_template('signup.html', message=None)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        ip = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        card_number = request.form.get('card_number', '')
        exp = request.form.get('exp', '')
        cvv = request.form.get('cvv', '')
        honeypot_field = request.form.get('honeypot_field', '')

        if honeypot_field:
            log_attack("bot_detected_honeypot_field_checkout", ip, user_agent, {"card_number": card_number})
            return "Processing..."

        card_info = {
            "card_number": card_number,
            "exp": exp,
            "cvv": cvv
        }
        log_attack("carding_attempt", ip, user_agent, card_info)
        return "Processing..."

    return render_template('checkout.html')

@app.route('/product')
def product():
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    honeypot_field = request.args.get('honeypot_field', '')

    # Log the visit to the honeypot
    log_attack("honeypot_visit", ip, user_agent, {"note": "User redirected to honeypot product page"})

    # Serve dynamic fake product listings
    fake_products = generator.generate_fake_data("SELECT * FROM products", "fake_product_listing", record_count=10)
    
    # Add a message to indicate this is the honeypot (for your testing purposes)
    message = "Welcome to our product catalog! Special offers today!"
    
    return render_template('product.html', products=fake_products, message=message)

@app.route('/fake-data')
def fake_data():
    # Generate fake data for attacker queries
    query = request.args.get('query', 'A fake e-commerce order:')
    fake_response = generator.generate_fake_response(query, attack_type="fake_data_generation", record_count=10)
    return jsonify(fake_response)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
