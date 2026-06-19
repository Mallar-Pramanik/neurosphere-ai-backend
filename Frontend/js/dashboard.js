/**
 * Dashboard Service
 * Handles all dashboard features and interactions
 */

let currentConversationId = null;
let selectedFile = null;

// ===== TAB MANAGEMENT =====

function showDashboardTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.dashboard-tab').forEach(tab => {
        tab.classList.remove('active');
    });

    // Remove active class from all links
    document.querySelectorAll('.dashboard-sidebar a').forEach(link => {
        link.classList.remove('active');
    });

    // Show selected tab
    const tabId = tabName + 'Tab';
    const tab = document.getElementById(tabId);
    if (tab) {
        tab.classList.add('active');
    }

    // Add active class to clicked link
    event.target.classList.add('active');

    Logger.log('Switched to tab:', tabName);
}

// ===== CHAT FUNCTIONALITY =====

async function sendChatMessage() {
    if (!checkAuth()) return;

    const input = document.getElementById('chatInput');
    const message = input.value.trim();

    if (!message) {
        showNotification('Please enter a message', 'warning');
        return;
    }

    try {
        // Add user message to UI
        addChatMessage(message, 'user');
        input.value = '';

        // Send to API
        Logger.log('Sending message...', message);

        const response = await api.chatWithAI(message, currentConversationId);

        if (response.response) {
            currentConversationId = response.conversation_id;
            addChatMessage(response.response, 'assistant');
            Logger.log('Got response:', response);
        }

    } catch (error) {
        Logger.error('Chat error', error);
        showNotification('Failed to send message: ' + error.message, 'error');
        addChatMessage(error.message, 'assistant');
    }
}

function addChatMessage(content, role) {
    const messagesContainer = document.getElementById('chatMessages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;
    
    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);

    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// ===== CONTENT GENERATION =====

async function generateContent(event) {
    event.preventDefault();
    if (!checkAuth()) return;

    const prompt = document.getElementById('contentPrompt').value;
    const contentType = document.getElementById('contentType').value;
    const contentTone = document.getElementById('contentTone').value;
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const spinner = submitBtn.querySelector('.spinner');

    try {
        submitBtn.disabled = true;
        spinner.classList.remove('hidden');

        Logger.log('Generating content...', { contentType, contentTone });

        const response = await api.generateContent(prompt, contentType, contentTone);

        if (response.content) {
            displayGeneratedContent(response.content);
            showNotification('Content generated successfully!', 'success');
        }

    } catch (error) {
        Logger.error('Generation error', error);
        showNotification('Failed to generate content: ' + error.message, 'error');
    } finally {
        submitBtn.disabled = false;
        spinner.classList.add('hidden');
    }
}

function displayGeneratedContent(content) {
    const container = document.getElementById('generatedContent');
    const textDiv = document.getElementById('generatedText');

    textDiv.textContent = content;
    container.classList.remove('hidden');
    container.scrollIntoView({ behavior: 'smooth' });
}

function copyToClipboard() {
    const text = document.getElementById('generatedText').textContent;
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success');
    });
}

// ===== DATA ANALYSIS =====

async function analyzeData(event) {
    event.preventDefault();
    if (!checkAuth()) return;

    const text = document.getElementById('analyzeText').value;
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const spinner = submitBtn.querySelector('.spinner');

    try {
        submitBtn.disabled = true;
        spinner.classList.remove('hidden');

        Logger.log('Analyzing data...');

        const response = await api.analyzeData(text, 'general');

        if (response.analysis) {
            const resultDiv = document.getElementById('analysisText');
            resultDiv.textContent = JSON.stringify(response.analysis, null, 2);
            document.getElementById('analysisResult').classList.remove('hidden');
            showNotification('Analysis complete!', 'success');
        }

    } catch (error) {
        Logger.error('Analysis error', error);
        showNotification('Failed to analyze data: ' + error.message, 'error');
    } finally {
        submitBtn.disabled = false;
        spinner.classList.add('hidden');
    }
}

// ===== FILE PROCESSING =====

function handleFileSelect() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];

    if (!file) return;

    if (file.size > FILE_OPTIONS.maxSize) {
        showNotification('File is too large. Maximum size is 10MB.', 'error');
        return;
    }

    selectedFile = file;
    showNotification(`File selected: ${file.name}`, 'success');
}

async function processFile() {
    if (!checkAuth()) return;

    if (!selectedFile) {
        showNotification('Please select a file first', 'warning');
        return;
    }

    const processType = document.getElementById('processType').value;
    const btn = event.target;
    const spinner = btn.querySelector('.spinner');

    try {
        btn.disabled = true;
        spinner.classList.remove('hidden');

        Logger.log('Processing file...', { filename: selectedFile.name, processType });

        const response = await api.processFile(selectedFile, processType);

        if (response.result) {
            displayProcessedFile(response);
            showNotification('File processed successfully!', 'success');
        }

    } catch (error) {
        Logger.error('File processing error', error);
        showNotification('Failed to process file: ' + error.message, 'error');
    } finally {
        btn.disabled = false;
        spinner.classList.add('hidden');
    }
}

