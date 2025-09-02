"""
Simplified FastAPI Backend for Instagram API Testing
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from routes.instagram import router as instagram_router

# Load environment variables from current directory
load_dotenv()

app = FastAPI(title="AI Social Media Manager API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Instagram router
app.include_router(instagram_router)

@app.get("/")
async def root():
    return {"message": "AI Social Media Manager API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)