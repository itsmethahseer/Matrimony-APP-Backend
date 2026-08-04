from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.config import settings

# Import routers
from app.routers import auth, profile, explore, inbox, menu

# Import all models to ensure they are registered with Base for auto-creation
from app.models.user import User
from app.models.profile import Profile, Photo
from app.models.interaction import Interest, ProfileVisit, ContactView, Favourite, Note, Block, Pass
from app.models.chat import ChatMessage

from fastapi.staticfiles import StaticFiles
import os

# Auto-create tables on startup (Simple approach, Alembic can be configured for migrations later)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for Matrimony Application supporting matches, explore interactions, inbox chat/calls, and plan subscription.",
    version="1.0.0"
)

# Ensure static/uploads folder exists and mount static route
os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure CORS for React frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to the frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(auth.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(explore.router, prefix="/api")
app.include_router(inbox.router, prefix="/api")
app.include_router(menu.router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }
