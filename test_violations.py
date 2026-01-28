# Test file with security issues
   api_key = "sk_live_1234567890abcdef"
   password = "admin123"
   
   def unsafe_query(user_input):
       query = "SELECT * FROM users WHERE id = " + user_input
       return execute(query)
   
   import pickle
   data = pickle.loads(user_input)  # Unsafe deserialization