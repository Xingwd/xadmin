import random
import string


def generate_secure_password(chars: int = 8, nums: int = 6, symbols: int = 2) -> str:
    letters = random.sample(string.ascii_letters, chars)
    digits = random.sample(string.digits, nums)
    puncts = random.sample("!@#$%^&*", symbols)
    combined = letters + digits + puncts
    random.shuffle(combined)
    return "".join(combined)
