"""
Test file with multiple security violations for testing GitHub Copilot Guardrails
This file intentionally contains security vulnerabilities for testing purposes.
DO NOT USE IN PRODUCTION!
"""

# ============================================================================
# CRITICAL: Hardcoded Secrets and Credentials
# ============================================================================

# Violation: Hardcoded API Key (using fake keys to avoid GitHub Push Protection)
api_key = "FAKE_API_KEY_1234567890abcdefghijklmnopqrstuvwxyz"
secret_key = "FAKE_SECRET_KEY_12345678901234567890"
password = "FAKE_PASSWORD_12345"
token = "Bearer FAKE_TOKEN_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0"

# Violation: AWS Credentials (fake credentials)
aws_access_key_id = "FAKE_AKIAIOSFODNN7EXAMPLE"
aws_secret_access_key = "FAKE_wJalrXUtnFEMI_K7MDENG_bPxRfiCYEXAMPLEKEY"

# Violation: Database Connection String with Password (fake)
database_url = "postgresql://fake_user:FAKE_PASSWORD_123@localhost:5432/testdb"
db_password = "FAKE_DB_PASSWORD_12345"

# Violation: Stripe Secret Key (fake - starts with FAKE_ to avoid GitHub detection)
stripe_secret_key = "FAKE_sk_live_51Hqw2eKvRoJbGIdRspyzFqG9XeZ2KbYcL3mN4oP5qR6sT7uV8wX9yZ0"

# Violation: Private Key (PEM format) - FAKE key for testing
private_key = """-----BEGIN FAKE RSA PRIVATE KEY-----
FAKE_MIIEpAIBAAKCAQEA1234567890abcdefghijklmnopqrstuvwxyz
FAKE_ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghijklmnop
-----END FAKE RSA PRIVATE KEY-----"""

# ============================================================================
# HIGH: SQL Injection Vulnerabilities
# ============================================================================

def unsafe_query_vulnerable(user_id):
    """Violation: SQL Injection via string concatenation"""
    query = "SELECT * FROM users WHERE id = " + user_id
    return execute(query)

def unsafe_query_fstring(user_input):
    """Violation: SQL Injection via f-string"""
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    return execute(query)

def unsafe_query_format(user_input):
    """Violation: SQL Injection via string format"""
    query = "SELECT * FROM products WHERE category = '{}'".format(user_input)
    return execute(query)

def unsafe_query_percent(user_input):
    """Violation: SQL Injection via % formatting"""
    query = "DELETE FROM orders WHERE user_id = %s" % user_input
    return execute(query)

# ============================================================================
# CRITICAL: Unsafe Deserialization
# ============================================================================

import pickle
import json

def unsafe_pickle_load(user_data):
    """Violation: Unsafe pickle deserialization"""
    data = pickle.loads(user_data)  # CWE-502
    return data

def unsafe_pickle_load_file(filename):
    """Violation: Unsafe pickle file loading"""
    with open(filename, 'rb') as f:
        data = pickle.load(f)  # CWE-502
    return data

def unsafe_json_loads(user_input):
    """Violation: Potentially unsafe JSON deserialization"""
    # This could be unsafe if user_input contains malicious JSON
    data = json.loads(user_input)
    return data

# ============================================================================
# CRITICAL: Code Injection (eval/exec)
# ============================================================================

def unsafe_eval(user_input):
    """Violation: Use of eval() - Code Injection"""
    result = eval(user_input)  # CWE-95
    return result

def unsafe_exec(user_code):
    """Violation: Use of exec() - Code Injection"""
    exec(user_code)  # CWE-95
    return "Executed"

def unsafe_exec_globals(user_code):
    """Violation: exec() with user-controlled globals"""
    exec(user_code, {"__builtins__": __builtins__})  # CWE-95

# ============================================================================
# HIGH: Command Injection
# ============================================================================

import subprocess
import os

def unsafe_shell_execution(user_command):
    """Violation: Unsafe shell execution"""
    subprocess.run(user_command, shell=True)  # CWE-78

def unsafe_subprocess_call(user_input):
    """Violation: Command injection via subprocess"""
    subprocess.call(f"rm -rf {user_input}", shell=True)  # CWE-78

def unsafe_os_system(user_command):
    """Violation: Command injection via os.system"""
    os.system(f"ls -la {user_command}")  # CWE-78

# ============================================================================
# HIGH: Path Traversal
# ============================================================================

