import random
import string


def generate_secure_password(chars=8, nums=6, symbols=2):
    letters = random.sample(string.ascii_letters, chars)
    digits = random.sample(string.digits, nums)
    puncts = random.sample("!@#$%^&*", symbols)
    combined = letters + digits + puncts
    random.shuffle(combined)
    return "".join(combined)
