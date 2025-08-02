from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Import routes
from app.routes import health, language, entity


load_dotenv()


api = FastAPI(
    title="SmartScanAI Backend",
    description="Hindi/English NER service for business cards",
    version="1.0.0"
)


api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
api.include_router(health.router)
api.include_router(language.router)
api.include_router(entity.router)



# Run the server (like app.listen())
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 Starting server on {host}:{port}")
    uvicorn.run(
        "app.main:api",
        host=host,
        port=port,
        reload=True,  # Auto-restart on file changes (like nodemon)
        log_level="info"
    )