# neurosphere-ai-backend
Ai landing page  website backend
# NeuroSphere AI Backend 🚀

Premium FastAPI backend with Odysseus AI Model and Google APIs integration.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Backend](#running-the-backend)
- [API Endpoints](#api-endpoints)
- [Database Models](#database-models)
- [Authentication](#authentication)
- [Error Handling](#error-handling)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## ✨ Features

### 🤖 AI Capabilities
- **Odysseus AI Integration** - Local LLM model support
- **Chat System** - Multi-turn conversations with context
- **Content Generation** - Blog posts, emails, social media, etc.
- **Data Analysis** - Advanced text and data analysis
- **File Processing** - Extract, summarize, analyze uploaded files

### 📊 Google APIs Integration
- **Gmail API** - Read and send emails
- **Google Drive** - List and manage files
- **Cloud NLP** - Sentiment analysis, entity recognition, syntax analysis

### 🔐 Security & Authentication
- **JWT Authentication** - Secure token-based auth
- **Password Hashing** - Bcrypt encryption
- **Rate Limiting** - Prevent abuse
- **CORS Support** - Cross-origin requests

### 💾 Database
- **SQLAlchemy ORM** - Multi-database support
- **SQLite** (default) / **PostgreSQL** / **MySQL**
- **Audit Logging** - Track user actions
- **Usage Statistics** - Monitor API usage

### 📁 Additional Features
- **File Upload** - Process various file types
- **Conversation History** - Multi-turn chat persistence
- **Task Management** - Track AI processing tasks
- **User Management** - Registration and profile management
- **Error Handling** - Comprehensive error responses

## 🏗️ Architecture

```
neurosphere-ai-backend/
├── main.py                 # FastAPI application
├── config.py              # Configuration settings
├── database.py            # Database setup
├── models.py              # SQLAlchemy models
├── schemas.py             # Pydantic schemas
├── services/
│   ├── __init__.py
│   ├── odysseus_service.py    # AI integration
│   ├── google_service.py      # Google APIs
│   ├── database_service.py    # DB operations
│   └── auth_service.py        # Authentication
├── credentials/           # Google credentials (git-ignored)
├── logs/                  # Application logs
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
└── README.md             # This file
```

## 📦 Prerequisites

- **Python 3.9+**
- **CUDA 11.8+** (for GPU acceleration, optional)
- **Git**
- **PostgreSQL** (optional, for production)

## 🔧 Installation

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/neurosphere-ai-backend.git
cd neurosphere-ai-backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
```bash
cp .env.example .env
# Edit .env with your settings
```

### 5. Configure Odysseus AI Model

Option A: Download from HuggingFace
```bash
python -c "from transformers import AutoTokenizer, AutoModelForCausalLM; \
AutoTokenizer.from_pretrained('meta-llama/Llama-2-7b-chat'); \
AutoModelForCausalLM.from_pretrained('meta-llama/Llama-2-7b-chat')"
```

Option B: Use Local Model
```bash
# Place your local model at ./models/odysseus_ai
mkdir -p models
# Copy your model files here
```

### 6. Setup Google APIs (Optional)

1. Create Google Cloud Project
2. Enable APIs: Gmail, Drive, Cloud NLP
3. Create Service Account credentials
4. Download JSON key and place at `./credentials/google-credentials.json`

```bash
mkdir -p credentials
# Place your google-credentials.json here
```

## ⚙️ Configuration

### Environment Variables (.env)

```env
# API Settings
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Database
DATABASE_URL=sqlite:///./neurosphere_ai.db

# JWT
SECRET_KEY=your-super-secret-key-minimum-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Odysseus AI
ODYSSEUS_MODEL_PATH=./models/odysseus_ai
ODYSSEUS_MAX_TOKENS=2048
ODYSSEUS_TEMPERATURE=0.7

# Google APIs
GOOGLE_CREDENTIALS_PATH=./credentials/google-credentials.json
GOOGLE_PROJECT_ID=your-project-id

# Feature Flags
ENABLE_ODYSSEUS_AI=True
ENABLE_GOOGLE_APIS=True
ENABLE_FILE_PROCESSING=True
```

### Database Configuration

**SQLite (Default)**
```
DATABASE_URL=sqlite:///./neurosphere_ai.db
```

**PostgreSQL (Production)**
```
DATABASE_URL=postgresql://user:password@localhost:5432/neurosphere_ai
```

**MySQL**
```
DATABASE_URL=mysql://user:password@localhost:3306/neurosphere_ai
```

## 🚀 Running the Backend

### Development
```bash
python main.py
```

Or with hot-reload:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

### Access API
- **API Docs:** http://localhost:8000/docs (Swagger UI)
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

## 📡 API Endpoints

### Authentication
```
POST   /api/v1/auth/register       # Register user
POST   /api/v1/auth/login          # Login and get token
```

### AI Tasks
```
POST   /api/v1/ai/chat             # Chat with AI
POST   /api/v1/ai/generate-content # Generate content
POST   /api/v1/ai/analyze          # Analyze data
```

### Google APIs
```
GET    /api/v1/google/emails       # Get emails
POST   /api/v1/google/send-email   # Send email
GET    /api/v1/google/drive-files  # Get Drive files
POST   /api/v1/google/analyze-nlp  # NLP analysis
```

### File Processing
```
POST   /api/v1/files/process       # Process uploaded file
```

### Task Management
```
GET    /api/v1/tasks               # List user tasks
GET    /api/v1/tasks/{task_id}     # Get task details
DELETE /api/v1/tasks/{task_id}     # Delete task
```

### Health
```
GET    /health                     # API health
GET    /api/v1/status             # Service status
```

## 🗄️ Database Models

### Users
- id, email, username, password, full_name
- is_active, is_premium, created_at, last_login

### Tasks
- id, user_id, task_type, status
- input_data, output_data, tokens_used
- created_at, updated_at

### Conversations
- id, user_id, title, is_archived
- created_at, updated_at

### Messages
- id, conversation_id, role, content
- created_at

### ProcessedFiles
- id, user_id, filename, process_type
- result, storage_path, created_at

### AuditLogs
- id, user_id, action, resource_type
- changes, ip_address, created_at

## 🔐 Authentication

### JWT Tokens
1. User registers with email/password
2. User logs in, receives JWT token
3. Include token in Authorization header: `Bearer <token>`
4. Token expires after configured duration (default: 24 hours)

### Password Security
- Passwords hashed with bcrypt
- Minimum 8 characters required
- Never stored in plain text

## ⚠️ Error Handling

### Standard Error Responses
```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00"
}
```

### Common Errors
- 400: Bad Request (validation error)
- 401: Unauthorized (missing/invalid token)
- 403: Forbidden (insufficient permissions)
- 404: Not Found (resource not found)
- 500: Internal Server Error

## 🌐 Deployment

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Heroku Deployment
```bash
heroku create neurosphere-ai
git push heroku main
```

### AWS Deployment
```bash
# Using Elastic Beanstalk
eb create neurosphere-ai-env
eb deploy
```

## 🐛 Troubleshooting

### Model Loading Issues
```bash
# Clear cache and reload
rm -rf ~/.cache/huggingface
python main.py
```

### Database Connection Error
```bash
# Check SQLAlchemy connection string
python -c "from database import DatabaseManager; print(DatabaseManager.check_connection())"
```

### Google APIs Not Working
```bash
# Verify credentials file
ls -la ./credentials/google-credentials.json

# Check permissions
chmod 600 ./credentials/google-credentials.json
```

### Out of Memory (OOM)
```bash
# Reduce model size in config.py
ODYSSEUS_MAX_TOKENS=1024
ODYSSEUS_TEMPERATURE=0.5
```

### Port Already in Use
```bash
# Change port in .env
PORT=8001

# Or kill process
lsof -i :8000
kill -9 <PID>
```

## 📊 Usage Examples

### Chat with AI
```bash
curl -X POST "http://localhost:8000/api/v1/ai/chat" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello, how are you?"}'
```

### Generate Content
```bash
curl -X POST "http://localhost:8000/api/v1/ai/generate-content" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a blog post about AI",
    "content_type": "blog_post",
    "tone": "professional"
  }'
```

### Upload and Process File
```bash
curl -X POST "http://localhost:8000/api/v1/files/process" \
  -H "Authorization: Bearer <token>" \
  -F "file=@document.pdf" \
  -F "process_type=summarize"
```

## 📝 Logging

Logs are stored in `./logs/neurosphere_ai.log`

Configure logging level in `.env`:
```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🎯 Roadmap

- [ ] WebSocket support for real-time chat
- [ ] File storage on S3/GCS
- [ ] Advanced analytics dashboard
- [ ] Multi-user conversations
- [ ] Fine-tuning API
- [ ] Custom model support
- [ ] Streaming responses
- [ ] Caching layer (Redis)

## 📞 Support

For issues and questions:
1. Check troubleshooting section
2. Create GitHub issue
3. Email: support@neurosphere.ai

---

Made with ❤️ by NeuroSphere Team

