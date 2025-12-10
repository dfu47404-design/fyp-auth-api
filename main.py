# main.py - UPDATED
import os
import sys

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print(f"📁 Current directory: {current_dir}")
print(f"🐍 Python path: {sys.path}")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime

# Create app first
app = FastAPI(
    title="Sure Step Auth API",
    description="Authentication System for Sure Step App",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Try to import routers with better error handling
try:
    # Try relative import first
    try:
        from app.routers import signup, login, password_reset
    except ImportError:
        # Try absolute import
        from app.routers import signup, login, password_reset
    
    # Include routers
    app.include_router(signup.router, prefix="/api")
    app.include_router(login.router, prefix="/api")
    app.include_router(password_reset.router, prefix="/api")
    
    print("✅ All routers imported successfully")
    
except ImportError as e:
    print(f"❌ Router import error: {e}")
    
    # Create minimal test endpoints
    from fastapi import APIRouter
    
    test_router = APIRouter()
    
    @test_router.get("/test")
    async def test():
        return {"message": "API is working", "status": "test_mode"}
    
    @test_router.post("/signup")
    async def test_signup():
        return {"message": "Test signup - routers not loaded", "status": "test"}
    
    @test_router.post("/login")
    async def test_login():
        return {"message": "Test login - routers not loaded", "status": "test"}
    
    app.include_router(test_router, prefix="/api")
    print("⚠️  Using test router mode")

@app.get("/")
async def root():
    return {
        "message": "Sure Step Auth API is running",
        "status": "active",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "signup": "POST /api/signup",
            "login": "POST /api/login",
            "forgot_password": "POST /api/password/forgot",
            "verify_reset": "POST /api/password/verify-token",
            "reset_password": "POST /api/password/reset",
            "health_check": "GET /health",
            "docs": "GET /docs",
            "redoc": "GET /redoc"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Sure Step Auth API",
        "version": "1.0.0"
    }

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "error": str(exc),
            "path": request.url.path
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "=" * 50)
    print("🚀 Starting Sure Step Auth API")
    print("🌐 Local: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("=" * 50 + "\n")
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )