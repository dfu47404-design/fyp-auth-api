from pydantic import BaseModel, EmailStr, Field, validator

# -------------------------------
# Signup & Login Schemas
# -------------------------------

class SignupRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    confirm_password: str = Field(..., min_length=6, max_length=100)

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v

    @validator("email")
    def normalize_email(cls, v):
        return v.lower().strip()

class SignupInfoUpdate(BaseModel):
    user_id: int
    age: int = Field(..., ge=13, le=80)
    weight: float = Field(..., ge=30, le=150)
    foot_size: float = Field(..., ge=30, le=55)
    purpose: str = Field(..., min_length=3, max_length=50)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)

class LoginResponse(BaseModel):
    token: str
    user_id: int

# -------------------------------
# Forgot Password Flow Schemas
# -------------------------------

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

    @validator("email")
    def normalize_email(cls, v):
        return v.lower().strip()

class VerifyResetTokenRequest(BaseModel):
    email: EmailStr
    token: str = Field(..., min_length=6, max_length=6, description="6-digit reset code")

    @validator("email")
    def normalize_email(cls, v):
        return v.lower().strip()

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    token: str = Field(..., description="JWT reset token from verify step")
    new_password: str = Field(..., min_length=6, max_length=100)
    confirm_password: str = Field(..., min_length=6, max_length=100)

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("Passwords do not match")
        return v

    @validator("email")
    def normalize_email(cls, v):
        return v.lower().strip()
