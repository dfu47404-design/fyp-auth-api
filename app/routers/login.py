# app/routers/login.py - PostgreSQL version
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..schemas import LoginRequest, LoginResponse
from ..auth import verify_password, create_token
from ..models import User
from ..db import get_db

router = APIRouter(prefix="/login", tags=["login"])

@router.post("", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    # Find user by username
    user = db.query(User).filter(User.username == payload.username).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create token
    token = create_token(user.id)
    
    return LoginResponse(token=token, user_id=user.id)