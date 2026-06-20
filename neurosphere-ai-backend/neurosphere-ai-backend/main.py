
"""
NeuroSphere AI Backend - FastAPI Application
Integrated with Odysseus AI Model and Google APIs
"""

from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager
from typing import List, Optional

from config import settings
from database import init_db, get_db
from schemas import (
    AITaskRequest,
    AITaskResponse,
    ChatMessage,
    ChatResponse,
    EmailRequest,
    FileProcessRequest,
    FileProcessResponse,
    ContentGenerationRequest,
    ContentGenerationResponse,
    UserCreate,
    UserResponse,
    LoginRequest,
    TokenResponse
)
from services.odysseus_service import OdysseusAIService
from services.google_service import GoogleAPIService
from services.database_service import DatabaseService
from services.auth_service import AuthService
from models import User, Task, ProcessedFile
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
odysseus_service = OdysseusAIService()
google_service = GoogleAPIService()
auth_service = AuthService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 NeuroSphere AI Backend Starting...")
    
    # Initialize database
    init_db()
    logger.info("✅ Database initialized")
    
    # Load Odysseus AI Model
    await odysseus_service.initialize()
    logger.info("✅ Odysseus AI Model loaded")
    
    # Initialize Google APIs
    google_service.initialize()
    logger.info("✅ Google APIs initialized")
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down NeuroSphere AI Backend...")
    await odysseus_service.cleanup()

# Create FastAPI app
app = FastAPI(
    title="NeuroSphere AI Backend",
    description="Premium AI-powered backend with Odysseus AI and Google APIs",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "NeuroSphere AI Backend is running"
    }

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== HEALTH CHECK ENDPOINTS =====

@app.get("/health", tags=["Health"])
async def health_check():
    """Check API health status"""
    return {
        "status": "healthy",
        "service": "NeuroSphere AI Backend",
        "version": "1.0.0"
    }

@app.get("/api/v1/status", tags=["Health"])
async def api_status():
    """Check API and service status"""
    return {
        "api": "operational",
        "odysseus_ai": True,
        "google_apis": True,
        "database": "connected"
    }

# ===== AUTHENTICATION ENDPOINTS =====

@app.post("/api/v1/auth/register", response_model=UserResponse, tags=["Authentication"])
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        user = auth_service.register_user(db, user_data)
        logger.info(f"New user registered: {user.email}")
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.post("/api/v1/auth/login", response_model=TokenResponse, tags=["Authentication"])
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Login user and get JWT token"""
    try:
        token = auth_service.login_user(db, credentials.email, credentials.password)
        logger.info(f"User logged in: {credentials.email}")
        return {"access_token": token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

# ===== AI TASK ENDPOINTS =====

@app.post("/api/v1/ai/chat", response_model=ChatResponse, tags=["AI Tasks"])
async def chat_with_ai(
    message: ChatMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Chat with Odysseus AI model"""
    try:
        logger.info(f"Chat request from {current_user.email}: {message.content[:50]}...")
        
        # Process with Odysseus AI
        response = await odysseus_service.chat(
            message.content,
            conversation_id=message.conversation_id,
            context=message.context
        )
        
        # Save to database
        task = DatabaseService.create_task(
            db,
            user_id=current_user.id,
            task_type="chat",
            input_data=message.content,
            output_data=response
        )
        
        return ChatResponse(
            response=response,
            conversation_id=message.conversation_id,
            task_id=task.id
        )
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="AI processing failed")

