import hashlib
import secrets

from pwdlib import PasswordHash

_password_hash = PasswordHash.recommended()  # argon2id


def hash_password(password: str) -> str:
    return _password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return _password_hash.verify(password, hashed)


def generate_token() -> str:
    """推測できない乱数トークン (約256ビット、43文字)。セッションと招待リンクで使う。"""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """トークンの SHA-256 (16進64文字)。セッションは DB にこのハッシュだけを保存する。"""
    return hashlib.sha256(token.encode()).hexdigest()