def unsafe_file_open(user_path):
    """Violation: Path traversal vulnerability"""
    with open(f"../data/{user_path}", 'r') as f:  # CWE-22
        return f.read()

def unsafe_file_access(filename):
    """Violation: Unsafe file access"""
    file_path = f"/tmp/{filename}"
    with open(file_path, 'r') as f:
        return f.read()

# ============================================================================
# MEDIUM: Insecure Random Number Generation
# ============================================================================

import random

def insecure_random_token():
    """Violation: Using insecure random for security token"""
    token = random.randint(1000, 9999)  # Should use secrets module
    return str(token)

def insecure_password_generation():
    """Violation: Weak password generation"""
    password = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(8))
    return password

# ============================================================================
# MEDIUM: Hardcoded Cryptographic Keys
# ============================================================================

def weak_encryption_key():
    """Violation: Hardcoded encryption key"""
    key = b"1234567890123456"  # Should be randomly generated
    return key

# ============================================================================
# HIGH: Insecure HTTP Requests
# ============================================================================

import urllib.request

def insecure_url_open(user_url):
    """Violation: Insecure URL opening without validation"""
    response = urllib.request.urlopen(user_url)  # CWE-918
    return response.read()

# ============================================================================
# MEDIUM: Missing Input Validation
# ============================================================================

def no_input_validation(user_input):
    """Violation: No input validation"""
    # Process user input without validation
    result = process_data(user_input)
    return result

def weak_input_validation(email):
    """Violation: Weak input validation"""
    if '@' in email:  # Too weak
        return send_email(email)
    return None

# ============================================================================
# MEDIUM: Insecure Temporary Files
# ============================================================================

import tempfile

def insecure_temp_file(user_data):
    """Violation: Insecure temporary file creation"""
    temp_file = tempfile.NamedTemporaryFile(delete=False)  # CWE-377
    temp_file.write(user_data.encode())
    temp_file.close()
    return temp_file.name

# ============================================================================
# LOW: Information Disclosure
# ============================================================================

def expose_sensitive_info(error):
    """Violation: Exposing sensitive information in error messages"""
    raise Exception(f"Database error: {error}")  # May expose DB structure

def debug_mode_enabled():
    """Violation: Debug mode in production"""
    DEBUG = True  # Should be False in production
    return DEBUG

# ============================================================================
# MEDIUM: Weak Cryptography
# ============================================================================

import hashlib

def weak_hash_password(password):
    """Violation: Using weak hash function (MD5)"""
    return hashlib.md5(password.encode()).hexdigest()  # CWE-327

def weak_hash_salt(password):
    """Violation: Weak salt for password hashing"""
    salt = "static_salt"  # Should be random
    return hashlib.sha256((password + salt).encode()).hexdigest()

# ============================================================================
# HIGH: Insecure Direct Object Reference
# ============================================================================

def insecure_file_access_by_id(file_id):
    """Violation: Direct file access without authorization check"""
    file_path = f"/files/{file_id}.txt"
    with open(file_path, 'r') as f:
        return f.read()

# ============================================================================
# MEDIUM: Missing Error Handling
# ============================================================================

def no_error_handling(user_input):
    """Violation: Missing error handling"""
    result = dangerous_operation(user_input)
    return result  # No try-except

# ============================================================================
# LOW: Code Quality Issues (for AI detection)
# ============================================================================

def generic_function_name(data):
    """This function processes data"""
    result = []
    for item in data:
        result.append(item)
    return result

def no_docstring(param1, param2):
    value = param1 + param2
    return value

# ============================================================================
# Test Functions (Helper functions referenced above)
# ============================================================================

def execute(query):
    """Mock database execute function"""
    print(f"Executing: {query}")
    return []

def process_data(data):
    """Mock data processing function"""
    return data.upper()

def send_email(email):
    """Mock email sending function"""
    print(f"Sending email to: {email}")
    return True

def dangerous_operation(input_data):
    """Mock dangerous operation"""
    return input_data

# ============================================================================
# Main execution (for testing)
# ============================================================================

if __name__ == "__main__":
    print("Security Violations Test File")
    print("This file contains intentional security vulnerabilities for testing.")
    print("DO NOT USE IN PRODUCTION!")
    
    # Test some functions
    test_input = "test"
    unsafe_query_vulnerable(test_input)
    unsafe_eval("print('test')")
    insecure_random_token()