@app.post("/api/v1/ai/generate-content", response_model=ContentGenerationResponse, tags=["AI Tasks"])
async def generate_content(
    request: ContentGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Generate content using Odysseus AI"""
    try:
        logger.info(f"Content generation request from {current_user.email}")
        
        # Generate content with Odysseus AI
        generated_content = await odysseus_service.generate_content(
            prompt=request.prompt,
            content_type=request.content_type,
            tone=request.tone,
            max_tokens=request.max_tokens
        )
        
        # Save to database
        task = DatabaseService.create_task(
            db,
            user_id=current_user.id,
            task_type="content_generation",
            input_data=request.prompt,
            output_data=generated_content
        )
        
        return ContentGenerationResponse(
            content=generated_content,
            content_type=request.content_type,
            task_id=task.id
        )
    except Exception as e:
        logger.error(f"Content generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Content generation failed")

@app.post("/api/v1/ai/analyze", response_model=dict, tags=["AI Tasks"])
async def analyze_data(
    request: AITaskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Analyze data using Odysseus AI"""
    try:
        logger.info(f"Analysis request from {current_user.email}")
        
        # Analyze with Odysseus AI
        analysis = await odysseus_service.analyze(
            data=request.input_data,
            analysis_type=request.task_type
        )
        
        # Save to database
        task = DatabaseService.create_task(
            db,
            user_id=current_user.id,
            task_type="analysis",
            input_data=str(request.input_data),
            output_data=str(analysis)
        )
        
        return {
            "analysis": analysis,
            "task_id": task.id,
            "status": "completed"
        }
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Analysis failed")

# ===== GOOGLE API ENDPOINTS =====

@app.get("/api/v1/google/emails", tags=["Google APIs"])
async def get_emails(
    max_results: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get emails from Gmail"""
    try:
        logger.info(f"Email fetch request from {current_user.email}")
        
        emails = google_service.get_emails(
            user_id=current_user.id,
            max_results=max_results
        )
        
        return {"emails": emails, "total": len(emails)}
    except Exception as e:
        logger.error(f"Gmail error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch emails")

@app.post("/api/v1/google/send-email", tags=["Google APIs"])
async def send_email(
    email_request: EmailRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Send email via Gmail"""
    try:
        logger.info(f"Email send request from {current_user.email}")
        
        result = google_service.send_email(
            to=email_request.to,
            subject=email_request.subject,
            body=email_request.body,
            user_id=current_user.id
        )
        
        return {"status": "sent", "message_id": result}
    except Exception as e:
        logger.error(f"Email send error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send email")

@app.get("/api/v1/google/drive-files", tags=["Google APIs"])
async def get_drive_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get files from Google Drive"""
    try:
        logger.info(f"Drive files request from {current_user.email}")
        
        files = google_service.get_drive_files(user_id=current_user.id)
        
        return {"files": files, "total": len(files)}
    except Exception as e:
        logger.error(f"Drive error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch drive files")

@app.post("/api/v1/google/analyze-nlp", tags=["Google APIs"])
async def analyze_with_nlp(
    text: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Analyze text using Google Cloud NLP"""
    try:
        logger.info(f"NLP analysis request from {current_user.email}")
        
        analysis = google_service.analyze_sentiment(text=text)
        
        # Save analysis to database
        task = DatabaseService.create_task(
            db,
            user_id=current_user.id,
            task_type="nlp_analysis",
            input_data=text,
            output_data=str(analysis)
        )
        
        return {
            "analysis": analysis,
            "task_id": task.id
        }
    except Exception as e:
        logger.error(f"NLP analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="NLP analysis failed")

# ===== FILE PROCESSING ENDPOINTS =====

@app.post("/api/v1/files/process", response_model=FileProcessResponse, tags=["File Processing"])
async def process_file(
    file: UploadFile = File(...),
    process_type: str = "analyze",
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Process uploaded file with AI"""
    try:
        logger.info(f"File processing from {current_user.email}: {file.filename}")
        
        # Read file content
        content = await file.read()
        
        # Process with Odysseus AI
        if process_type == "extract":
            result = await odysseus_service.extract_from_file(content, file.filename)
        elif process_type == "summarize":
            result = await odysseus_service.summarize_file(content, file.filename)
        else:
            result = await odysseus_service.analyze_file(content, file.filename)
        
        # Save to database
        processed_file = DatabaseService.create_processed_file(
            db,
            user_id=current_user.id,
            filename=file.filename,
            file_type=file.content_type,
            process_type=process_type,
            result=str(result)
        )
        
        return FileProcessResponse(
            filename=file.filename,
            process_type=process_type,
            result=result,
            file_id=processed_file.id
        )
    except Exception as e:
        logger.error(f"File processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="File processing failed")

# ===== TASK MANAGEMENT ENDPOINTS =====

@app.get("/api/v1/tasks", tags=["Tasks"])
async def get_user_tasks(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get user's tasks"""
    try:
        tasks = DatabaseService.get_user_tasks(db, current_user.id, skip, limit)
        return {
            "tasks": tasks,
            "total": len(tasks)
        }
    except Exception as e:
        logger.error(f"Error fetching tasks: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch tasks")

@app.get("/api/v1/tasks/{task_id}", tags=["Tasks"])
async def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get specific task details"""
    try:
        task = DatabaseService.get_task_by_id(db, task_id, current_user.id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching task: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch task")

@app.delete("/api/v1/tasks/{task_id}", tags=["Tasks"])
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Delete a task"""
    try:
        success = DatabaseService.delete_task(db, task_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete task")

# ===== ERROR HANDLERS =====

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# ===== STARTUP/SHUTDOWN EVENTS =====

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("Application shutdown")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
