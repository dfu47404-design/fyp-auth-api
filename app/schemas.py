# app/schemas.py
from pydantic import BaseModel, EmailStr, Field, validator

class SignupRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)  # Increased limit
    confirm_password: str = Field(min_length=6, max_length=100)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class SignupInfoUpdate(BaseModel):
    user_id: int
    age: int
    weight: float
    foot_size: float
    purpose: str

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    user_id: int