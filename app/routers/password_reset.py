# app/routers/password_reset.py
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timedelta

from ..db import get_db
from ..models import User
from ..auth import hash_password, verify_password
from ..email_service import email_service
from ..utils.tokens import generate_reset_token, generate_jwt_reset_token, verify_reset_token

router = APIRouter(prefix="/password", tags=["password-reset"])

# ============ SCHEMAS ============

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class VerifyResetTokenRequest(BaseModel):
    email: EmailStr
    token: str = Field(min_length=6, max_length=6)

class ResetPasswordRequest(BaseModel):
    token: str  # JWT token from verify step
    new_password: str = Field(min_length=6)
    confirm_password: str = Field(min_length=6)
    
    def validate_passwords(self):
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")

# ============ ENDPOINTS ============

@router.post("/forgot")
async def forgot_password(
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Step 1: Request password reset
    - User provides email
    - Generate reset token
    - Send token via email
    - Store token hash in database
    """
    
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        # For security, don't reveal if user exists
        return {
            "message": "If your email exists in our system, you will receive a password reset code.",
            "status": "success"
        }
    
    # Generate reset token (6-digit code for mobile)
    reset_token = generate_reset_token()
    
    # Generate JWT token for verification
    jwt_token = generate_jwt_reset_token(user.id, user.email)
    
    # Store token hash in database (not the plain token)
    token_hash = hash_password(reset_token)
    user.reset_token = token_hash
    user.reset_token_expiry = datetime.utcnow() + timedelta(minutes=15)
    db.commit()
    
    # Send email in background (non-blocking)
    background_tasks.add_task(
        email_service.send_password_reset_email,
        user.email,
        reset_token,
        f"{user.first_name} {user.last_name}"
    )
    
    return {
        "message": "Password reset code sent to your email",
        "status": "success",
        "expires_in": "15 minutes"
    }

@router.post("/verify-token")
async def verify_reset_code(
    request: VerifyResetTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Step 2: Verify reset token
    - User provides email and 6-digit code
    - Verify code matches and is not expired
    - Return JWT token for password reset
    """
    
    # Find user
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user or not user.reset_token:
        raise HTTPException(status_code=400, detail="Invalid or expired reset code")
    
    # Check if token expired
    if not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Reset code has expired")
    
    # Verify token
    if not verify_password(request.token, user.reset_token):
        raise HTTPException(status_code=400, detail="Invalid reset code")
    
    # Generate JWT token for password reset
    jwt_token = generate_jwt_reset_token(user.id, user.email)
    
    # Clear the one-time code after successful verification
    user.reset_token = None
    user.reset_token_expiry = None
    db.commit()
    
    return {
        "message": "Reset code verified successfully",
        "reset_token": jwt_token,  # JWT token for next step
        "user_id": user.id,
        "status": "success"
    }

@router.post("/reset")
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Step 3: Reset password with JWT token
    - User provides JWT token and new password
    - Verify JWT token
    - Update password
    """
    
    # Validate passwords match
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    # Verify JWT token
    payload = verify_reset_token(request.token)
    if not payload:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    user_id = int(payload.get("sub"))
    email = payload.get("email")
    
    # Find user
    user = db.query(User).filter(
        User.id == user_id,
        User.email == email,
        User.is_active == True
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update password
    user.password_hash = hash_password(request.new_password)
    
    # Clear any reset tokens
    user.reset_token = None
    user.reset_token_expiry = None
    
    db.commit()
    
    return {
        "message": "Password reset successful. You can now login with your new password.",
        "status": "success"
    }