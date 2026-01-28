"""
Test file for guardrails - contains intentional security issues
This will trigger warnings in warning mode

NOTE: Using fake patterns that won't trigger GitHub's push protection
but will still be detected by our guardrails system.
"""

# Hardcoded API key (SEC001 - Critical)
# Using pattern that matches our scanner but not GitHub's secret scanner
api_key = "test_api_key_12345678901234567890"
API_KEY = "fake_api_key_for_testing_purposes_only"

# Hardcoded password (SEC002 - Critical)
# Using generic password pattern
password = "test_password_123"
DATABASE_PASSWORD = "fake_database_password_for_testing"

# SQL injection risk (SEC101 - High)
def get_user_data(user_id):
    """Get user data - vulnerable to SQL injection"""
    # String concatenation in SQL query
    query = "SELECT * FROM users WHERE id = " + str(user_id)
    return execute_query(query)

# Another SQL injection pattern
def search_users(search_term):
    """Search users - vulnerable to SQL injection"""
    query = f"SELECT * FROM users WHERE name LIKE '{search_term}'"
    return execute_query(query)

# Unsafe deserialization (SEC204 - High)
import pickle
def load_config(data):
    """Load config - unsafe deserialization"""
    return pickle.loads(data)

# Command injection risk (SEC203 - High)
import subprocess
def delete_file(filename):
    """Delete file - unsafe shell execution"""
    subprocess.run(f"rm -rf {filename}", shell=True)
