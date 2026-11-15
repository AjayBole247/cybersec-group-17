# Indian Institute of Information Technology Allahabad
## Department of Information Technology
### Cyber Security (IT-30001) | Autumn Semester 2026
**Assignment:** Web Server Security — Exploitation and Mitigation of Four Vulnerability Categories  
**Course Instructor:** Dr. Soumyadev Maity  
**Submission Deadline:** 15th November 2026 (Sunday), by midnight (23:59)  

---

## 📋 Table 3. Individual Ownership Declaration

| Member Name | Roll Number | Vulnerability Category | Variant Implemented | Module Endpoint |
| :--- | :--- | :--- | :--- | :--- |
| **Ajay Bole** | `IIT2024088` | SQL Injection | **Variant 1: Authentication Bypass** | `/sqli-auth` |
| **Sayan Biswas** | `IIT2024090` | SQL Injection | **Variant 2: UNION-based Data Extraction** | `/sqli-union` |
| **Prince Kumar** | `IIT2024085` | OS Command Injection | **Variant 1: In-Band (Command Output Returned)** | `/cmd-injection` |
| **Chandan Kumar Das** | `IIT2024070` | Cross-Site Scripting (XSS) | **Variant 1: Stored XSS** | `/xss-stored` |
| **Raghvendra** | `IIT2024062` | Cross-Site Request Forgery (CSRF) | **Variant 2: POST-based Forged Action (Auto-Submitting Form)** | `/csrf-post` |

*Bonus Variants Implemented for Reference & Viva Defense:*
- **OS Command Injection (Variant 2):** Blind / Time-based delay (`/cmd-blind`)
- **Cross-Site Scripting (Variant 2):** Reflected XSS (`/xss-reflected`)
- **Cross-Site Request Forgery (Variant 1):** GET-based forged action (`/csrf-get`)
- **Simulated External Malicious Attacker Portal:** (`/attacker-portal`)

---

## 🚀 Quick Start & Installation

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Web browser (Chrome, Firefox, Edge)

### 1. Clone & Setup Workspace
```bash
# Clone the repository
git clone https://github.com/<your-group-repo>/web-server-security-lab.git
cd web-server-security-lab

# Install required dependencies
python -m pip install -r requirements.txt
```

### 2. Initialize the Database
```bash
python database.py
```
This initializes the SQLite database (`vulnerable_lab.db`) with initial seed records across `users`, `products`, `comments`, and `transactions`.

### 3. Run the Automated Verification Suite
```bash
python test_app.py
```
This tests all 5 individual modules in both **Vulnerable** and **Mitigated** states.

### 4. Launch the Web Application
```bash
python app.py
```
Access the application at: **`http://127.0.0.1:5000`**

---

## 🔍 Detailed Variant Documentation (Table 2 Requirements)

Each member's section provides the five required components for the video demonstration and viva examination:
- **(a) Vulnerable Implementation:** Code path and flawed mechanism.
- **(b) Working Exploit:** The exact payload and request tested.
- **(c) Root Cause:** Conceptual explanation of the vulnerability.
- **(d) Mitigation Implemented:** The defensive code fix and blocking proof.
- **(e) Alternative Mitigations (Theory):** Review of lecture slide alternatives.

---

### Member 1: Ajay Bole (`IIT2024088`)
**Category:** SQL Injection  
**Variant:** Variant 1 — Authentication Bypass  
**Route:** `http://127.0.0.1:5000/sqli-auth`

