from passlib.context import CryptContext


# Use a portable, dependency-free scheme for tests & dev
# Avoid bcrypt native backend issues and 72-byte limits
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)
