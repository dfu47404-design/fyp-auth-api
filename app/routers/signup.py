# app/routers/signup.py - PostgreSQL version
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..schemas import SignupRequest, SignupInfoUpdate
from ..auth import hash_password
from ..models import User
from ..db import get_db

router = APIRouter(prefix="/signup", tags=["signup"])

@router.post("")
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # username = FirstName + LastName
    username = f"{payload.first_name}{payload.last_name}".strip()

    # Create new user
    new_user = User(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        username=username,
        password_hash=hash_password(payload.password)
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError as e:
        db.rollback()
        if "email" in str(e):
            raise HTTPException(status_code=400, detail="Email already exists")
        elif "username" in str(e):
            raise HTTPException(status_code=400, detail="Username already exists")
        else:
            raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Signup successful", "user_id": new_user.id}

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
    
    try:
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Info updated"}