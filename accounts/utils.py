# utils.py
import string
import random

def generateRandomPassword(length=10):
    charset = string.ascii_letters + string.digits
    password = ''.join(random.choice(charset) for _ in range(length))
    return password
