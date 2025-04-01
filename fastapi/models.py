import hashlib
from pydantic import BaseModel
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class UserDB(BaseModel):
    login: str
    password: str

class UrlDB(BaseModel):
    id: int
    save_url: str
    short_url: str
    created_by_login: bool
    exp_time: datetime | None = None

class StatsDB(BaseModel):
    id: int
    date_created: datetime
    use_count: int
    date_last: datetime | None = None

def shorten_string(long_str: str, length) -> str:
    hash_obj = hashlib.sha256(long_str.encode())
    return hash_obj.hexdigest()[:length]

