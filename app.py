"""
IIIT Allahabad | Department of Information Technology
Cyber Security (IT-30001) | Autumn Semester 2026
Assignment: Web Server Security - Exploitation and Mitigation
Instructor: Dr. Soumyadev Maity

Team Members:
1. Ajay Bole         (IIT2024088) - SQL Injection: Variant 1 (Authentication Bypass)
2. Sayan Biswas      (IIT2024090) - SQL Injection: Variant 2 (UNION-based Data Extraction)
3. Prince Kumar      (IIT2024085) - OS Command Injection: Variant 1 (In-Band Output Returned)
4. Chandan Kumar Das (IIT2024070) - Cross-Site Scripting (XSS): Variant 1 (Stored XSS)
5. Raghvendra        (IIT2024062) - Cross-Site Request Forgery (CSRF): Variant 2 (POST-based Forged Action)
"""

import os
import re
import html
import time
import secrets
import sqlite3
import subprocess
import ipaddress
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify, make_response
)
import database

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Ensure cookie settings allow educational demonstration across local origins
app.config['SESSION_COOKIE_HTTPONLY'] = False  # Allows demonstration of cookie theft in XSS
app.config['SESSION_COOKIE_SAMESITE'] = 'None' # Allows cross-site requests for CSRF demonstration
app.config['SESSION_COOKIE_SECURE'] = False

@app.before_request
def ensure_session_defaults():
    """Ensure standard session state for CSRF and login testing."""
    if 'user' not in session:
        session['user'] = 'victim_user'
        session['user_role'] = 'Customer'
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(16)

# -------------------------------------------------------------
# ROOT / DASHBOARD ROUTE
# -------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reset-db', methods=['POST'])
def reset_db_route():
    database.init_db(reset=True)
    flash("Database has been reset to its fresh seed state successfully!", "success")
    return redirect(request.referrer or url_for('index'))

# -------------------------------------------------------------
# 1. AJAY BOLE (IIT2024088) - SQL INJECTION: VARIANT 1 (AUTH BYPASS)
# -------------------------------------------------------------
@app.route('/sqli-auth', methods=['GET', 'POST'])
def sqli_auth():
    mode = request.args.get('mode', 'vulnerable')
    login_result = None
    executed_query = None
    raw_error = None

    if request.method == 'POST':
        mode = request.form.get('mode', 'vulnerable')
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        # Every new login attempt starts unauthenticated; only a successful query sets this.
        session.pop('sqli_auth_user_id', None)

        conn = database.get_db_connection()
        cursor = conn.cursor()

        if mode == 'vulnerable':
            # VULNERABLE CODE PATH:
            # String concatenation directly incorporating user input without sanitization or parameterization
            executed_query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
            try:
                # Using cursor.execute directly on interpolated string
                cursor.execute(executed_query)
                user = cursor.fetchone()
                if user:
                    # Establish a real Flask session after the vulnerable query returns a user.
                    # This is intentionally vulnerable only in this isolated academic lab.
                    # Store only the account ID in Flask's signed session cookie.
                    # Account details are fetched server-side on the protected dashboard.
                    session['sqli_auth_user_id'] = user['id']
                    login_result = {
                        'success': True,
                        'message': f"Authentication Successful! Logged in as: {user['username']}",
                        'user': {
                            'id': user['id'], 'username': user['username'],
                            'role': user['role'], 'email': user['email'],
                            'secret_flag': user['secret_flag'], 'balance': user['balance']
                        }
                    }
                else:
                    session.pop('sqli_auth_user_id', None)
                    login_result = {
                        'success': False,
                        'message': "Authentication Failed: Invalid username or password."
                    }
            except sqlite3.OperationalError as e:
                raw_error = str(e)
                login_result = {
                    'success': False,
                    'message': f"SQL Syntax Error: {str(e)}"
                }
        else:
            # MITIGATED CODE PATH:
            # Secure parameterized query using prepared statement place-holders (?)
            executed_query = "SELECT * FROM users WHERE username = ? AND password = ?"
            cursor.execute(executed_query, (username, password))
            user = cursor.fetchone()
            if user:
                session['sqli_auth_user_id'] = user['id']
                login_result = {
                    'success': True,
                    'message': f"Authentication Successful! Logged in as: {user['username']}",
                    'user': {
                        'id': user['id'], 'username': user['username'],
                        'role': user['role'], 'email': user['email'],
                        'secret_flag': user['secret_flag'], 'balance': user['balance']
                    }
                }
            else:
                # Clear any previous lab login so a failed mitigated attempt cannot
                # reuse an earlier vulnerable-mode session.
                session.pop('sqli_auth_user_id', None)
                login_result = {
                    'success': False,
                    'message': "Authentication Blocked / Failed: No user matching literal credentials."
                }

        conn.close()

    return render_template(
        'sqli_auth_bypass.html',
        mode=mode,
        login_result=login_result,
        executed_query=executed_query,
        raw_error=raw_error
    )