function displayProcessedFile(fileData) {
    const container = document.getElementById('processedFiles');
    
    const fileItem = document.createElement('div');
    fileItem.className = 'file-item';
    fileItem.innerHTML = `
        <h4>📁 ${fileData.filename}</h4>
        <p><strong>Process Type:</strong> ${fileData.process_type}</p>
        <div style="margin-top: 1rem; padding: 1rem; background: rgba(15, 23, 42, 0.5); border-radius: 8px;">
            <p>${JSON.stringify(fileData.result)}</p>
        </div>
    `;

    container.insertBefore(fileItem, container.firstChild);
}

// ===== TASKS ===== 

async function fetchTasks() {
    if (!checkAuth()) return;

    try {
        const response = await api.getTasks();
        displayTasks(response.tasks || []);
    } catch (error) {
        Logger.error('Failed to fetch tasks', error);
        showNotification('Failed to load tasks', 'error');
    }
}

function displayTasks(tasks) {
    const container = document.getElementById('tasksList');

    if (tasks.length === 0) {
        container.innerHTML = '<p class="empty-state">No tasks yet</p>';
        return;
    }

    container.innerHTML = tasks.map(task => `
        <div class="task-item">
            <div class="task-info">
                <h4>${task.task_type.replace('_', ' ').toUpperCase()}</h4>
                <p>${task.input_data.substring(0, 100)}...</p>
                <div class="file-meta">
                    <span>${new Date(task.created_at).toLocaleDateString()}</span>
                </div>
            </div>
            <span class="task-status ${task.status}">${task.status}</span>
            <div class="item-actions">
                <button class="btn btn-secondary" onclick="deleteTask(${task.id})">Delete</button>
            </div>
        </div>
    `).join('');
}

async function deleteTask(taskId) {
    if (!confirm('Delete this task?')) return;

    try {
        await api.deleteTask(taskId);
        showNotification('Task deleted', 'success');
        fetchTasks();
    } catch (error) {
        Logger.error('Delete error', error);
        showNotification('Failed to delete task', 'error');
    }
}

// ===== EMAIL FUNCTIONALITY =====

async function fetchEmails() {
    if (!checkAuth()) return;

    try {
        const response = await api.getEmails();
        displayEmails(response.emails || []);
    } catch (error) {
        Logger.error('Failed to fetch emails', error);
        showNotification('Failed to load emails. Make sure Gmail API is configured.', 'error');
    }
}

function displayEmails(emails) {
    const container = document.getElementById('emailsList');

    if (emails.length === 0) {
        container.innerHTML = '<p class="empty-state">No emails found</p>';
        return;
    }

    container.innerHTML = emails.map(email => `
        <div class="email-item">
            <h4>📧 ${email.subject || '(No Subject)'}</h4>
            <p><strong>From:</strong> ${email.from_email}</p>
            <p>${email.body || 'No content'}</p>
            <div class="file-meta">
                <span>${email.date || 'Unknown date'}</span>
            </div>
        </div>
    `).join('');
}

// ===== GOOGLE DRIVE =====

async function fetchDriveFiles() {
    if (!checkAuth()) return;

    try {
        const response = await api.getDriveFiles();
        displayDriveFiles(response.files || []);
    } catch (error) {
        Logger.error('Failed to fetch drive files', error);
        showNotification('Failed to load Drive files. Make sure Drive API is configured.', 'error');
    }
}

function displayDriveFiles(files) {
    const container = document.getElementById('driveFilesList');

    if (files.length === 0) {
        container.innerHTML = '<p class="empty-state">No files found in Google Drive</p>';
        return;
    }

    container.innerHTML = files.map(file => `
        <div class="file-item">
            <h4>☁️ ${file.name}</h4>
            <div class="file-meta">
                <span>📄 ${file.mime_type}</span>
                <span>👤 ${file.owner}</span>
                <span>📅 ${new Date(file.modified_time).toLocaleDateString()}</span>
            </div>
        </div>
    `).join('');
}

// ===== PRICING & PLANS =====

function selectPlan(plan) {
    if (!checkAuth()) return;
    
    showNotification(`Plan "${plan}" selected! Upgrade coming soon.`, 'success');
}

// ===== DATA MANAGEMENT =====

function clearAllData() {
    currentConversationId = null;
    selectedFile = null;
    document.getElementById('chatMessages').innerHTML = '';
    document.getElementById('contentPrompt').value = '';
    document.getElementById('analyzeText').value = '';
    document.getElementById('generatedContent').classList.add('hidden');
    document.getElementById('analysisResult').classList.add('hidden');
}

// ===== INITIALIZATION =====

function initDashboard() {
    Logger.log('Initializing dashboard...');

    // Set initial tab
    if (isAuthenticated()) {
        showDashboardTab('chat');
    }

    // Auto-load tasks periodically
    if (isAuthenticated()) {
        fetchTasks();
        setInterval(() => {
            if (document.getElementById('tasksTab').classList.contains('active')) {
                fetchTasks();
            }
        }, 30000); // Every 30 seconds
    }
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDashboard);
} else {
    initDashboard();
}

// Export for modular use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        sendChatMessage,
        generateContent,
        analyzeData,
        processFile,
        fetchTasks,
        fetchEmails,
        fetchDriveFiles,
    };
}