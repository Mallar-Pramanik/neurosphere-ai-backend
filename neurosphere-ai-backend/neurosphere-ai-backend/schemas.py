"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

# ===== USER SCHEMAS =====

class UserCreate(BaseModel):
    """User registration schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    """User response schema"""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"

# ===== AI TASK SCHEMAS =====

class TaskType(str, Enum):
    """Task type enumeration"""
    CHAT = "chat"
    CONTENT_GENERATION = "content_generation"
    ANALYSIS = "analysis"
    FILE_PROCESSING = "file_processing"
    NLP_ANALYSIS = "nlp_analysis"

class ChatMessage(BaseModel):
    """Chat message schema"""
    content: str = Field(..., min_length=1, max_length=4096)
    conversation_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    """Chat response schema"""
    response: str
    conversation_id: Optional[str]
    task_id: int
    timestamp: datetime = Field(default_factory=datetime.now)

class AITaskRequest(BaseModel):
    """Generic AI task request"""
    task_type: str
    input_data: Dict[str, Any]
    parameters: Optional[Dict[str, Any]] = None

class AITaskResponse(BaseModel):
    """Generic AI task response"""
    task_id: int
    task_type: str
    status: str
    result: Dict[str, Any]
    created_at: datetime

# ===== CONTENT GENERATION SCHEMAS =====

class ContentType(str, Enum):
    """Content type enumeration"""
    BLOG_POST = "blog_post"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"
    TECHNICAL = "technical"
    CREATIVE = "creative"
    SUMMARY = "summary"

class Tone(str, Enum):
    """Tone enumeration"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FORMAL = "formal"
    FRIENDLY = "friendly"
    TECHNICAL = "technical"
    CREATIVE = "creative"

class ContentGenerationRequest(BaseModel):
    """Content generation request"""
    prompt: str = Field(..., min_length=10, max_length=2048)
    content_type: ContentType = ContentType.BLOG_POST
    tone: Tone = Tone.PROFESSIONAL
    max_tokens: int = Field(default=1024, le=4096)
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)

class ContentGenerationResponse(BaseModel):
    """Content generation response"""
    content: str
    content_type: str
    task_id: int
    tokens_used: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# ===== GOOGLE API SCHEMAS =====

class EmailRequest(BaseModel):
    """Email request schema"""
    to: str = Field(...)
    subject: str = Field(..., max_length=256)
    body: str = Field(..., min_length=1)
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    attachments: Optional[List[str]] = None

class EmailResponse(BaseModel):
    """Email response schema"""
    message_id: str
    status: str
    timestamp: datetime = Field(default_factory=datetime.now)

class GmailMessage(BaseModel):
    """Gmail message schema"""
    id: str
    from_email: str
    subject: str
    body: Optional[str]
    date: datetime
    has_attachments: bool

class DriveFile(BaseModel):
    """Google Drive file schema"""
    id: str
    name: str
    mime_type: str
    size: int
    created_time: datetime
    modified_time: datetime
    owner: str

class NLPAnalysisResult(BaseModel):
    """NLP analysis result schema"""
    text: str
    sentiment: Dict[str, float]
    entities: List[Dict[str, Any]]
    language: str
    task_id: int

# ===== FILE PROCESSING SCHEMAS =====

class ProcessType(str, Enum):
    """File process type"""
    ANALYZE = "analyze"
    EXTRACT = "extract"
    SUMMARIZE = "summarize"
    CLASSIFY = "classify"

class FileProcessRequest(BaseModel):
    """File process request"""
    process_type: ProcessType = ProcessType.ANALYZE
    parameters: Optional[Dict[str, Any]] = None

class FileProcessResponse(BaseModel):
    """File process response"""
    filename: str
    process_type: str
    result: Dict[str, Any]
    file_id: int
    timestamp: datetime = Field(default_factory=datetime.now)

class ProcessedFileResponse(BaseModel):
    """Processed file response"""
    id: int
    filename: str
    file_type: str
    process_type: str
    result: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# ===== TASK MANAGEMENT SCHEMAS =====

class TaskStatus(str, Enum):
    """Task status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskResponse(BaseModel):
    """Task response schema"""
    id: int
    user_id: int
    task_type: str
    status: str
    input_data: str
    output_data: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TaskListResponse(BaseModel):
    """Task list response"""
    tasks: List[TaskResponse]
    total: int
    page: int
    per_page: int

# ===== CONVERSATION SCHEMAS =====

class ConversationMessage(BaseModel):
    """Message in conversation"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

class ConversationCreate(BaseModel):
    """Create conversation"""
    title: Optional[str] = None
    initial_message: Optional[str] = None

class ConversationResponse(BaseModel):
    """Conversation response"""
    id: str
    user_id: int
    title: str
    messages: List[ConversationMessage]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ===== ERROR SCHEMAS =====

class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class ValidationErrorResponse(BaseModel):
    """Validation error response"""
    detail: List[Dict[str, Any]]
    timestamp: datetime = Field(default_factory=datetime.now)

# ===== BATCH OPERATION SCHEMAS =====

class BatchRequest(BaseModel):
    """Batch operation request"""
    operations: List[Dict[str, Any]]
    parallel: bool = False

class BatchResponse(BaseModel):
    """Batch operation response"""
    batch_id: str
    total_operations: int
    successful: int
    failed: int
    results: List[Dict[str, Any]]
    timestamp: datetime = Field(default_factory=datetime.now)

# ===== ANALYTICS SCHEMAS =====

class UsageStats(BaseModel):
    """User usage statistics"""
    total_tasks: int
    tasks_by_type: Dict[str, int]
    api_calls: int
    storage_used: int
    credits_used: float

class UserAnalytics(BaseModel):
    """User analytics"""
    user_id: int
    email: str
    stats: UsageStats
    last_active: datetime
    premium: bool
