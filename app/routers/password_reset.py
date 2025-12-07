# app/routers/password_reset.py - COMPATIBLE VERSION
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ..db import get_db
from ..models import User
from ..auth import hash_password, verify_password
from ..email_service import email_service
from ..utils.tokens import generate_reset_token, generate_jwt_reset_token, verify_reset_token
from ..schemas import ResetPasswordRequest, ForgotPasswordRequest, VerifyResetTokenRequest

router = APIRouter(prefix="/password", tags=["password-reset"])

@router.post("/forgot")
async def forgot_password(
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Step 1: Request password reset
    """
    
    # Find user by email
    user = db.query(User).filter(User.email == request.email.lower().strip()).first()
    
    if not user:
        # For security, don't reveal if user exists
        return {
            "message": "If your email exists in our system, you will receive a password reset code.",
            "status": "success"
        }
    
    # Generate 6-digit reset token
    reset_token = generate_reset_token()
    
    # Store token hash in database (not the plain token)
    token_hash = hash_password(reset_token)
    user.reset_token = token_hash
    user.reset_token_expiry = datetime.utcnow() + timedelta(minutes=15)
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")
    
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
    """
    
    # Find user
    user = db.query(User).filter(User.email == request.email.lower().strip()).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email address")
    
    if not user.reset_token:
        raise HTTPException(status_code=400, detail="No reset token found. Please request a new one.")
    
    # Check if token expired
    if not user.reset_token_expiry:
        raise HTTPException(status_code=400, detail="Reset token has no expiry time")
    
    if user.reset_token_expiry < datetime.utcnow():
        # Clear expired token
        user.reset_token = None
        user.reset_token_expiry = None
        db.commit()
        raise HTTPException(status_code=400, detail="Reset code has expired. Please request a new one.")
    
    # Verify token
    if not verify_password(request.token, user.reset_token):
        raise HTTPException(status_code=400, detail="Invalid reset code")
    
    # Generate JWT token for password reset
    jwt_token = generate_jwt_reset_token(user.id, user.email)
    
    # Clear the one-time code after successful verification
    user.reset_token = None
    user.reset_token_expiry = None
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")
    
    return {
        "message": "Reset code verified successfully",
        "reset_token": jwt_token,  # JWT token for next step
        "user_id": user.id,
        "expires_in": "15 minutes",
        "status": "success"
    }

@router.post("/reset")
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Step 3: Reset password with JWT token
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
    
    # Verify email matches
    if email.lower().strip() != request.email.lower().strip():
        raise HTTPException(status_code=400, detail="Email does not match reset token")
    
    # Find user
    user = db.query(User).filter(
        User.id == user_id,
        User.email == email.lower().strip()
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update password
    user.password_hash = hash_password(request.new_password)
    
    # Clear any reset tokens
    user.reset_token = None
    user.reset_token_expiry = None
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")
    
    return {
        "message": "Password reset successful. You can now login with your new password.",
        "status": "success"
    }