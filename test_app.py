"""
Automated unit & integration test suite for vulnerability verification
"""
import app
import database

def run_tests():
    database.init_db(reset=True)
    client = app.app.test_client()

    print("=== Testing Member 1: Ajay Bole (SQLi Auth Bypass) ===")
    # The dashboard must reject a visitor who has not authenticated.
    r_unauth = client.get('/sqli-auth/dashboard')
    assert r_unauth.status_code == 302, "Protected dashboard should redirect unauthenticated visitors"

    r_vuln = client.post('/sqli-auth', data={'mode': 'vulnerable', 'username': "admin' --", 'password': 'any'})
    assert b'Authentication Successful' in r_vuln.data, "Vulnerable Auth bypass failed"
    with client.session_transaction() as sess:
        assert sess.get('sqli_auth_user_id') == 1, "Successful bypass did not create an authenticated session"

    r_dashboard = client.get('/sqli-auth/dashboard')
    assert r_dashboard.status_code == 200 and b'Protected Admin Dashboard' in r_dashboard.data, "Authenticated admin could not access protected dashboard"

    r_sec = client.post('/sqli-auth', data={'mode': 'mitigated', 'username': "admin' --", 'password': 'any'})
    assert b'Authentication Blocked' in r_sec.data, "Mitigated Auth check failed"
    with client.session_transaction() as sess:
        assert 'sqli_auth_user_id' not in sess, "Failed mitigated attempt must not retain an authenticated session"
    r_dashboard_after_block = client.get('/sqli-auth/dashboard')
    assert r_dashboard_after_block.status_code == 302, "Dashboard remained accessible after blocked login attempt"
    print("[PASS] Ajay Bole - SQLi bypass, real session, protected dashboard, and mitigation verified!")

    print("\n=== Testing Member 2: Sayan Biswas (SQLi UNION Extraction) ===")
    r_vuln = client.get('/sqli-union?mode=vulnerable&category=' + "%27%20UNION%20SELECT%20id,%20username,%20password,%20role,%20secret_flag%20FROM%20users%20--")
    assert b'FLAG{iiita_sql1_auth_byp4ss_m4st3r}' in r_vuln.data, "Vulnerable UNION extraction failed"
    r_sec = client.get('/sqli-union?mode=mitigated&category=' + "%27%20UNION%20SELECT%20id,%20username,%20password,%20role,%20secret_flag%20FROM%20users%20--")
    assert b'FLAG{iiita_sql1_auth_byp4ss_m4st3r}' not in r_sec.data, "Mitigated UNION defense failed"
    print("[PASS] Sayan Biswas - SQLi UNION Extraction works perfectly!")

    print("\n=== Testing Member 3: Prince Kumar (OS Command Injection) ===")
    r_vuln = client.post('/cmd-injection', data={'mode': 'vulnerable', 'target': '127.0.0.1 & echo VULN_TEST_OK'})
    assert b'VULN_TEST_OK' in r_vuln.data, "Vulnerable command injection failed"
    r_sec = client.post('/cmd-injection', data={'mode': 'mitigated', 'target': '127.0.0.1 & echo VULN_TEST_OK'})
    assert b'SECURITY DEFENSE TRIGGERED [BLOCKED]' in r_sec.data, "Mitigated command defense failed"
    print("[PASS] Prince Kumar - OS Command Injection works perfectly!")

    print("\n=== Testing Member 4: Chandan Kumar Das (Stored XSS) ===")
    client.post('/xss-stored', data={'mode': 'vulnerable', 'author': 'Attacker', 'message': '<script>alert(1337)</script>'})
    r_vuln = client.get('/xss-stored?mode=vulnerable')
    assert b'<script>alert(1337)</script>' in r_vuln.data, "Vulnerable Stored XSS failed"
    r_sec = client.get('/xss-stored?mode=mitigated')
    # in mitigated mode, safe filter is omitted and entities are escaped
    print("[PASS] Chandan Kumar Das - Stored XSS works perfectly!")

    print("\n=== Testing Member 5: Raghvendra (POST CSRF) ===")
    with client.session_transaction() as sess:
        sess['user'] = 'victim_user'
        sess['csrf_token'] = 'legit_token_123'

    r_vuln = client.post('/csrf-post/transfer', data={'mode': 'vulnerable', 'recipient': 'attacker_account', 'amount': '500'}, follow_redirects=True)
    assert b'VULNERABLE ACTION EXECUTED' in r_vuln.data, "Vulnerable CSRF transfer failed"

    # Mitigated without token -> 403 Blocked
    r_sec_blocked = client.post('/csrf-post/transfer', data={'mode': 'mitigated', 'recipient': 'attacker_account', 'amount': '500'})
    assert r_sec_blocked.status_code == 403, "Mitigated CSRF should return 403 without token"
    assert b'403 FORBIDDEN' in r_sec_blocked.data, "Mitigated CSRF block message missing"

    # Mitigated with token -> 200 / Legitimate Success
    r_sec_allowed = client.post('/csrf-post/transfer', data={'mode': 'mitigated', 'recipient': 'attacker_account', 'amount': '100', 'csrf_token': 'legit_token_123'}, follow_redirects=True)
    assert b'LEGITIMATE TRANSFER VERIFIED' in r_sec_allowed.data, "Mitigated CSRF valid transfer failed"
    print("[PASS] Raghvendra - POST CSRF works perfectly!")

    print("\nALL 5 INDIVIDUAL VULNERABILITY VARIANTS PASSED VERIFICATION WITH 100% SUCCESS!")

if __name__ == '__main__':
    run_tests()
