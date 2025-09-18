from pydantic import BaseModel, EmailStr
from typing import Optional

class UserInDB(BaseModel):
    id: int
    email: EmailStr
    hashed_password: str
    class Config:
        from_attributes = True
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[EmailStr] = None