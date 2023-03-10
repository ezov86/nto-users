import jwt

from datetime import datetime, timedelta

_ALGORITHM = "HS256"


class InvalidJWTError(Exception):
    def __init__(self):
        super().__init__("Invalid JWT")


def encode_jwt(sub: str, secret: str, expire_in_seconds: int | None = None, extra_payload: dict = None) -> str:
    """
    Encodes and encrypts token.

    :param sub: token's subject (use for username if required).
    :param secret: encrypting secret.
    :param expire_in_seconds: lifetime of token in seconds. If None then no "exp" added.
    :param extra_payload: any JSON data. If None then no extra data is included.

    :return: encoded and encrypted token as a string.
    """

    if extra_payload is None:
        extra_payload = dict()

    payload = {
        **extra_payload,
        "sub": sub
    }

    if expire_in_seconds is not None:
        payload["exp"] = datetime.utcnow() + timedelta(seconds=expire_in_seconds)

    return jwt.encode(payload, secret, _ALGORITHM)


def decode_jwt(token: str, required_payload_fields: list[str], secret: str) -> dict:
    """
    Decodes and verifies given token.

    :param token: given token.
    :param required_payload_fields: names of fields that the payload should contain.
        "sub" will be checked in any way.
    :param secret: encoding encrypting secret.

    :raises InvalidTokenError: token is invalid or it's payload doesn't contain required fields.

    :return: payload dictionary.
    """
    try:
        payload = jwt.decode(token, secret, _ALGORITHM)
    except Exception:  # pyjwt may raise many exceptions (sometimes ValueError, for example).
        raise InvalidJWTError()


    for required in required_payload_fields + ["sub"]:
        if required not in payload:
            raise InvalidJWTError()

    return payload
