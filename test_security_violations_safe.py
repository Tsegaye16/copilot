

# ============================================================================
# CRITICAL: Hardcoded Secrets and Credentials (FAKE - for testing only)
# ============================================================================

# Violation: Hardcoded API Key (fake)
api_key = "FAKE_API_KEY_1234567890abcdefghijklmnopqrstuvwxyz"
secret_key = "FAKE_SECRET_KEY_12345678901234567890"
password = "FAKE_PASSWORD_admin123"
token = "Bearer FAKE_TOKEN_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"

# Violation: AWS Credentials (fake)
aws_access_key_id = "FAKE_AKIAIOSFODNN7EXAMPLE"
aws_secret_access_key = "FAKE_wJalrXUtnFEMI_K7MDENG_bPxRfiCYEXAMPLEKEY"

# Violation: Database Connection String with Password (fake)
database_url = "postgresql://fake_user:FAKE_PASSWORD_123@localhost:5432/testdb"
db_password = "FAKE_DB_PASSWORD_12345"

# Violation: Stripe Secret Key (fake - prefixed to avoid GitHub detection)
stripe_secret_key = "FAKE_sk_live_51Hqw2eKvRoJbGIdRspyzFqG9XeZ2KbYcL3mN4oP5qR6sT7uV8wX9yZ0"

# Violation: Private Key (PEM format) - FAKE key
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

# ============================================================================
# MEDIUM: Weak Cryptography
# ============================================================================

import hashlib

def weak_hash_password(password):
    """Violation: Using weak hash function (MD5)"""
    return hashlib.md5(password.encode()).hexdigest()  # CWE-327

# ============================================================================
# MEDIUM: Missing Input Validation
# ============================================================================

def no_input_validation(user_input):
    """Violation: No input validation"""
    result = process_data(user_input)
    return result

# ============================================================================
# Helper Functions
# ============================================================================

def execute(query):
    """Mock database execute function"""
    print(f"Executing: {query}")
    return []

def process_data(data):
    """Mock data processing function"""
    return data.upper()

if __name__ == "__main__":
    print("Security Violations Test File (Safe Version)")
    print("This file contains FAKE credentials to avoid GitHub Push Protection.")
    print("All secrets are prefixed with FAKE_ to indicate they're test data.")
    print("DO NOT USE IN PRODUCTION!")
