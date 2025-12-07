from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from .routers.signup import router as signup_router
from .routers.login import router as login_router
from .routers.password_reset import router as password_reset_router
from .db import engine
from .models import Base

# Create tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FYP Auth API",
    description="Complete Authentication System with Password Reset",
    version="1.0.0"
)

# CORS for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(signup_router)
app.include_router(login_router)
app.include_router(password_reset_router)

@app.get("/")
def root():
    return {
        "message": "FYP Auth API is running",
        "status": "active",
        "version": "1.0.0",
        "endpoints": {
            "signup": "/signup",
            "login": "/login",
            "forgot_password": "/password/forgot",
            "verify_reset": "/password/verify-token",
            "reset_password": "/password/reset"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
