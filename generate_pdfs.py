"""
PDF Generator script for:
1. VIDEO_DEMO_SCRIPT.pdf
2. VIVA_PREPARATION_GUIDE.pdf

IIIT Allahabad | Department of Information Technology
Cyber Security (IT-30001) | Dr. Soumyadev Maity
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class NumberedCanvas(canvas.Canvas):
    """Adds page numbers and header/footer to each page."""
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        # Top Header line
        self.drawString(54, 755, "IIIT Allahabad | IT-30001 Cyber Security | Web Server Security Project")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 748, 558, 748)

        # Bottom Footer line
        self.line(54, 45, 558, 45)
        self.drawString(54, 32, "Instructor: Dr. Soumyadev Maity | Autumn 2026")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 32, page_str)
        self.restoreState()


def get_custom_styles():
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#0284c7"),
        spaceAfter=14
    )

    h1_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=12,
        spaceAfter=6
    )

    h2_style = ParagraphStyle(
        'SubSectionHeading',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#0369a1"),
        spaceBefore=8,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6
    )

    speech_style = ParagraphStyle(
        'SpeakerText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=6
    )

    code_style = ParagraphStyle(
        'CodeSnippet',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#0f172a")
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e293b")
    )

    return {
        'title': title_style,
        'subtitle': subtitle_style,
        'h1': h1_style,
        'h2': h2_style,
        'body': body_style,
        'speech': speech_style,
        'code': code_style,
        'callout': callout_style
    }


def create_callout_box(title, text, bg_color="#f1f5f9", border_color="#cbd5e1"):
    styles = get_custom_styles()
    content = [
        Paragraph(f"<b>{title}</b>", styles['h2']),
        Paragraph(text, styles['callout'])
    ]
    t = Table([[content]], colWidths=[504])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(bg_color)),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor(border_color)),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    return t


def build_video_script_pdf():
    pdf_filename = os.path.join(BASE_DIR, 'VIDEO_DEMO_SCRIPT.pdf')
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = get_custom_styles()
    story = []

    # Title & Header
    story.append(Paragraph("🎬 Group Video Demonstration Script", styles['title']))
    story.append(Paragraph("Indian Institute of Information Technology Allahabad | Cyber Security (IT-30001)<br/>Course Instructor: Dr. Soumyadev Maity | Target Length: 12-15 Minutes", styles['subtitle']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0"), spaceAfter=10))

    # Ownership Table
    story.append(Paragraph("📋 Table 3. Group Ownership & Video Timeline", styles['h1']))
    table_data = [
        [
            Paragraph("<b>Timestamp</b>", styles['body']),
            Paragraph("<b>Speaker</b>", styles['body']),
            Paragraph("<b>Roll No</b>", styles['body']),
            Paragraph("<b>Assigned Category & Variant</b>", styles['body'])
        ],
        [
            Paragraph("00:00 - 00:45", styles['body']),
            Paragraph("Ajay Bole", styles['body']),
            Paragraph("IIT2024088", styles['body']),
            Paragraph("Group Intro & System Architecture Overview", styles['body'])
        ],
        [
            Paragraph("00:45 - 03:15", styles['body']),
            Paragraph("Ajay Bole", styles['body']),
            Paragraph("IIT2024088", styles['body']),
            Paragraph("SQLi: Variant 1 (Authentication Bypass)", styles['body'])
        ],
        [
            Paragraph("03:15 - 05:45", styles['body']),
            Paragraph("Sayan Biswas", styles['body']),
            Paragraph("IIT2024090", styles['body']),
            Paragraph("SQLi: Variant 2 (UNION-based Data Extraction)", styles['body'])
        ],
        [
            Paragraph("05:45 - 08:15", styles['body']),
            Paragraph("Prince Kumar", styles['body']),
            Paragraph("IIT2024085", styles['body']),
            Paragraph("OS Cmd Inj: Variant 1 (In-Band Output)", styles['body'])
        ],
        [
            Paragraph("08:15 - 10:45", styles['body']),
            Paragraph("Chandan K. Das", styles['body']),
            Paragraph("IIT2024070", styles['body']),
            Paragraph("XSS: Variant 1 (Stored XSS)", styles['body'])
        ],
        [
            Paragraph("10:45 - 13:15", styles['body']),
            Paragraph("Raghvendra", styles['body']),
            Paragraph("IIT2024062", styles['body']),
            Paragraph("CSRF: Variant 2 (POST Auto-Submit)", styles['body'])
        ],
        [
            Paragraph("13:15 - 14:00", styles['body']),
            Paragraph("All Members", styles['body']),
            Paragraph("Group 4", styles['body']),
            Paragraph("Conclusion & Submission Summary", styles['body'])
        ]
    ]
    t = Table(table_data, colWidths=[80, 95, 75, 254])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

    # Segment 0: Intro
    story.append(Paragraph("Segment 0: Group Introduction (00:00 - 00:45)", styles['h1']))
    story.append(Paragraph("<b>Screen View:</b> Open web browser at <code>http://127.0.0.1:5000/</code> showing the Main Dashboard and Table 3 Ownership table.", styles['body']))
    intro_speech = (
        '"Hello everyone and respected instructor Dr. Soumyadev Maity sir. We are Group 4 presenting our Web Server '
        'Security assignment for IT-30001. Our group has five members: myself Ajay Bole, Sayan Biswas, Prince Kumar, '
        'Chandan Kumar Das, and Raghvendra. Today we demonstrate live exploitation and implemented defenses across SQL Injection, '
        'OS Command Injection, Stored XSS, and CSRF. Each member personally implemented, exploited, and mitigated their assigned variant."'
    )
    story.append(create_callout_box("🎙️ Ajay Speaks (Intro)", intro_speech, "#eff6ff", "#93c5fd"))
    story.append(Spacer(1, 10))

    # Segment 1: Ajay Bole
    story.append(Paragraph("Segment 1: Ajay Bole (IIT2024088) — SQLi Auth Bypass (00:45 - 03:15)", styles['h1']))
    story.append(Paragraph("<b>Target Route:</b> <code>/sqli-auth</code> | <b>Mode:</b> Vulnerable &rarr; Mitigated", styles['body']))
    ajay_speech = (
        '<b>1. Vulnerable Code (a):</b> "In app.py, the login query is formed by directly interpolating user input: '
        '<code>SELECT * FROM users WHERE username = \'{username}\' AND password = \'{password}\'</code>.<br/>'
        '<b>2. Working Exploit (b):</b> In the username field, I enter <code>admin\' --</code> and arbitrary password \'x\'. '
        'Clicking login immediately grants Administrator access, extracting the admin flag <code>FLAG{iiita_sql1_auth_byp4ss_m4st3r}</code>!<br/>'
        '<b>3. Root Cause (c):</b> Unsanitized concatenation allows the single quote to break out of the string literal, and <code>--</code> comments '
        'out password verification, creating an authentication bypass.<br/>'
        '<b>4. Implemented Mitigation (d):</b> Parameterized queries with prepared statement <code>cursor.execute(\'SELECT ... WHERE username = ? AND password = ?\', (username, password))</code>. '
        'Switching to Mitigated Mode and re-submitting <code>admin\' --</code> returns Access Denied / Blocked because the input is treated as literal text.<br/>'
        '<b>5. Other Mitigations (e):</b> Allow-list input validation, least-privilege DB roles, and safe generic error messages."'
    )
    story.append(create_callout_box("🎙️ Ajay's Narration Script", ajay_speech, "#f8fafc", "#cbd5e1"))
    story.append(Spacer(1, 12))

    story.append(PageBreak())

    # Segment 2: Sayan Biswas
    story.append(Paragraph("Segment 2: Sayan Biswas (IIT2024090) — SQLi UNION Extraction (03:15 - 05:45)", styles['h1']))
    story.append(Paragraph("<b>Target Route:</b> <code>/sqli-union</code> | <b>Mode:</b> Vulnerable &rarr; Mitigated", styles['body']))
    sayan_speech = (
        '<b>1. Vulnerable Code (a):</b> "This product catalog endpoint directly concatenates the category query parameter: '
        '<code>SELECT id, name, category, price, description FROM products WHERE category = \'{category}\'</code>.<br/>'
        '<b>2. Working Exploit (b):</b> Since the query selects 5 columns, I inject: <code>\' UNION SELECT id, username, password, role, secret_flag FROM users --</code>. '
        'Submitting this exfiltrates the entire users table—displaying admin credentials and flags alongside products!<br/>'
        '<b>3. Root Cause (c):</b> Dynamic query construction with matching column count allows an attacker to inject UNION operators and join records from unrelated tables.<br/>'
        '<b>4. Implemented Mitigation (d):</b> Prepared statements with parameter binding: <code>cursor.execute(\'SELECT ... WHERE category = ?\', (category,))</code>. '
        'In Mitigated Mode, the UNION payload is treated as an exact category string, returning 0 rows and blocking data extraction.<br/>'
        '<b>5. Other Mitigations (e):</b> Server-side allow-list category verification, least-privilege DB user partitioning, and suppressing database syntax errors."'
    )
    story.append(create_callout_box("🎙️ Sayan's Narration Script", sayan_speech, "#f8fafc", "#cbd5e1"))
    story.append(Spacer(1, 12))

    # Segment 3: Prince Kumar
    story.append(Paragraph("Segment 3: Prince Kumar (IIT2024085) — OS Command Injection (05:45 - 08:15)", styles['h1']))
    story.append(Paragraph("<b>Target Route:</b> <code>/cmd-injection</code> | <b>Mode:</b> Vulnerable &rarr; Mitigated", styles['body']))
    prince_speech = (
        '<b>1. Vulnerable Code (a):</b> "In app.py, the network diagnostic tool executes: '
        '<code>subprocess.check_output(f\'ping -n 1 {target}\', shell=True, text=True)</code>.<br/>'
        '<b>2. Working Exploit (b):</b> I enter <code>127.0.0.1 && whoami</code>. The console outputs both the ping reply and executes whoami, returning the system user!<br/>'
        '<b>3. Root Cause (c):</b> Using <code>shell=True</code> passes user input to the OS command interpreter, allowing metacharacters like <code>&&</code> or <code>&</code> to chain arbitrary commands.<br/>'
        '<b>4. Implemented Mitigation (d):</b> Strict IP allow-list validation using Python\'s <code>ipaddress</code> module, plus parameterized execution with argument vectors: '
        '<code>subprocess.run([\'ping\', \'-n\', \'1\', target], shell=False)</code>. In Mitigated Mode, submitting metacharacters triggers an immediate blocked defense.<br/>'
        '<b>5. Other Mitigations (e):</b> Avoiding the shell via native socket APIs, running under a least-privileged service account, and sandboxing."'
    )
    story.append(create_callout_box("🎙️ Prince's Narration Script", prince_speech, "#f8fafc", "#cbd5e1"))
    story.append(Spacer(1, 12))

    story.append(PageBreak())

    # Segment 4: Chandan Kumar Das
    story.append(Paragraph("Segment 4: Chandan Kumar Das (IIT2024070) — Stored XSS (08:15 - 10:45)", styles['h1']))
    story.append(Paragraph("<b>Target Route:</b> <code>/xss-stored</code> | <b>Mode:</b> Vulnerable &rarr; Mitigated", styles['body']))
    chandan_speech = (
        '<b>1. Vulnerable Code (a):</b> "This forum stores comments in SQLite and renders them in Jinja2 using the unescaped filter: '
        '<code>{{ comment.message | safe }}</code>.<br/>'
        '<b>2. Working Exploit (b):</b> I enter <code>&lt;script&gt;alert(\'Stored XSS! Cookie: \' + document.cookie);&lt;/script&gt;</code>. '
        'Submitting triggers an immediate browser alert showing the active session cookie! Every subsequent visitor also executes the payload.<br/>'
        '<b>3. Root Cause (c):</b> Untrusted input is stored and inserted into the DOM without HTML entity encoding, causing the browser to parse script tags as executable JavaScript.<br/>'
        '<b>4. Implemented Mitigation (d):</b> Server-side HTML entity escaping with <code>html.escape()</code> and removing <code>| safe</code> for automatic template escaping. '
        'In Mitigated Mode, submitting the script renders harmlessly as plain text <code>&amp;lt;script&amp;gt;</code> without executing.<br/>'
        '<b>5. Other Mitigations (e):</b> Content Security Policy (CSP), HttpOnly cookie flag to prevent cookie theft, and DOMPurify sanitizers."'
    )
    story.append(create_callout_box("🎙️ Chandan's Narration Script", chandan_speech, "#f8fafc", "#cbd5e1"))
    story.append(Spacer(1, 12))

    # Segment 5: Raghvendra
    story.append(Paragraph("Segment 5: Raghvendra (IIT2024062) — POST-based CSRF (10:45 - 13:15)", styles['h1']))
    story.append(Paragraph("<b>Target Routes:</b> <code>/csrf-post</code> and <code>/attacker-portal</code> | <b>Mode:</b> Vulnerable &rarr; Mitigated", styles['body']))
    raghvendra_speech = (
        '<b>1. Vulnerable Code (a):</b> "The wire transfer endpoint <code>POST /csrf-post/transfer</code> executes transfers relying solely on ambient session cookies without checking user intent.<br/>'
        '<b>2. Working Exploit (b):</b> The attacker hosts <code>/attacker-portal</code> with a hidden auto-submitting POST form targeting the bank URL: '
        '<code>&lt;form id=\'f\' action=\'/csrf-post/transfer\' method=\'POST\'&gt;...&lt;/form&gt;&lt;script&gt;f.submit();&lt;/script&gt;</code>. '
        'When the logged-in victim visits the attacker page, $5,000 is silently transferred without consent!<br/>'
        '<b>3. Root Cause (c):</b> Browsers automatically attach cookies to cross-site requests, and the server fails to require proof of origin or intent.<br/>'
        '<b>4. Implemented Mitigation (d):</b> Synchronizer Token Pattern (Anti-CSRF Token). In Mitigated Mode, the server verifies <code>submitted_token == session[\'csrf_token\']</code>. '
        'When the external attacker site submits, it is rejected with <code>403 FORBIDDEN: Missing or invalid Anti-CSRF Token</code>.<br/>'
        '<b>5. Other Mitigations (e):</b> SameSite cookie attribute (Strict/Lax), step-up re-authentication/OTP, and validating Origin/Referer headers."'
    )
    story.append(create_callout_box("🎙️ Raghvendra's Narration Script", raghvendra_speech, "#f8fafc", "#cbd5e1"))
    story.append(Spacer(1, 12))

    # Segment 6: Conclusion
    story.append(Paragraph("Segment 6: Group Conclusion (13:15 - 14:00)", styles['h1']))
    concl_speech = (
        '"To wrap up, all five group members have successfully demonstrated their assigned vulnerability variants, '
        'executed real-world exploits, and verified robust defensive mitigations. The complete code and automated test suite '
        'are available in our public GitHub repository. Thank you!"'
    )
    story.append(create_callout_box("🎙️ Group Wrap-Up", concl_speech, "#eff6ff", "#93c5fd"))

    doc.build(story, canvasmaker=NumberedCanvas)
    print("Built:", pdf_filename)


def build_viva_guide_pdf():
    pdf_filename = os.path.join(BASE_DIR, 'VIVA_PREPARATION_GUIDE.pdf')
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = get_custom_styles()
    story = []

    # Title & Header
    story.append(Paragraph("🎓 Individual Viva Preparation & Defense Guide", styles['title']))
    story.append(Paragraph("Indian Institute of Information Technology Allahabad | Cyber Security (IT-30001)<br/>Course Instructor: Dr. Soumyadev Maity | Master Defense Bank for Group Members", styles['subtitle']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0"), spaceAfter=10))

    # Introduction block
    story.append(Paragraph("<b>Viva Evaluation Instructions:</b> The viva is individual: each member's score depends on demonstrating and explaining their own variant, including the working exploit, root cause, the one implemented mitigation, and the theory of alternative mitigations from lecture slides.", styles['body']))
    story.append(Spacer(1, 8))

    # Ajay Bole
    story.append(Paragraph("1. Ajay Bole (IIT2024088) — SQL Injection: Auth Bypass", styles['h1']))
    qa_ajay = [
        ("Q1: What is the exact root cause of your vulnerability?",
         "Dynamic string concatenation where user input is directly formatted into a SQL query string before execution: f'SELECT * FROM users WHERE username = \\'{username}\\' AND password = \\'{password}\\''. The single quote closes the literal and the double hyphen (--) comments out password checking."),
        ("Q2: How does your implemented mitigation prevent this attack?",
         "Prepared statements with parameterized queries (SELECT ... WHERE username = ? AND password = ?). The database pre-compiles the SQL syntax before binding parameter values. The payload admin' -- is evaluated strictly as literal data, preventing syntax modification."),
        ("Q3: Explain the other mitigations from the lecture slides.",
         "1. Allow-list input validation: Restricting usernames to regex ^[a-zA-Z0-9_]{3,20}$.<br/>2. Least-privilege DB accounts: Granting minimal permissions to the web app connection.<br/>3. Safe generic errors: Suppressing database error traces to prevent reconnaissance.")
    ]
    for q, a in qa_ajay:
        story.append(Paragraph(f"<b>{q}</b>", styles['h2']))
        story.append(Paragraph(a, styles['body']))
        story.append(Spacer(1, 4))
    story.append(Spacer(1, 8))

    # Sayan Biswas
    story.append(Paragraph("2. Sayan Biswas (IIT2024090) — SQL Injection: UNION Data Extraction", styles['h1']))
    qa_sayan = [
        ("Q1: What are the two prerequisites for a successful UNION SQLi?",
         "1. The injected query must select the exact same number of columns as the original query (here, 5 columns).<br/>2. The corresponding data types in each column must be compatible between the queries."),
        ("Q2: How does your mitigation stop ' UNION SELECT id, username, password, role, secret_flag FROM users --?",
         "Using parameterized queries: cursor.execute('SELECT ... WHERE category = ?', (category,)). The entire string is bound as a single literal category parameter, so SQLite never executes the UNION statement."),
        ("Q3: Explain the other mitigations from the lecture slides.",
         "1. Category allow-listing: Verifying requested category against an allowed list.<br/>2. Database account privilege partitioning: Restricting the catalog account from reading the users table.<br/>3. Safe error handling: Suppressing syntax errors so column count probing fails.")
    ]
    for q, a in qa_sayan:
        story.append(Paragraph(f"<b>{q}</b>", styles['h2']))
        story.append(Paragraph(a, styles['body']))
        story.append(Spacer(1, 4))

    story.append(PageBreak())

    # Prince Kumar
    story.append(Paragraph("3. Prince Kumar (IIT2024085) — OS Command Injection: In-Band", styles['h1']))
    qa_prince = [
        ("Q1: What makes command injection possible and why is it 'in-band'?",
         "Command injection occurs when user input is passed to an OS shell interpreter (shell=True), allowing operators like && or & to chain commands. It is 'in-band' because command output (stdout/stderr) is returned directly within the HTTP response."),
        ("Q2: How does your defense block '127.0.0.1 && whoami'?",
         "Defense uses two layers: 1) Strict IP validation using python's ipaddress module (rejects metacharacters immediately), and 2) Parameterized execution with argument vectors: subprocess.run(['ping', '-n', '1', target], shell=False). The string is passed as a literal argument without invoking cmd.exe/sh."),
        ("Q3: Explain the other mitigations from the lecture slides.",
         "1. Avoid the shell: Using native socket libraries for reachability checks.<br/>2. Least-privilege service account: Running web service under an unprivileged user.<br/>3. Sandboxing & containerization: Limiting filesystem and binary access.")
    ]
    for q, a in qa_prince:
        story.append(Paragraph(f"<b>{q}</b>", styles['h2']))
        story.append(Paragraph(a, styles['body']))
        story.append(Spacer(1, 4))
    story.append(Spacer(1, 8))

    # Chandan Kumar Das
    story.append(Paragraph("4. Chandan Kumar Das (IIT2024070) — Cross-Site Scripting: Stored XSS", styles['h1']))
    qa_chandan = [
        ("Q1: Why is Stored XSS more severe than Reflected XSS?",
         "In Stored XSS, the payload is persisted in server storage (database). It does not require tricking victims into clicking a malicious link; any legitimate user who views the page automatically executes the injected script."),
        ("Q2: How does HTML entity encoding prevent script execution?",
         "HTML encoding converts special markup characters into character entities: < to &lt;, > to &gt;, and \" to &quot;. The browser renders them visually as text but does not parse them as executable DOM script elements."),
        ("Q3: Explain the other mitigations from the lecture slides.",
         "1. Content Security Policy (CSP): Restricting script sources and blocking inline scripts.<br/>2. HttpOnly cookie flag: Preventing script access to session cookies via document.cookie.<br/>3. HTML sanitizers: Using libraries like DOMPurify to strip dangerous elements.")
    ]
    for q, a in qa_chandan:
        story.append(Paragraph(f"<b>{q}</b>", styles['h2']))
        story.append(Paragraph(a, styles['body']))
        story.append(Spacer(1, 4))
    story.append(Spacer(1, 8))

    # Raghvendra
    story.append(Paragraph("5. Raghvendra (IIT2024062) — CSRF: POST-based Auto-Submit", styles['h1']))
    qa_raghvendra = [
        ("Q1: What conditions are required for a CSRF attack to succeed?",
         "1. The victim must possess an active, authenticated session (cookie).<br/>2. The application performs sensitive state changes without verifying user intent.<br/>3. All request parameters are predictable (no unguessable secrets)."),
        ("Q2: How does the Synchronizer Token Pattern mitigate CSRF?",
         "A cryptographically random token is generated per session and required in POST request bodies. Because the attacker site is barred by the Same-Origin Policy (SOP) from reading the victim's token, forged cross-origin requests cannot include a valid token and are rejected with HTTP 403."),
        ("Q3: Explain the other mitigations from the lecture slides.",
         "1. SameSite cookie attribute: Setting SameSite=Lax/Strict stops browsers from sending cookies on cross-site requests.<br/>2. Re-authentication / OTP: Requiring step-up verification for transfers.<br/>3. Avoiding state-changing GETs: Maintaining HTTP verb semantics.")
    ]
    for q, a in qa_raghvendra:
        story.append(Paragraph(f"<b>{q}</b>", styles['h2']))
        story.append(Paragraph(a, styles['body']))
        story.append(Spacer(1, 4))

    doc.build(story, canvasmaker=NumberedCanvas)
    print("Built:", pdf_filename)

if __name__ == '__main__':
    build_video_script_pdf()
    build_viva_guide_pdf()