#### (a) Vulnerable Implementation
Located in [`app.py`](file:///e:/5th%20sem/Cyber/project/app.py#L68-L82):
```python
# Flawed concatenation of user input directly into SQL statement
executed_query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
cursor.execute(executed_query)
user = cursor.fetchone()
```

#### (b) Working Exploit
- **Target URL:** `POST /sqli-auth`
- **Payload:**
  - **Username:** `admin' --`
  - **Password:** `anything`
- **Result:** The vulnerable query returns the `admin` record without validating the password. The application then stores the authenticated account ID in a Flask session. Use the **Open Protected Admin Dashboard** link to prove that the server recognizes the login and grants access to `/sqli-auth/dashboard`.

#### (c) Root Cause
User input is concatenated directly into the dynamic SQL query string without sanitization. The single quotation mark (`'`) prematurely closes the data literal, and the SQL comment delimiter (`--`) instruct the SQL engine to discard the password check, causing the query to evaluate:
```sql
SELECT * FROM users WHERE username = 'admin' --' AND password = '...'
```

#### (d) Mitigation Implemented
Parameterized query using prepared statements with placeholder `?`:
```python
executed_query = "SELECT * FROM users WHERE username = ? AND password = ?"
cursor.execute(executed_query, (username, password))
user = cursor.fetchone()
```
**Outcome:** When the payload `admin' --` is entered, SQLite treats the input strictly as a literal username string. No user exists with that literal username, so authentication fails and any previous SQLi-lab session is cleared. The protected dashboard then redirects the visitor back to the login page.
> `[-] Authentication Blocked / Failed: No user matching literal credentials.`

#### Protected-session proof (Ajay's module)
- `GET /sqli-auth/dashboard` redirects users who have not authenticated.
- After a successful vulnerable-mode login, the server stores only the user ID in the Flask session cookie. The dashboard fetches account details server-side and permits access only to the `Administrator` role.
- Every new login attempt clears the previous SQLi-lab login first. Therefore, the same payload in mitigated mode cannot inherit a session created by the vulnerable demonstration.
- `POST /sqli-auth/logout` clears the SQLi-lab authentication session.

#### (e) Alternative Mitigations (Theory)
1. **Parameterized Queries / Prepared Statements:** Compiles the SQL command structure before runtime; parameter values cannot alter query logic.
2. **Allow-List Input Validation:** Enforces strict regex validation (e.g., `^[a-zA-Z0-9_]{3,20}$`) preventing unexpected quotes, semicolons, or dashes.
3. **Least-Privilege Database Accounts:** Restricts the database user permissions strictly to necessary operations, avoiding administrative/DBA roles.
4. **Safe Error Handling:** Replaces database engine stack traces with generic error messages to eliminate reconnaissance opportunities.

---

### Member 2: Sayan Biswas (`IIT2024090`)
**Category:** SQL Injection  
**Variant:** Variant 2 — UNION-based Data Extraction  
**Route:** `http://127.0.0.1:5000/sqli-union`

#### (a) Vulnerable Implementation
Located in [`app.py`](file:///e:/5th%20sem/Cyber/project/app.py#L125-L135):
```python
# Unsanitized input injected into 5-column SELECT statement
executed_query = f"SELECT id, name, category, price, description FROM products WHERE category = '{category}'"
cursor.execute(executed_query)
rows = cursor.fetchall()
```

#### (b) Working Exploit
- **Target URL:** `GET /sqli-union?category=...`
- **Payload:**
  ```sql
  ' UNION SELECT id, username, password, role, secret_flag FROM users --
  ```
- **Result:** Extracts rows from the confidential `users` table including plaintext passwords, roles, and secret flags alongside product catalog data.

#### (c) Root Cause
The product catalog endpoint performs string concatenation into a 5-column query. Because the application reflects all result columns back to the client, appending a `UNION SELECT` statement with the matching number of columns (5) allows the attacker to join and exfiltrate data from arbitrary database tables.

#### (d) Mitigation Implemented
Parameterized query binding:
```python
executed_query = "SELECT id, name, category, price, description FROM products WHERE category = ?"
cursor.execute(executed_query, (category,))
```
**Outcome:** The malicious UNION query is evaluated strictly as an exact category name string, returning zero matching catalog records and blocking exfiltration.

#### (e) Alternative Mitigations (Theory)
1. **Parameterized Queries:** Parameter values are bound separately from query planning, neutralizing UNION joins.
2. **Strict Category Allow-Listing:** Validating the requested category against a server-side array of approved categories (`Hardware`, `Software`, `Books`).
3. **Database Account Partitioning:** Configuring the catalog service account to have read permissions only on `products`, with zero privileges on `users` or `transactions`.
4. **Safe Errors:** Disabling verbose database syntax errors to block column count discovery via `ORDER BY 1, 2, ...` trial-and-error probes.

---

### Member 3: Prince Kumar (`IIT2024085`)
**Category:** OS Command Injection  
**Variant:** Variant 1 — In-Band (Command Output Returned)  
**Route:** `http://127.0.0.1:5000/cmd-injection`

#### (a) Vulnerable Implementation
Located in [`app.py`](file:///e:/5th%20sem/Cyber/project/app.py#L165-L177):
```python
command_executed = f"ping -n 1 {target}"
output = subprocess.check_output(
    command_executed,
    shell=True,          # Invokes system shell (cmd.exe / bash)
    stderr=subprocess.STDOUT,
    text=True
)
```

#### (b) Working Exploit
- **Target URL:** `POST /cmd-injection`
- **Payload:**
  ```text
  127.0.0.1 && whoami
  ```
  *(or `127.0.0.1 & dir` on Windows / `127.0.0.1; id` on Linux)*
- **Result:** Executes both the ping command and the injected system command (`whoami` / `dir`), returning the terminal output in the web response.

#### (c) Root Cause
The application uses `shell=True` to execute a shell command constructed via dynamic string formatting. Shell metacharacters (`&&`, `&`, `|`, `;`) allow chaining secondary operating system commands, which the shell evaluates and executes with the web server process permissions.

#### (d) Mitigation Implemented
1. Strict IP allow-list validation using Python's `ipaddress` module:
```python
try:
    ipaddress.ip_address(target)
except ValueError:
    return "BLOCKED: Input validation failed: Illegal metacharacters detected."
```
2. Parameterized execution with argument vectors (`shell=False`):
```python
subprocess.run(['ping', '-n', '1', target], shell=False, capture_output=True, text=True)
```
**Outcome:** Injected metacharacters (`&& whoami`) immediately fail IP address validation. Even without validation, `shell=False` passes the string as a single hostname literal to `ping`, preventing shell execution.

#### (e) Alternative Mitigations (Theory)
1. **Avoid the Shell:** Utilize programming language native APIs (e.g. Python `socket` module) rather than executing OS shell commands.
2. **Parameterized Execution with Argument Vectors:** Passing arguments as an array of discrete strings with `shell=False` prevents command chaining.
3. **Allow-List Validation:** Enforcing strict character allow-lists (alphanumerics, dots, hyphens only).
4. **Least-Privilege Service Account:** Running the web service under a low-privilege dedicated service account with minimal filesystem and command execution permissions.

---

### Member 4: Chandan Kumar Das (`IIT2024070`)
**Category:** Cross-Site Scripting (XSS)  
**Variant:** Variant 1 — Stored XSS  
**Route:** `http://127.0.0.1:5000/xss-stored`

#### (a) Vulnerable Implementation
Located in [`app.py`](file:///e:/5th%20sem/Cyber/project/app.py#L225-L235) and [`xss_stored.html`](file:///e:/5th%20sem/Cyber/project/templates/xss_stored.html#L90-L95):
```html
<!-- Flawed: Unescaped rendering using Jinja2 safe filter -->
<div class="comment-body">
    {{ comment.message | safe }}
</div>
```

#### (b) Working Exploit
- **Target URL:** `POST /xss-stored`
- **Payload:**
  ```html
  <script>alert('Stored XSS Triggered! Session Cookie: ' + document.cookie);</script>
  ```
  *(or `<img src=x onerror="alert('Stored XSS Executed!')">`)*
- **Result:** The malicious script is permanently stored in the database. When any visitor loads the page, the JavaScript runs in their browser context, allowing session cookie access or DOM manipulation.

#### (c) Root Cause
Untrusted user input is persisted in the database and rendered in the HTML document without contextual encoding. The browser parses the injected `<script>` or event handlers as genuine executable code.

#### (d) Mitigation Implemented
Server-side HTML entity escaping (`html.escape()`) combined with default framework auto-escaping (removing `| safe`):
```python
sanitized_message = html.escape(message)
sanitized_author = html.escape(author)
```
```html
<div class="comment-body">
    {{ comment.message }}
</div>
```
**Outcome:** Characters like `<` and `>` are encoded as `&lt;` and `&gt;`. The browser renders the payload harmlessly as plain text without executing the script.

#### (e) Alternative Mitigations (Theory)
1. **Context-Aware Output Encoding:** Encoding dynamic data based on output context (HTML body, attributes, JavaScript, CSS).
2. **Framework Auto-Escaping:** Using template engines with automatic contextual escaping enabled.
3. **Content Security Policy (CSP):** Setting headers like `Content-Security-Policy: default-src 'self'` to block inline scripts and restrict script origins.
4. **HttpOnly Cookie Flag:** Marking session cookies `HttpOnly` so JavaScript cannot access `document.cookie`.
5. **Safe DOM Sinks & Sanitizers:** Using sanitization libraries (e.g. DOMPurify) for rich HTML and avoiding sinks like `innerHTML` or `document.write`.

---

### Member 5: Raghvendra (`IIT2024062`)
**Category:** Cross-Site Request Forgery (CSRF)  
**Variant:** Variant 2 — POST-based Forged Action (Auto-Submitting Form)  
**Routes:**
- Banking Portal: `http://127.0.0.1:5000/csrf-post`
- Attacker PoC Page: `http://127.0.0.1:5000/attacker-portal`

#### (a) Vulnerable Implementation
Located in [`app.py`](file:///e:/5th%20sem/Cyber/project/app.py#L320-L345):
```python
# Flawed: Processes fund transfer relying solely on ambient session cookie
current_user = session.get('user')
amount = float(request.form.get('amount'))
recipient = request.form.get('recipient')
execute_transfer(current_user, recipient, amount)
```

#### (b) Working Exploit
- **Attacker Page:** `http://127.0.0.1:5000/attacker-portal`
- **Payload:** An auto-submitting hidden HTML form:
  ```html
  <form id="csrfForm" action="http://127.0.0.1:5000/csrf-post/transfer" method="POST">
      <input type="hidden" name="mode" value="vulnerable">
      <input type="hidden" name="recipient" value="attacker_account">
      <input type="hidden" name="amount" value="5000.00">
  </form>
  <script>
      document.getElementById('csrfForm').submit();
  </script>
  ```
- **Result:** When the authenticated victim visits the attacker page, the browser automatically submits the form along with session cookies, transferring $5,000 to the attacker without user consent.

#### (c) Root Cause
The browser automatically attaches session cookies to cross-site requests. Because the server does not verify user intent or check an unpredictable secret token, it cannot distinguish a legitimate user submission from a cross-site forged request.

#### (d) Mitigation Implemented
The Synchronizer Token Pattern (Anti-CSRF Token):
```python
expected_token = session.get('csrf_token')
submitted_token = request.form.get('csrf_token')

if not submitted_token or submitted_token != expected_token:
    return "403 FORBIDDEN: CSRF Protection Triggered! Invalid Token.", 403
```
**Outcome:** When the attacker's page attempts to submit the form, it cannot access the victim's session token (due to Same-Origin Policy). The server rejects the request with HTTP 403 Forbidden.

#### (e) Alternative Mitigations (Theory)
1. **Anti-CSRF (Synchronizer) Tokens:** Cryptographically random, unguessable tokens associated with the session and validated on state-changing requests.
2. **SameSite Cookie Attribute:** Setting `SameSite=Lax` or `SameSite=Strict` prevents browsers from attaching session cookies to cross-site requests.
3. **Re-Authentication:** Prompting for password re-entry or MFA/OTP for sensitive actions like wire transfers.
4. **Avoiding State-Changing GET Requests:** Ensuring GET requests remain safe and idempotent per RFC standards.

---

## 📁 Repository Directory Structure

```text
web-server-security-lab/
├── app.py                      # Core Flask application with dual vulnerable/mitigated engines
├── database.py                 # SQLite database schema, seeding, and helper utilities
├── test_app.py                 # Automated test suite verifying all 5 member vulnerabilities
├── requirements.txt            # Python dependencies
├── README.md                   # Complete assignment report and documentation
├── VIDEO_DEMO_SCRIPT.md        # Screen-recording narration script (2-3 mins per member)
├── VIVA_PREPARATION_GUIDE.md   # Individual viva question bank and answers
├── vulnerable_lab.db           # SQLite database file (created upon initialization)
├── static/
│   ├── css/
│   │   └── style.css           # Custom dark cyber-security theme stylesheet
│   └── js/
│       └── app.js              # Interactive payload quick-fill and UI helpers
└── templates/
    ├── base.html               # Base navigation and footer layout
    ├── index.html              # Main dashboard with Table 3 ownership table
    ├── sqli_auth_bypass.html   # Ajay Bole (SQLi Variant 1 login)
    ├── sqli_auth_dashboard.html # Ajay Bole (protected admin dashboard)
    ├── sqli_union.html         # Sayan Biswas (SQLi Variant 2)
    ├── cmd_injection.html      # Prince Kumar (OS Command Injection Variant 1)
    ├── xss_stored.html         # Chandan Kumar Das (XSS Variant 1)
    ├── csrf_post.html          # Raghvendra (CSRF Variant 2)
    ├── attacker_portal.html    # External malicious website simulating auto-submitting CSRF
    ├── cmd_blind.html          # Bonus Variant (OS Command Injection Variant 2 - Blind)
    ├── xss_reflected.html      # Bonus Variant (XSS Variant 2 - Reflected)
    └── csrf_get.html           # Bonus Variant (CSRF Variant 1 - GET)
```

---

## 🏆 Viva Verification Checklist

Before attending the individual viva examination:
1. Ensure the web application runs locally (`python app.py`).
2. Verify you can explain your assigned variant's:
   - Flawed code path and line numbers
   - Exploit payload and metacharacter roles
   - Root cause in 1-2 concise sentences
   - Implemented mitigation code and why the exploit fails
   - Theoretical explanations of the alternative mitigations from lecture slides
3. Reference [`VIVA_PREPARATION_GUIDE.md`](file:///e:/5th%20sem/Cyber/project/VIVA_PREPARATION_GUIDE.md) for sample questions and answers.
