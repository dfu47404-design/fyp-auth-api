from fastapi import FastAPI
from .routers.signup import router as signup_router
from .routers.login import router as login_router
from .db import engine
from .models import Base

# Create tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(title='FYP Auth API')

app.include_router(signup_router)
app.include_router(login_router)

@app.get('/')
def root():
    return {'message': 'FYP Auth API is running'}
