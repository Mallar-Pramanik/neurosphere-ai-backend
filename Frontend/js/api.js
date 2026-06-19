/**
 * API Service
 * Handles all HTTP requests to the backend
 */

class APIService {
    constructor() {
        this.baseURL = API_URL;
        this.token = this.getToken();
    }

    /**
     * Get stored auth token
     */
    getToken() {
        return localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
    }

    /**
     * Set auth token
     */
    setToken(token) {
        localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, token);
        this.token = token;
    }

    /**
     * Clear auth token
     */
    clearToken() {
        localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
        localStorage.removeItem(STORAGE_KEYS.USER_DATA);
        this.token = null;
    }

    /**
     * Get request headers with auth
     */
    getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json',
        };

        if (includeAuth && this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        return headers;
    }

    /**
     * Generic fetch method
     */
    async fetch(url, options = {}) {
        try {
            const config = {
                ...options,
                headers: this.getHeaders(options.includeAuth !== false),
            };

            Logger.log(`Fetching: ${url}`, options);

            const response = await fetch(url, config);

            // Handle unauthorized
            if (response.status === 401) {
                this.clearToken();
                window.location.href = '#home';
                showNotification('Session expired. Please login again.', 'error');
                throw new Error('Unauthorized');
            }

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'API Error');
            }

            Logger.log(`Response:`, data);
            return data;
        } catch (error) {
            Logger.error(`Fetch error: ${url}`, error);
            throw error;
        }
    }

    /**
     * GET request
     */
    async get(url, options = {}) {
        return this.fetch(url, {
            method: 'GET',
            ...options,
        });
    }

    /**
     * POST request
     */
    async post(url, data, options = {}) {
        return this.fetch(url, {
            method: 'POST',
            body: JSON.stringify(data),
            ...options,
        });
    }

    /**
     * PUT request
     */
    async put(url, data, options = {}) {
        return this.fetch(url, {
            method: 'PUT',
            body: JSON.stringify(data),
            ...options,
        });
    }

    /**
     * DELETE request
     */
    async delete(url, options = {}) {
        return this.fetch(url, {
            method: 'DELETE',
            ...options,
        });
    }

    /**
     * FormData for file uploads
     */
    async postFormData(url, formData, options = {}) {
        try {
            const headers = this.getHeaders(options.includeAuth !== false);
            delete headers['Content-Type']; // Let browser set it

            const config = {
                method: 'POST',
                headers,
                body: formData,
                ...options,
            };

            Logger.log(`Posting FormData: ${url}`);

            const response = await fetch(url, config);

            if (response.status === 401) {
                this.clearToken();
                window.location.href = '#home';
                throw new Error('Unauthorized');
            }

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'API Error');
            }

            return data;
        } catch (error) {
            Logger.error(`FormData error: ${url}`, error);
            throw error;
        }
    }

    // ===== AUTHENTICATION =====

    async register(email, username, password, fullName) {
        return this.post(API_ENDPOINTS.AUTH_REGISTER, {
            email,
            username,
            password,
            full_name: fullName,
        }, { includeAuth: false });
    }

    async login(email, password) {
        const response = await this.post(API_ENDPOINTS.AUTH_LOGIN, {
            email,
            password,
        }, { includeAuth: false });
        
        if (response.access_token) {
            this.setToken(response.access_token);
        }
        
        return response;
    }

    // ===== AI ENDPOINTS =====

    async chatWithAI(message, conversationId = null, context = null) {
        return this.post(API_ENDPOINTS.AI_CHAT, {
            content: message,
            conversation_id: conversationId,
            context: context || {},
        });
    }

    async generateContent(prompt, contentType, tone, maxTokens = 1024) {
        return this.post(API_ENDPOINTS.AI_GENERATE_CONTENT, {
            prompt,
            content_type: contentType,
            tone,
            max_tokens: maxTokens,
        });
    }

    async analyzeData(data, analysisType) {
        return this.post(API_ENDPOINTS.AI_ANALYZE, {
            input_data: data,
            task_type: analysisType,
        });
    }

    // ===== FILE PROCESSING =====

    async processFile(file, processType) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('process_type', processType);

        return this.postFormData(API_ENDPOINTS.FILES_PROCESS, formData);
    }

    // ===== GOOGLE APIS =====

    async getEmails(maxResults = 10) {
        return this.get(`${API_ENDPOINTS.GOOGLE_EMAILS}?max_results=${maxResults}`);
    }

    async sendEmail(to, subject, body, cc = [], bcc = []) {
        return this.post(API_ENDPOINTS.GOOGLE_SEND_EMAIL, {
            to,
            subject,
            body,
            cc,
            bcc,
        });
    }

    async getDriveFiles(maxResults = 10) {
        return this.get(`${API_ENDPOINTS.GOOGLE_DRIVE_FILES}?max_results=${maxResults}`);
    }

    async analyzeNLP(text) {
        return this.post(`${API_ENDPOINTS.GOOGLE_NLP_ANALYZE}?text=${encodeURIComponent(text)}`, {});
    }

    // ===== TASK MANAGEMENT =====

    async getTasks(skip = 0, limit = 10) {
        return this.get(`${API_ENDPOINTS.TASKS_LIST}?skip=${skip}&limit=${limit}`);
    }

    async getTask(taskId) {
        return this.get(API_ENDPOINTS.TASKS_GET(taskId));
    }

    async deleteTask(taskId) {
        return this.delete(API_ENDPOINTS.TASKS_DELETE(taskId));
    }

    // ===== HEALTH CHECK =====

    async checkHealth() {
        try {
            return await this.get(API_ENDPOINTS.HEALTH, { includeAuth: false });
        } catch (error) {
            Logger.error('Health check failed', error);
            return { status: 'offline' };
        }
    }

    async getStatus() {
        return this.get(API_ENDPOINTS.STATUS, { includeAuth: false });
    }
}

// Create global instance
const api = new APIService();

// Export for modular use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = APIService;
}