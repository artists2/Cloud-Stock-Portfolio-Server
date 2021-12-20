from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    user_id: str
    password: str
    name: str
    email: Optional[str] = None


class Login(BaseModel):
    user_id: str
    password: str


class Stock(BaseModel):
    stock_id: str
    stock_name: str


class Session(BaseModel):
    session_id: str
    user_id: str
    ip_address: str
    user_agent: str
    last_modified: int
