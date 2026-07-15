from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, InvalidHash


ph = PasswordHasher(
    time_cost=2,
    memory_cost=19456,
    parallelism=1,
    hash_len=32,
    salt_len=16,
)

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    
    try:
        return ph.verify(hashed_password, plain_password)
    except (VerificationError, InvalidHash):
        return False