import secrets
from django.core.cache import cache
from django.contrib.auth.hashers import make_password, check_password

TTL = 300
MAX_TRIES = 5

def _key(purpose, identifier):
    return f"otp:{purpose}:{identifier.lower()}"

def generate_otp(purpose, identifier):
    plain = f"{secrets.randbelow(10**6):06d}"
    k = _key(purpose, identifier)
    cache.set(k, make_password(plain), TTL)   # overwrites any old OTP
    cache.set(k + ":tries", 0, TTL)
    return plain

def verify_otp(purpose, identifier, plain):
    k = _key(purpose, identifier)
    hashed = cache.get(k)
    if hashed is None:                         # expired or never created
        return False
    tries = cache.get(k + ":tries", 0)
    if tries >= MAX_TRIES:
        cache.delete_many([k, k + ":tries"])
        return False
    if not check_password(plain, hashed):
        cache.set(k + ":tries", tries + 1, TTL)
        return False
    cache.delete_many([k, k + ":tries"])       # single use
    return True