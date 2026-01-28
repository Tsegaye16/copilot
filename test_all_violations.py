"""
Comprehensive test file with ALL types of security violations
Use this file to test the complete guardrails system.
"""

# ============================================================================
# CRITICAL VIOLATIONS - Hardcoded Secrets
# ============================================================================

# Using FAKE_ prefix to avoid GitHub Push Protection while still testing guardrails
API_KEY = "FAKE_sk_live_51Hqw2eKvRoJbGIdRspyzFqG9XeZ2KbYcL3mN4oP5qR6sT7uV8wX9yZ0"
SECRET_KEY = "FAKE_my_secret_key_12345678901234567890"
PASSWORD = "FAKE_SuperSecretPassword123!"
DATABASE_PASSWORD = "FAKE_db_pass_12345"
AWS_ACCESS_KEY = "FAKE_AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY = "FAKE_wJalrXUtnFEMI_K7MDENG_bPxRfiCYEXAMPLEKEY"

# ============================================================================
# CRITICAL VIOLATIONS - SQL Injection
# ============================================================================

def get_user_data(user_id):
    """SQL Injection via string concatenation"""
    query = "SELECT * FROM users WHERE id = " + user_id
    return execute(query)

def search_products(search_term):
    """SQL Injection via f-string"""
    query = f"SELECT * FROM products WHERE name LIKE '%{search_term}%'"
    return execute(query)

# ============================================================================
# CRITICAL VIOLATIONS - Code Injection
# ============================================================================

def process_user_code(user_code):
    """Code injection via eval"""
    return eval(user_code)

def execute_user_script(script):
    """Code injection via exec"""
    exec(script)

# ============================================================================
# CRITICAL VIOLATIONS - Command Injection
# ============================================================================

import subprocess
import os

def run_command(user_input):
    """Command injection"""
    os.system(f"ls -la {user_input}")

def delete_file(filename):
    """Unsafe command execution"""
    subprocess.run(f"rm -rf {filename}", shell=True)

# ============================================================================
# CRITICAL VIOLATIONS - Unsafe Deserialization
# ============================================================================

import pickle
import json

def load_user_data(data):
    """Unsafe pickle deserialization"""
    return pickle.loads(data)

def parse_json_data(json_str):
    """Potentially unsafe JSON parsing"""
    return json.loads(json_str)

# ============================================================================
# HIGH VIOLATIONS - Path Traversal
# ============================================================================

def read_file(filename):
    """Path traversal vulnerability"""
    with open(f"../data/{filename}", 'r') as f:
        return f.read()

# ============================================================================
# MEDIUM VIOLATIONS - Weak Cryptography
# ============================================================================

import hashlib

def hash_password(password):
    """Weak MD5 hashing"""
    return hashlib.md5(password.encode()).hexdigest()

# ============================================================================
# MEDIUM VIOLATIONS - Missing Input Validation
# ============================================================================

def process_email(email):
    """No input validation"""
    return send_email(email)

def update_profile(user_id, data):
    """Weak validation"""
    if user_id:
        save_profile(user_id, data)

# ============================================================================
# Helper Functions
# ============================================================================

def execute(query):
    print(f"Executing: {query}")
    return []

def send_email(email):
    print(f"Sending to: {email}")

def save_profile(user_id, data):
    print(f"Saving profile for {user_id}")

if __name__ == "__main__":
    print("All Violations Test File")
    print("Contains comprehensive security violations for testing.")
