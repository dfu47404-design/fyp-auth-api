from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging

from ..db import get_db
from ..models import User
from ..auth import hash_password, verify_password
from ..email_service import email_service
from ..utils.tokens import generate_reset_token, generate_jwt_reset_token, verify_reset_token
from ..schemas import ResetPasswordRequest, ForgotPasswordRequest, VerifyResetTokenRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/password", tags=["password-reset"])

@router.get("/email-config")
async def check_email_config():
    """Check email service configuration (for debugging)"""
    config = email_service.get_configuration_status()
    return {
        "email_service": config,
        "message": "Email configuration status",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/forgot")
async def forgot_password(
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Step 1: Request password reset
    """
    logger.info(f"Password reset requested for email: {request.email}")
    
    # Find user by email
    user = db.query(User).filter(User.email == request.email.lower().strip()).first()
    
    if not user:
        # For security, don't reveal if user exists
        logger.warning(f"Password reset requested for non-existent email: {request.email}")
        return {
            "message": "If your email exists in our system, you will receive a password reset code.",
            "status": "success"
        }
    
    logger.info(f"User found: {user.id} - {user.email}")
    
    # Generate 6-digit reset token
    reset_token = generate_reset_token()
    logger.info(f"Generated reset token for {user.email}: {reset_token}")
    
    # Store token hash in database
    token_hash = hash_password(reset_token)
    user.reset_token = token_hash
    user.reset_token_expiry = datetime.utcnow() + timedelta(minutes=15)
    
    try:
        db.commit()
        logger.info(f"Reset token stored in database for user {user.id}")
    except Exception as e:
        db.rollback()
        logger.error(f"Database error storing reset token: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    
    # Send email in background
    background_tasks.add_task(
        email_service.send_password_reset_email,
        user.email,
        reset_token,
        f"{user.first_name} {user.last_name}".strip() or "User"
    )
    
    return {
        "message": "Password reset code sent to your email",
        "status": "success",
        "expires_in": "15 minutes",
        "email_sent_to": user.email,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/verify-token")
async def verify_reset_code(
    request: VerifyResetTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Step 2: Verify reset token
    """
    logger.info(f"Token verification requested for email: {request.email}")
    
    # Find user
    user = db.query(User).filter(User.email == request.email.lower().strip()).first()
    
    if not user:
        logger.error(f"Token verification failed: User not found for email {request.email}")
        raise HTTPException(status_code=400, detail="Invalid email address")
    
    if not user.reset_token:
        logger.error(f"Token verification failed: No reset token for user {user.id}")
        raise HTTPException(status_code=400, detail="No reset token found. Please request a new one.")
    
    # Check if token expired
    if not user.reset_token_expiry:
        logger.error(f"Token verification failed: No expiry time for user {user.id}")
        raise HTTPException(status_code=400, detail="Reset token has no expiry time")
    
    if user.reset_token_expiry < datetime.utcnow():
        logger.warning(f"Token expired for user {user.id}")
        # Clear expired token
        user.reset_token = None
        user.reset_token_expiry = None
        db.commit()
        raise HTTPException(status_code=400, detail="Reset code has expired. Please request a new one.")
    
    # Verify token
    if not verify_password(request.token, user.reset_token):
        logger.warning(f"Invalid token for user {user.id}. Provided: {request.token}")
        raise HTTPException(status_code=400, detail="Invalid reset code")
    
    logger.info(f"Token verified successfully for user {user.id}")
    
    # Generate JWT token for password reset
    jwt_token = generate_jwt_reset_token(user.id, user.email)
    
    # Clear the one-time code after successful verification
    user.reset_token = None
    user.reset_token_expiry = None
    
    try:
        db.commit()
        logger.info(f"Database updated after successful token verification for user {user.id}")
    except Exception as e:
        db.rollback()
        logger.error(f"Database error clearing token: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    
    return {
        "message": "Reset code verified successfully",
        "reset_token": jwt_token,
        "user_id": user.id,
        "email": user.email,
        "expires_in": "15 minutes",
        "status": "success",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/reset")
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Step 3: Reset password with JWT token
    """
    logger.info(f"Password reset requested for email: {request.email}")
    
    # Validate passwords match
    if request.new_password != request.confirm_password:
        logger.error("Password reset failed: Passwords do not match")
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    # Verify JWT token
    payload = verify_reset_token(request.token)
    if not payload:
        logger.error("Password reset failed: Invalid JWT token")
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    user_id = int(payload.get("sub"))
    email = payload.get("email")
    
    # Verify email matches
    if email.lower().strip() != request.email.lower().strip():
        logger.error(f"Email mismatch: Token email {email} != Request email {request.email}")
        raise HTTPException(status_code=400, detail="Email does not match reset token")
    
    # Find user
    user = db.query(User).filter(
        User.id == user_id,
        User.email == email.lower().strip()
    ).first()
    
    if not user:
        logger.error(f"Password reset failed: User not found - ID: {user_id}, Email: {email}")
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.info(f"Updating password for user {user.id}")
    
    # Update password
    user.password_hash = hash_password(request.new_password)
    
    # Clear any reset tokens
    user.reset_token = None
    user.reset_token_expiry = None
    
    try:
        db.commit()
        logger.info(f"Password updated successfully for user {user.id}")
    except Exception as e:
        db.rollback()
        logger.error(f"Database error updating password: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    
    return {
        "message": "Password reset successful. You can now login with your new password.",
        "status": "success",
        "user_id": user.id,
        "timestamp": datetime.utcnow().isoformat()
    }