@app.route('/sqli-auth/dashboard', methods=['GET'])
def sqli_auth_dashboard():
    """Protected admin area for demonstrating a real authenticated session."""
    user_id = session.get('sqli_auth_user_id')
    if not user_id:
        flash('Please log in before accessing the admin dashboard.', 'error')
        return redirect(url_for('sqli_auth', mode='vulnerable'))

    conn = database.get_db_connection()
    user = conn.execute(
        'SELECT id, username, role, email, secret_flag, balance FROM users WHERE id = ?',
        (user_id,)
    ).fetchone()
    conn.close()

    if not user or user['role'] != 'Administrator':
        session.pop('sqli_auth_user_id', None)
        return 'Forbidden: Administrator access required.', 403

    return render_template('sqli_auth_dashboard.html', user=dict(user))


@app.route('/sqli-auth/logout', methods=['POST'])
def sqli_auth_logout():
    """Log out only from Ajay's SQL injection demonstration module."""
    session.pop('sqli_auth_user_id', None)
    flash('SQL injection lab session logged out.', 'success')
    return redirect(url_for('sqli_auth', mode='vulnerable'))

# -------------------------------------------------------------
# 2. SAYAN BISWAS (IIT2024090) - SQL INJECTION: VARIANT 2 (UNION DATA EXTRACTION)
# -------------------------------------------------------------
@app.route('/sqli-union', methods=['GET'])
def sqli_union():
    mode = request.args.get('mode', 'vulnerable')
    category = request.args.get('category', 'Hardware')
    products = []
    executed_query = None
    raw_error = None

    conn = database.get_db_connection()
    cursor = conn.cursor()

    if mode == 'vulnerable':
        # VULNERABLE CODE PATH:
        # String concatenation allows injecting ' UNION SELECT ...' matching column count (5 columns)
        executed_query = f"SELECT id, name, category, price, description FROM products WHERE category = '{category}'"
        try:
            cursor.execute(executed_query)
            rows = cursor.fetchall()
            products = [dict(row) for row in rows]
        except sqlite3.OperationalError as e:
            raw_error = str(e)
    else:
        # MITIGATED CODE PATH:
        # Parameterized query binds input as literal data string, neutralizing UNION statement injection
        executed_query = "SELECT id, name, category, price, description FROM products WHERE category = ?"
        cursor.execute(executed_query, (category,))
        rows = cursor.fetchall()
        products = [dict(row) for row in rows]

    conn.close()

    return render_template(
        'sqli_union.html',
        mode=mode,
        category=category,
        products=products,
        executed_query=executed_query,
        raw_error=raw_error
    )

