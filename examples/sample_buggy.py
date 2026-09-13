# Sample buggy file for KV-13 demo
import hashlib
import random

def get_user(user_input):
    # BUG: SQL injection
    query = "SELECT * FROM users WHERE id = " + user_input
    # BUG: code injection
    result = eval(user_input)
    # BUG: weak hash
    h = hashlib.md5(user_input.encode()).hexdigest()
    # BUG: division by zero
    return result / 0

# TODO: add auth
