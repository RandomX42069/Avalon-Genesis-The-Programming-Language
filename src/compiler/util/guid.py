import random

def GUIDgen():
    allowed = "abcdef0123456789"
    return ''.join(random.choice(allowed) for _ in range(8)) + "-" + ''.join(random.choice(allowed) for _ in range(4)) + "-" + ''.join(random.choice(allowed) for _ in range(4)) + "-" + ''.join(random.choice(allowed) for _ in range(4)) + "-" + ''.join(random.choice(allowed) for _ in range(6))