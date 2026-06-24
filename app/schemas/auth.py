from pydantic import BaseModel, EmailStr
from fastapi.security import OAuth2PasswordRequestForm

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"