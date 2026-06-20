/**
 * API Configuration
 * Change the API_URL to match your backend server
 */

// Backend API URL
const API_BASE = "https://neurosphere-ai-backend-2.onrender.com";
const API_URL = `${API_BASE}/api/v1`;

// API Endpoints
const API_ENDPOINTS = {
    // Authentication
    AUTH_REGISTER: `${API_URL}/auth/register`,
    AUTH_LOGIN: `${API_URL}/auth/login`,
    
    // AI Tasks
    AI_CHAT: `${API_URL}/ai/chat`,
    AI_GENERATE_CONTENT: `${API_URL}/ai/generate-content`,
    AI_ANALYZE: `${API_URL}/ai/analyze`,
    
    // File Processing
    FILES_PROCESS: `${API_URL}/files/process`,
    
    // Google APIs
    GOOGLE_EMAILS: `${API_URL}/google/emails`,
    GOOGLE_SEND_EMAIL: `${API_URL}/google/send-email`,
    GOOGLE_DRIVE_FILES: `${API_URL}/google/drive-files`,
    GOOGLE_NLP_ANALYZE: `${API_URL}/google/analyze-nlp`,
    
    // Task Management
    TASKS_LIST: `${API_URL}/tasks`,
    TASKS_GET: (id) => `${API_URL}/tasks/${id}`,
    TASKS_DELETE: (id) => `${API_URL}/tasks/${id}`,
    
    // Health
    HEALTH: `${API_BASE}/health`,
    STATUS: `${API_URL}/status`,
};

// Local Storage Keys
const STORAGE_KEYS = {
    AUTH_TOKEN: 'authToken',
    USER_DATA: 'userData',
    CONVERSATION_ID: 'conversationId',
    THEME: 'theme',
};

// Notification Duration (ms)
const NOTIFICATION_DURATION = 3000;

// Page Configuration
const PAGE_CONFIG = {
    DEMO_MODE: false, // Set to true for demo without backend
    DEBUG: true, // Set to true for detailed logging
};

// Content Generation Options
const CONTENT_OPTIONS = {
    types: [
        { value: 'blog_post', label: 'Blog Post' },
        { value: 'social_media', label: 'Social Media' },
        { value: 'email', label: 'Email' },
        { value: 'technical', label: 'Technical Writing' },
        { value: 'creative', label: 'Creative Content' },
        { value: 'summary', label: 'Summary' },
    ],
    tones: [
        { value: 'professional', label: 'Professional' },
        { value: 'casual', label: 'Casual' },
        { value: 'formal', label: 'Formal' },
        { value: 'friendly', label: 'Friendly' },
        { value: 'technical', label: 'Technical' },
        { value: 'creative', label: 'Creative' },
    ],
};

// File Processing Options
const FILE_OPTIONS = {
    types: [
        { value: 'analyze', label: 'Analyze' },
        { value: 'extract', label: 'Extract' },
        { value: 'summarize', label: 'Summarize' },
        { value: 'classify', label: 'Classify' },
    ],
    maxSize: 10 * 1024 * 1024, // 10MB
    allowed: ['.txt', '.pdf', '.json', '.csv', '.docx', '.md'],
};

// Logging Utility
const Logger = {
    log: (message, data = null) => {
        if (PAGE_CONFIG.DEBUG) {
            console.log(`[NeuroSphere] ${message}`, data || '');
        }
    },
    error: (message, error = null) => {
        console.error(`[NeuroSphere Error] ${message}`, error || '');
    },
    warn: (message, data = null) => {
        console.warn(`[NeuroSphere Warning] ${message}`, data || '');
    },
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        API_URL,
        API_ENDPOINTS,
        STORAGE_KEYS,
        PAGE_CONFIG,
        Logger,
    };
}