# -------------------------------------------------------------
# 3. PRINCE KUMAR (IIT2024085) - OS COMMAND INJECTION: VARIANT 1 (IN-BAND)
# -------------------------------------------------------------
@app.route('/cmd-injection', methods=['GET', 'POST'])
def cmd_injection():
    mode = request.args.get('mode', 'vulnerable')
    output = None
    command_executed = None
    status = None

    if request.method == 'POST':
        mode = request.form.get('mode', 'vulnerable')
        target = request.form.get('target', '127.0.0.1').strip()

        if mode == 'vulnerable':
            # VULNERABLE CODE PATH:
            # String formatting with shell=True permits command chaining operators (&, &&, |, ;)
            command_executed = f"ping -n 1 {target}"
            try:
                output = subprocess.check_output(
                    command_executed,
                    shell=True,
                    stderr=subprocess.STDOUT,
                    text=True,
                    timeout=5
                )
                status = "SUCCESS"
            except subprocess.CalledProcessError as e:
                output = e.output
                status = "RETURNED_ERROR"
            except Exception as e:
                output = f"Execution Exception: {str(e)}"
                status = "EXCEPTION"
        else:
            # MITIGATED CODE PATH:
            # 1. Strict Allow-list Input Validation: checks if input is a valid IPv4/IPv6 address or alphanumeric domain
            # 2. Parameterized Execution: shell=False with argument vector prevents shell parsing
            command_executed = f"['ping', '-n', '1', '{target}'] (shell=False with allow-list check)"
            
            is_valid_ip = False
            try:
                ipaddress.ip_address(target)
                is_valid_ip = True
            except ValueError:
                # Allow strictly clean hostnames without metacharacters
                if re.match(r'^[a-zA-Z0-9\.\-]+$', target) and not any(c in target for c in '&|;><$`"\'\\'):
                    is_valid_ip = True

            if not is_valid_ip:
                output = (
                    "SECURITY DEFENSE TRIGGERED [BLOCKED]:\n"
                    "Input validation failed: Malicious metacharacters or illegal IP format detected.\n"
                    "Allow-list enforcement strictly permitted only valid IPv4/IPv6 or alphanumeric hostnames."
                )
                status = "BLOCKED"
            else:
                try:
                    result = subprocess.run(
                        ['ping', '-n', '1', target],
                        shell=False,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    output = result.stdout or result.stderr
                    status = "SUCCESS"
                except Exception as e:
                    output = f"Execution Exception: {str(e)}"
                    status = "EXCEPTION"

    return render_template(
        'cmd_injection.html',
        mode=mode,
        output=output,
        command_executed=command_executed,
        status=status
    )

# -------------------------------------------------------------
# 4. CHANDAN KUMAR DAS (IIT2024070) - CROSS-SITE SCRIPTING (XSS): VARIANT 1 (STORED)
# -------------------------------------------------------------
@app.route('/xss-stored', methods=['GET', 'POST'])
def xss_stored():
    mode = request.args.get('mode', 'vulnerable')

    if request.method == 'POST':
        mode = request.form.get('mode', 'vulnerable')
        author = request.form.get('author', 'Anonymous')
        message = request.form.get('message', '')

        if message.strip():
            conn = database.get_db_connection()
            cursor = conn.cursor()
            
            if mode == 'vulnerable':
                # VULNERABLE CODE PATH:
                # User payload is stored raw and rendered in HTML using '| safe' unescaped filter
                cursor.execute(
                    "INSERT INTO comments (author, message, created_at) VALUES (?, ?, ?)",
                    (author, message, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                )
            else:
                # MITIGATED CODE PATH:
                # Context-aware server-side sanitization / HTML entity encoding before storage + Jinja autoescaping
                sanitized_message = html.escape(message)
                sanitized_author = html.escape(author)
                cursor.execute(
                    "INSERT INTO comments (author, message, created_at) VALUES (?, ?, ?)",
                    (sanitized_author, sanitized_message, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                )
            
            conn.commit()
            conn.close()
            flash("Comment posted successfully!", "info")
            return redirect(url_for('xss_stored', mode=mode))

    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM comments ORDER BY id DESC")
    comments = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return render_template(
        'xss_stored.html',
        mode=mode,
        comments=comments
    )

@app.route('/xss-stored/clear', methods=['POST'])
def clear_comments():
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM comments WHERE id > 3")  # keep 3 initial seed comments
    conn.commit()
    conn.close()
    flash("Custom comments cleared. Reset to default.", "info")
    return redirect(url_for('xss_stored'))

# -------------------------------------------------------------
# 5. RAGHVENDRA (IIT2024062) - CSRF: VARIANT 2 (POST-BASED FORGED ACTION)
# -------------------------------------------------------------
@app.route('/csrf-post', methods=['GET'])
def csrf_post():
    mode = request.args.get('mode', 'vulnerable')
    conn = database.get_db_connection()
    cursor = conn.cursor()

    current_user = session.get('user', 'victim_user')
    cursor.execute("SELECT * FROM users WHERE username = ?", (current_user,))
    user_data = cursor.fetchone()

    cursor.execute("SELECT * FROM transactions WHERE sender = ? OR recipient = ? ORDER BY id DESC LIMIT 10", (current_user, current_user))
    tx_rows = cursor.fetchall()
    conn.close()

    return render_template(
        'csrf_post.html',
        mode=mode,
        user=dict(user_data) if user_data else None,
        transactions=[dict(r) for r in tx_rows],
        csrf_token=session.get('csrf_token')
    )

@app.route('/csrf-post/transfer', methods=['POST'])
def csrf_post_transfer():
    mode = request.form.get('mode', 'vulnerable')
    recipient = request.form.get('recipient')
    amount_str = request.form.get('amount')
    submitted_token = request.form.get('csrf_token')

    try:
        amount = float(amount_str)
    except (TypeError, ValueError):
        flash("Invalid transfer amount.", "danger")
        return redirect(url_for('csrf_post', mode=mode))

    current_user = session.get('user', 'victim_user')

    if mode == 'vulnerable':
        # VULNERABLE CODE PATH:
        # Accepts POST request state changes relying purely on session cookie.
        # No Synchronizer Token is checked. External sites can submit forms on behalf of the user.
        conn = database.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT balance FROM users WHERE username = ?", (current_user,))
        row = cursor.fetchone()
        if not row or row['balance'] < amount:
            conn.close()
            flash("Transfer Failed: Insufficient balance.", "warning")
            return redirect(url_for('csrf_post', mode=mode))

        # Perform balance transfer
        cursor.execute("UPDATE users SET balance = balance - ? WHERE username = ?", (amount, current_user))
        cursor.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (amount, recipient))
        cursor.execute(
            "INSERT INTO transactions (sender, recipient, amount, status, timestamp) VALUES (?, ?, ?, ?, ?)",
            (current_user, recipient, amount, 'Completed [FORGED/VULNERABLE]', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        )
        conn.commit()
        conn.close()

        flash(f"VULNERABLE ACTION EXECUTED: Successfully transferred ${amount:.2f} to {recipient}!", "danger")
        return redirect(url_for('csrf_post', mode=mode))

    else:
        # MITIGATED CODE PATH:
        # Anti-CSRF Synchronizer Token Pattern validation
        expected_token = session.get('csrf_token')
        if not submitted_token or submitted_token != expected_token:
            response_msg = (
                "403 FORBIDDEN: CSRF Protection Triggered!\n"
                "Missing or invalid Anti-CSRF Synchronizer Token.\n"
                "Cross-Site Request Blocked by Server Defense."
            )
            flash(response_msg, "success")
            conn = database.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (current_user,))
            user_data = cursor.fetchone()
            cursor.execute("SELECT * FROM transactions WHERE sender = ? OR recipient = ? ORDER BY id DESC LIMIT 10", (current_user, current_user))
            tx_rows = cursor.fetchall()
            conn.close()

            return render_template(
                'csrf_post.html',
                mode=mode,
                blocked_error=response_msg,
                csrf_token=expected_token,
                user=dict(user_data) if user_data else {'username': current_user, 'balance': 0.0},
                transactions=[dict(r) for r in tx_rows]
            ), 403

        # Token is valid, proceed with verified transfer
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE username = ?", (current_user,))
        row = cursor.fetchone()
        if not row or row['balance'] < amount:
            conn.close()
            flash("Transfer Failed: Insufficient balance.", "warning")
            return redirect(url_for('csrf_post', mode=mode))

        cursor.execute("UPDATE users SET balance = balance - ? WHERE username = ?", (amount, current_user))
        cursor.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (amount, recipient))
        cursor.execute(
            "INSERT INTO transactions (sender, recipient, amount, status, timestamp) VALUES (?, ?, ?, ?, ?)",
            (current_user, recipient, amount, 'Completed [LEGITIMATE/VALIDATED]', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        )
        conn.commit()
        conn.close()

        flash(f"LEGITIMATE TRANSFER VERIFIED: Transferred ${amount:.2f} to {recipient} with valid CSRF token.", "success")
        return redirect(url_for('csrf_post', mode=mode))

@app.route('/switch-user/<username>')
def switch_user(username):
    session['user'] = username
    flash(f"Switched active session user to: {username}", "info")
    return redirect(request.referrer or url_for('index'))

# -------------------------------------------------------------
# ATTACKER SERVER SIMULATION (For CSRF Demonstration)
# -------------------------------------------------------------
@app.route('/attacker-portal')
def attacker_portal():
    """Simulates an external malicious website (e.g., evil-hacker.com)"""
    return render_template('attacker_portal.html')

# -------------------------------------------------------------
# BONUS VARIANTS (For maximum viva coverage)
# -------------------------------------------------------------
@app.route('/cmd-blind', methods=['GET', 'POST'])
def cmd_blind():
    """Bonus: OS Command Injection Variant 2 (Blind / Time-based)"""
    mode = request.args.get('mode', 'vulnerable')
    execution_time = None
    status = None

    if request.method == 'POST':
        mode = request.form.get('mode', 'vulnerable')
        domain = request.form.get('domain', 'google.com').strip()

        start_t = time.time()
        if mode == 'vulnerable':
            # Vulnerable to injected delays, e.g. 127.0.0.1 && ping -n 5 127.0.0.1
            cmd = f"nslookup {domain}"
            try:
                subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=12)
                status = "Executed (No stdout returned - Blind)"
            except subprocess.TimeoutExpired:
                status = "Timeout expired (Payload induced significant delay)"
        else:
            # Mitigated with domain regex allow-list
            if not re.match(r'^[a-zA-Z0-9\.\-]+$', domain):
                status = "BLOCKED: Metacharacters detected."
            else:
                subprocess.run(['nslookup', domain], shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                status = "Executed securely."
        execution_time = round(time.time() - start_t, 3)

    return render_template('cmd_blind.html', mode=mode, execution_time=execution_time, status=status)

@app.route('/xss-reflected')
def xss_reflected():
    """Bonus: Cross-Site Scripting Variant 2 (Reflected XSS)"""
    mode = request.args.get('mode', 'vulnerable')
    query = request.args.get('q', '')
    return render_template('xss_reflected.html', mode=mode, query=query)

@app.route('/csrf-get', methods=['GET'])
def csrf_get():
    """Bonus: Cross-Site Request Forgery Variant 1 (GET-based forged action)"""
    mode = request.args.get('mode', 'vulnerable')
    action = request.args.get('action')
    recipient = request.args.get('recipient')
    amount = request.args.get('amount')
    result = None

    if action == 'transfer' and recipient and amount:
        current_user = session.get('user', 'victim_user')
        if mode == 'vulnerable':
            result = f"GET-based transfer of ${amount} to {recipient} completed without user confirmation!"
        else:
            result = "BLOCKED: Sensitive state-changing actions are strictly forbidden via HTTP GET. Please use POST with CSRF tokens."

    return render_template('csrf_get.html', mode=mode, result=result)

# -------------------------------------------------------------
# APPLICATION ENTRYPOINT
# -------------------------------------------------------------
if __name__ == '__main__':
    database.init_db(reset=False)
    print("=" * 70)
    print(" IIIT Allahabad - Cyber Security (IT-30001)")
    print(" Web Server Security: Exploitation & Mitigation Platform")
    print(" Server running on http://127.0.0.1:5000")
    print("=" * 70)
    app.run(host='127.0.0.1', port=5000, debug=True)
