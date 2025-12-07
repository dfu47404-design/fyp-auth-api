# app/routers/signup.py - FIXED FOR PASSWORD RESET
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from ..schemas import SignupRequest, SignupInfoUpdate
from ..auth import hash_password
from ..models import User
from ..db import get_db

router = APIRouter(prefix="/signup", tags=["signup"])

@router.post("")
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Create username from FirstName + LastName
    username = f"{payload.first_name}{payload.last_name}".strip().lower()

    # Create new user with password reset fields
    new_user = User(
        first_name=payload.first_name.strip(),
        last_name=payload.last_name.strip(),
        email=payload.email.lower().strip(),
        username=username,
        password_hash=hash_password(payload.password),
        # Password reset fields (initialize to None)
        reset_token=None,
        reset_token_expiry=None,
        is_active=True,
        created_at=datetime.utcnow(),
        # Other fields (can be updated later)
        age=None,
        weight=None,
        foot_size=None,
        purpose=None
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError as e:
        db.rollback()
        if "email" in str(e).lower():
            raise HTTPException(status_code=400, detail="Email already exists")
        elif "username" in str(e).lower():
            raise HTTPException(status_code=400, detail="Username already exists")
        else:
            raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "message": "Signup successful", 
        "user_id": new_user.id,
        "username": username,
        "email": new_user.email
    }

@router.put("/info")
def update_info(payload: SignupInfoUpdate, db: Session = Depends(get_db)):
    # Find user
    user = db.query(User).filter(User.id == payload.user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user info
    user.age = payload.age
    user.weight = payload.weight
    user.foot_size = payload.foot_size
    user.purpose = payload.purpose
    user.updated_at = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Info updated successfully"}