from passlib.context import CryptContext

_crypt_context = CryptContext(schemes=["bcrypt"])


def hash_password(password: str) -> str:
    """
    Hashes given password with salt.
    """
    return _crypt_context.hash(password)


def verify_password(password: str, hash_: str) -> bool:
    """
    Verifies password with a hash.
    """
    return _crypt_context.verify(password, hash_)
