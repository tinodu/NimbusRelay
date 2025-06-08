/**
 * NimbusRelay - Imperial Email Management Application
 * Beautiful, minimalistic email client with AI-powered features
 * Imperial Purple Theme - Grandeur & Nobility
 */

class NimbusRelayApp {
    constructor() {
        this.socket = null;
        this.currentFolder = 'INBOX';
        this.currentEmail = null;
        this.emails = [];
        this.folders = [];
        this.isConfigured = false;
        
        this.init();
    }
    
    /**
     * Initialize the application
     */
    async init() {
        console.log('🌩️ Initializing NimbusRelay - Imperial Email Management');
        
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeApp());
        } else {
            this.initializeApp();
        }
    }
    
    /**
     * Initialize the application after DOM is ready
     */
    async initializeApp() {
        this.updateDebugStatus('🚀 Initializing NimbusRelay...');
        this.setupEventListeners();
        this.initializeSocket();
        await this.checkConfiguration();
    }
    
    /**
     * Setup event listeners for UI interactions
     */
    setupEventListeners() {
        // Configuration modal events
        const saveConfigBtn = document.getElementById('saveConfigBtn');
        if (saveConfigBtn) {
            saveConfigBtn.addEventListener('click', () => this.saveConfiguration());
        }
        
        // Main interface events
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshData());
        }
        
        const settingsBtn = document.getElementById('settingsBtn');
        if (settingsBtn) {
            settingsBtn.addEventListener('click', () => this.showSettings());
        }
        
        const analyzeSpamBtn = document.getElementById('analyzeSpamBtn');
        if (analyzeSpamBtn) {
            analyzeSpamBtn.addEventListener('click', () => this.analyzeAllSpam());
        }
        
        const generateDraftsBtn = document.getElementById('generateDraftsBtn');
        if (generateDraftsBtn) {
            generateDraftsBtn.addEventListener('click', () => this.generateAllDrafts());
        }
        
        // Handle Enter key in configuration fields
        document.querySelectorAll('#configModal fast-text-field').forEach(field => {
            field.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.saveConfiguration();
                }
            });
        });
        
        // Window load event
        window.addEventListener('load', () => {
            console.log('🌐 Window loaded');
            // Force initialization for debugging
            this.forceShowMainInterface();
        });
    }
    
    /**
     * Initialize Socket.IO connection
     */
    initializeSocket() {
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('🔗 Connected to NimbusRelay server');
            this.showStatus('Connected to server', 'success');
        });
        
        this.socket.on('disconnect', () => {
            console.log('🔌 Disconnected from NimbusRelay server');
            this.showStatus('Disconnected from server', 'warning');
        });
        
        this.socket.on('status', (data) => {
            console.log('📡 Server status:', data.message);
        });
    }
    
    /**
     * Check current configuration status
     */
    async checkConfiguration() {
        try {
            this.updateDebugStatus('🔍 Checking configuration...');
            console.log('🔍 Checking configuration status...');
            const response = await fetch('/api/config');
            const config = await response.json();
            
            console.log('📋 Configuration status:', config);
            this.isConfigured = config.configured;
            
            if (this.isConfigured) {
                this.updateDebugStatus('✅ Configuration complete, starting app...');
                console.log('✅ Configuration is complete, initializing app...');
                this.hideConfigModal();
                await this.connectServices();
                await this.loadInitialData();
                this.updateDebugStatus('🌩️ NimbusRelay ready!', false); // Hide debug bar when ready
            } else {
                this.updateDebugStatus('⚙️ Configuration needed');
                console.log('⚠️ Configuration incomplete, showing modal...');
                this.showConfigModal(config.missing_vars);
            }
        } catch (error) {
            this.updateDebugStatus('❌ Configuration check failed');
            console.error('❌ Failed to check configuration:', error);
            this.showStatus('Failed to check configuration', 'error');
            // Show config modal as fallback
            this.showConfigModal([]);
        }
    }
    
    /**
     * Show configuration modal
     */
    showConfigModal(missingVars = []) {
        const modal = document.getElementById('configModal');
        const mainInterface = document.getElementById('mainInterface');
        
        if (modal) {
            modal.style.display = 'flex';
        }
        
        if (mainInterface) {
            mainInterface.classList.remove('configured');
        }
        
        // Highlight missing variables
        missingVars.forEach(varName => {
            const fieldId = this.getFieldIdFromVarName(varName);
            const field = document.getElementById(fieldId);
            if (field) {
                field.style.borderColor = '#EF5350';
            }
        });
    }
    
    /**
     * Hide configuration modal and show main interface
     */
    hideConfigModal() {
        console.log('🔓 Hiding configuration modal and showing main interface...');
        const modal = document.getElementById('configModal');
        const mainInterface = document.getElementById('mainInterface');
        
        if (modal) {
            modal.style.display = 'none';
            console.log('✅ Configuration modal hidden');
        } else {
            console.warn('⚠️ Configuration modal element not found');
        }
        
        if (mainInterface) {
            mainInterface.classList.add('configured');
            mainInterface.style.display = 'grid'; // Force display
            console.log('✅ Main interface shown with configured class');
        } else {
            console.warn('⚠️ Main interface element not found');
        }
    }
    
    /**
     * Save configuration to server
     */
    async saveConfiguration() {
        try {
            this.showStatus('Saving configuration...', 'info');
            
            const config = {
                'IMAP_SERVER': document.getElementById('imapServer').value,
                'IMAP_PORT': document.getElementById('imapPort').value,
                'IMAP_USERNAME': document.getElementById('imapUsername').value,
                'IMAP_PASSWORD': document.getElementById('imapPassword').value,
                'AZURE_OPENAI_ENDPOINT': document.getElementById('azureEndpoint').value,
                'AZURE_OPENAI_API_KEY': document.getElementById('azureApiKey').value,
                'AZURE_OPENAI_DEPLOYMENT': document.getElementById('azureDeployment').value,
                'AZURE_OPENAI_API_VERSION': document.getElementById('azureApiVersion').value,
            };
            
            // Validate required fields
            const requiredFields = ['IMAP_SERVER', 'IMAP_USERNAME', 'IMAP_PASSWORD', 'AZURE_OPENAI_ENDPOINT', 'AZURE_OPENAI_API_KEY', 'AZURE_OPENAI_DEPLOYMENT'];
            const missingFields = requiredFields.filter(field => !config[field]);
            
            if (missingFields.length > 0) {
                this.showStatus(`Please fill in all required fields: ${missingFields.join(', ')}`, 'error');
                return;
            }
            
            const response = await fetch('/api/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config),
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showStatus('Configuration saved successfully', 'success');
                this.isConfigured = true;
                
                // Connect to services
                await this.connectServices();
                
                // Hide modal and load data
                this.hideConfigModal();
                await this.loadInitialData();
            } else {
                this.showStatus(`Failed to save configuration: ${result.error}`, 'error');
            }
        } catch (error) {
            console.error('Failed to save configuration:', error);
            this.showStatus('Failed to save configuration', 'error');
        }
    }
    
    /**
     * Connect to email and AI services
     */
    async connectServices() {
        try {
            this.showStatus('Connecting to services...', 'info');
            
            const response = await fetch('/api/connect', {
                method: 'POST',
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showStatus('Connected to all services successfully', 'success');
                return true;
            } else {
                this.showStatus(`Failed to connect: ${result.error}`, 'error');
                return false;
            }
        } catch (error) {
            console.error('Failed to connect to services:', error);
            this.showStatus('Failed to connect to services', 'error');
            return false;
        }
    }
    
    /**
     * Load initial data (folders and emails)
     */
    async loadInitialData() {
        await Promise.all([
            this.loadFolders(),
            this.loadEmails()
        ]);
    }
    
    /**
     * Load email folders from server
     */
    async loadFolders() {
        try {
            console.log('📁 Loading email folders...');
            // Load visible folders by default, with option to include hidden
            const includeHidden = false; // Can be made configurable later
            const response = await fetch(`/api/folders?include_hidden=${includeHidden}`);
            const data = await response.json();
            
            if (data.folders) {
                this.folders = data.folders;
                console.log(`✅ Loaded ${this.folders.length} folders:`, this.folders);
                this.renderFolders();
            } else if (data.error) {
                console.error('❌ Failed to load folders:', data.error);
                this.showEmptyFolders();
            } else {
                console.warn('⚠️ No folders returned from server');
                this.showEmptyFolders();
            }
        } catch (error) {
            console.error('❌ Failed to load folders:', error);
            this.showStatus('Failed to load folders', 'error');
            this.showEmptyFolders();
        }
    }
    
    /**
     * Show message when no folders are available
     */
    showEmptyFolders() {
        const folderList = document.getElementById('folderList');
        if (folderList) {
            folderList.innerHTML = `
                <div style="padding: 20px; text-align: center; color: #777777;">
                    <div style="font-size: 24px; margin-bottom: 12px;">📁</div>
                    <div>No folders available</div>
                    <div style="font-size: 12px; margin-top: 8px; color: #555;">
                        Check your email connection
                    </div>
                </div>
            `;
        }
    }
    
    /**
     * Load emails from current folder
     */
    async loadEmails(folder = this.currentFolder) {
        try {
            console.log(`📧 Loading emails from folder: ${folder}`);
            this.showEmailLoading();
            
            const response = await fetch(`/api/emails?folder=${encodeURIComponent(folder)}&limit=50`);
            const data = await response.json();
            
            if (data.emails) {
                this.emails = data.emails;
                console.log(`✅ Loaded ${this.emails.length} emails from ${folder}`);
                this.renderEmails();
            } else if (data.error) {
                console.error('❌ Failed to load emails:', data.error);
                this.showEmptyEmails(data.error);
            } else {
                console.warn('⚠️ No emails returned from server');
                this.showEmptyEmails('No emails found');
            }
        } catch (error) {
            console.error('❌ Failed to load emails:', error);
            this.showStatus('Failed to load emails', 'error');
            this.showEmptyEmails('Failed to connect to email server');
        }
    }
    
    /**
     * Show message when no emails are available
     */
    showEmptyEmails(message = 'No emails found') {
        const emailList = document.getElementById('emailList');
        if (emailList) {
            emailList.innerHTML = `
                <div style="padding: 40px; text-align: center; color: #777777;">
                    <div style="font-size: 48px; margin-bottom: 16px;">📬</div>
                    <div style="font-size: 16px; margin-bottom: 8px;">No emails found</div>
                    <div style="font-size: 12px; color: #555555;">${message}</div>
                </div>
            `;
        }
    }
    
    /**
     * Render folders in sidebar
     */
    renderFolders() {
        const folderList = document.getElementById('folderList');
        if (!folderList) return;
        
        folderList.innerHTML = '';
        
        this.folders.forEach(folder => {
            const folderElement = this.createFolderElement(folder);
            folderList.appendChild(folderElement);
        });
    }
    
    /**
     * Create folder element
     */
    createFolderElement(folder) {
        const div = document.createElement('div');
        div.className = 'folder-item';
        if (folder.name === this.currentFolder) {
            div.classList.add('active');
        }
        
        div.dataset.folder = folder.name;
        
        const icon = this.getFolderIcon(folder.type, folder.attributes || []);
        const displayName = folder.display_name || folder.name;
        
        // Add visual indicators for special folder properties
        let indicators = '';
        if (folder.is_hidden) {
            indicators += '<span class="folder-indicator hidden" title="Hidden folder">🔒</span>';
        }
        if (!folder.is_selectable) {
            indicators += '<span class="folder-indicator non-selectable" title="Non-selectable">⚠️</span>';
        }
        
        div.innerHTML = `
            <span class="folder-icon">${icon}</span>
            <span class="folder-name">${displayName}</span>
            ${indicators}
            <span class="folder-count" id="count-${folder.name.replace(/[^a-zA-Z0-9]/g, '_')}"></span>
        `;
        
        div.addEventListener('click', () => this.selectFolder(folder.name));
        
        return div;
    }
    
    /**
     * Get icon for folder type
     */
    getFolderIcon(type, attributes = []) {
        const icons = {
            'inbox': '📥',
            'sent': '📤',
            'drafts': '📝',
            'trash': '🗑️',
            'spam': '🛡️',
            'archive': '📦',
            'starred': '⭐',
            'important': '❗',
            'custom': '📁'
        };
        
        // Check for special attributes that might override the type-based icon
        if (attributes.includes('All')) return '📦';
        if (attributes.includes('Starred')) return '⭐';
        if (attributes.includes('Important')) return '❗';
        if (attributes.includes('Archive')) return '📦';
        
        return icons[type] || icons['custom'];
    }
    
    /**
     * Select a folder
     */
    async selectFolder(folderName) {
        this.currentFolder = folderName;
        
        // Update active folder in UI
        document.querySelectorAll('.folder-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const selectedFolder = document.querySelector(`[data-folder="${folderName}"]`);
        if (selectedFolder) {
            selectedFolder.classList.add('active');
        }
        
        // Update content title
        const contentTitle = document.getElementById('contentTitle');
        if (contentTitle) {
            const folderObj = this.folders.find(f => f.name === folderName);
            const displayName = folderObj ? folderObj.display_name : folderName;
            contentTitle.textContent = `📧 ${displayName}`;
        }
        
        // Load emails for selected folder
        await this.loadEmails(folderName);
    }
    
    /**
     * Show loading state for emails
     */
    showEmailLoading() {
        const emailList = document.getElementById('emailList');
        if (emailList) {
            emailList.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    Loading emails...
                </div>
            `;
        }
    }
    
    /**
     * Render emails in main content area
     */
    renderEmails() {
        const emailList = document.getElementById('emailList');
        if (!emailList) return;
        
        if (this.emails.length === 0) {
            emailList.innerHTML = `
                <div style="text-align: center; color: #777777; padding: 40px;">
                    <div style="font-size: 48px; margin-bottom: 16px;">📭</div>
                    <div>No emails found in this folder</div>
                </div>
            `;
            return;
        }
        
        emailList.innerHTML = '';
        
        this.emails.forEach(email => {
            const emailElement = this.createEmailElement(email);
            emailList.appendChild(emailElement);
        });
    }
    
    /**
     * Create email element
     */
    createEmailElement(email) {
        const div = document.createElement('div');
        div.className = 'email-item';
        div.dataset.emailId = email.id;
        
        const date = new Date(email.date);
        const formattedDate = this.formatDate(date);
        
        div.innerHTML = `
            <div class="email-date">${formattedDate}</div>
            <div class="email-sender">${this.escapeHtml(email.from || 'Unknown Sender')}</div>
            <div class="email-subject">${this.escapeHtml(email.subject || '(no subject)')}</div>
            <div class="email-preview">${this.escapeHtml(email.preview || '')}</div>
        `;
        
        div.addEventListener('click', () => this.selectEmail(email));
        
        return div;
    }
    
    /**
     * Select an email and show details
     */
    selectEmail(email) {
        this.currentEmail = email;
        
        // Update selected email in UI
        document.querySelectorAll('.email-item').forEach(item => {
            item.classList.remove('selected');
        });
        
        const selectedEmailElement = document.querySelector(`[data-email-id="${email.id}"]`);
        if (selectedEmailElement) {
            selectedEmailElement.classList.add('selected');
        }
        
        // Render email details
        this.renderEmailDetails(email);
    }
    
    /**
     * Render email details in right panel
     */
    renderEmailDetails(email) {
        const detailsPanel = document.getElementById('emailDetails');
        if (!detailsPanel) return;
        
        const date = new Date(email.date);
        const formattedDate = this.formatDateTime(date);
        
        detailsPanel.innerHTML = `
            <div class="email-header" style="margin-bottom: 24px;">
                <h3 style="color: #A88EBC; margin-bottom: 8px;">${this.escapeHtml(email.subject || '(no subject)')}</h3>
                <div style="color: #C0C0C0; margin-bottom: 4px;">From: <span>${this.escapeHtml(email.from || 'Unknown Sender')}</span></div>
                <div style="color: #999999; font-size: 12px;">${formattedDate}</div>
            </div>
            
            <div class="analysis-section">
                <div class="analysis-title">🛡️ Spam Analysis</div>
                <fast-button id="analyzeSpamSingleBtn" size="small">Analyze This Email</fast-button>
                <div id="spamResult" style="margin-top: 12px;"></div>
            </div>
            
            <div class="analysis-section">
                <div class="analysis-title">🔍 Email Analysis</div>
                <fast-button id="analyzeEmailBtn" size="small">Analyze Email Content</fast-button>
                <div id="emailAnalysis" style="margin-top: 12px;"></div>
            </div>
            
            <div class="analysis-section">
                <div class="analysis-title">✍️ Draft Response</div>
                <fast-button id="generateDraftBtn" size="small">Generate Draft Response</fast-button>
                <div id="draftResult" style="margin-top: 12px;"></div>
            </div>
        `;
        
        // Setup event listeners for analysis buttons
        this.setupEmailDetailListeners();
    }
    
    /**
     * Setup event listeners for email detail buttons
     */
    setupEmailDetailListeners() {
        const analyzeSpamBtn = document.getElementById('analyzeSpamSingleBtn');
        if (analyzeSpamBtn) {
            analyzeSpamBtn.addEventListener('click', () => this.analyzeEmailSpam(this.currentEmail));
        }
        
        const analyzeEmailBtn = document.getElementById('analyzeEmailBtn');
        if (analyzeEmailBtn) {
            analyzeEmailBtn.addEventListener('click', () => this.analyzeEmailContent(this.currentEmail));
        }
        
        const generateDraftBtn = document.getElementById('generateDraftBtn');
        if (generateDraftBtn) {
            generateDraftBtn.addEventListener('click', () => this.generateEmailDraft(this.currentEmail));
        }
    }
    
    /**
     * Analyze email for spam
     */
    async analyzeEmailSpam(email) {
        try {
            const button = document.getElementById('analyzeSpamSingleBtn');
            const resultDiv = document.getElementById('spamResult');
            
            if (button) button.textContent = 'Analyzing...';
            if (resultDiv) resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div>Analyzing for spam...</div>';
            
            const response = await fetch('/api/analyze-spam', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(email),
            });
            
            const result = await response.json();
            
            if (button) button.textContent = 'Analyze This Email';
            
            if (result.error) {
                if (resultDiv) resultDiv.innerHTML = `<div class="status-error" style="padding: 12px; border-radius: 6px;">Error: ${result.error}</div>`;
            } else {
                const isSpam = result.classification === 'Spam/Junk';
                const statusClass = isSpam ? 'spam' : 'not-spam';
                if (resultDiv) {
                    resultDiv.innerHTML = `
                        <div class="spam-result ${statusClass}">
                            <strong>${result.classification}</strong>
                            ${result.confidence ? `<br>Confidence: ${Math.round(result.confidence * 100)}%` : ''}
                            ${result.reason ? `<br><small>${result.reason}</small>` : ''}
                        </div>
                    `;
                }
            }
        } catch (error) {
            console.error('Failed to analyze spam:', error);
            const button = document.getElementById('analyzeSpamSingleBtn');
            const resultDiv = document.getElementById('spamResult');
            
            if (button) button.textContent = 'Analyze This Email';
            if (resultDiv) resultDiv.innerHTML = '<div class="status-error" style="padding: 12px; border-radius: 6px;">Failed to analyze email</div>';
        }
    }
    
    /**
     * Analyze email content
     */
    async analyzeEmailContent(email) {
        try {
            const button = document.getElementById('analyzeEmailBtn');
            const resultDiv = document.getElementById('emailAnalysis');
            
            if (button) button.textContent = 'Analyzing...';
            if (resultDiv) resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div>Analyzing email content...</div>';
            
            const response = await fetch('/api/analyze-email', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(email),
            });
            
            const result = await response.json();
            
            if (button) button.textContent = 'Analyze Email Content';
            
            if (result.error) {
                if (resultDiv) resultDiv.innerHTML = `<div class="status-error" style="padding: 12px; border-radius: 6px;">Error: ${result.error}</div>`;
            } else {
                if (resultDiv) {
                    resultDiv.innerHTML = `
                        <div style="background: rgba(30, 27, 69, 0.3); padding: 16px; border-radius: 6px; border: 1px solid rgba(75, 0, 130, 0.3);">
                            <pre style="white-space: pre-wrap; font-size: 13px; line-height: 1.5; margin: 0; color: #C0C0C0;">${this.escapeHtml(result.analysis)}</pre>
                        </div>
                    `;
                }
            }
        } catch (error) {
            console.error('Failed to analyze email:', error);
            const button = document.getElementById('analyzeEmailBtn');
            const resultDiv = document.getElementById('emailAnalysis');
            
            if (button) button.textContent = 'Analyze Email Content';
            if (resultDiv) resultDiv.innerHTML = '<div class="status-error" style="padding: 12px; border-radius: 6px;">Failed to analyze email</div>';
        }
    }
    
    /**
     * Generate draft response for email
     */
    async generateEmailDraft(email) {
        try {
            const button = document.getElementById('generateDraftBtn');
            const resultDiv = document.getElementById('draftResult');
            
            if (button) button.textContent = 'Generating...';
            if (resultDiv) resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div>Generating draft response...</div>';
            
            // First analyze the email, then generate draft
            const analyzeResponse = await fetch('/api/analyze-email', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(email),
            });
            
            const analyzeResult = await analyzeResponse.json();
            
            if (analyzeResult.error) {
                throw new Error(analyzeResult.error);
            }
            
            // Generate draft based on analysis
            const draftResponse = await fetch('/api/generate-draft', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ analysis: analyzeResult.analysis }),
            });
            
            const draftResult = await draftResponse.json();
            
            if (button) button.textContent = 'Generate Draft Response';
            
            if (draftResult.error) {
                if (resultDiv) resultDiv.innerHTML = `<div class="status-error" style="padding: 12px; border-radius: 6px;">Error: ${draftResult.error}</div>`;
            } else {
                if (resultDiv) {
                    resultDiv.innerHTML = `
                        <div style="background: rgba(30, 27, 69, 0.3); padding: 16px; border-radius: 6px; border: 1px solid rgba(75, 0, 130, 0.3);">
                            <div style="margin-bottom: 12px; font-weight: 600; color: #A88EBC;">Generated Draft:</div>
                            <pre style="white-space: pre-wrap; font-size: 13px; line-height: 1.5; margin: 0; color: #E6E6E6;">${this.escapeHtml(draftResult.draft)}</pre>
                        </div>
                    `;
                }
            }
        } catch (error) {
            console.error('Failed to generate draft:', error);
            const button = document.getElementById('generateDraftBtn');
            const resultDiv = document.getElementById('draftResult');
            
            if (button) button.textContent = 'Generate Draft Response';
            if (resultDiv) resultDiv.innerHTML = '<div class="status-error" style="padding: 12px; border-radius: 6px;">Failed to generate draft</div>';
        }
    }
    
    /**
     * Analyze all emails for spam
     */
    async analyzeAllSpam() {
        this.showStatus('Analyzing all emails for spam...', 'info');
        // Implementation for bulk spam analysis
        console.log('Analyzing all emails for spam...');
    }
    
    /**
     * Generate drafts for all emails
     */
    async generateAllDrafts() {
        this.showStatus('Generating draft responses...', 'info');
        // Implementation for bulk draft generation
        console.log('Generating draft responses...');
    }
    
    /**
     * Refresh all data
     */
    async refreshData() {
        this.showStatus('Refreshing data...', 'info');
        await this.loadInitialData();
        this.showStatus('Data refreshed successfully', 'success');
    }
    
    /**
     * Show settings modal
     */
    showSettings() {
        this.showConfigModal();
    }
    
    /**
     * Show status message
     */
    showStatus(message, type = 'info') {
        console.log(`[${type.toUpperCase()}] ${message}`);
        
        // Create status toast
        const toast = document.createElement('div');
        toast.className = `status-toast status-${type}`;
        toast.style.cssText = `
            position: fixed;
            top: 80px;
            right: 24px;
            padding: 12px 20px;
            border-radius: 6px;
            color: white;
            font-weight: 600;
            z-index: 2000;
            animation: slideInLeft 0.3s ease;
            max-width: 300px;
            word-wrap: break-word;
        `;
        
        // Set background color based on type
        const colors = {
            'success': '#40A74F',
            'error': '#EF5350',
            'warning': '#FFA726',
            'info': '#4B0082'
        };
        toast.style.backgroundColor = colors[type] || colors.info;
        
        toast.textContent = message;
        document.body.appendChild(toast);
        
        // Remove toast after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.style.animation = 'fadeOut 0.3s ease';
                setTimeout(() => {
                    if (toast.parentNode) {
                        toast.parentNode.removeChild(toast);
                    }
                }, 300);
            }
        }, 5000);
    }
    
    /**
     * Update debug status bar
     */
    updateDebugStatus(message, show = true) {
        const debugStatus = document.getElementById('debugStatus');
        const debugText = document.getElementById('debugText');
        
        if (debugStatus && debugText) {
            debugText.textContent = message;
            debugStatus.style.display = show ? 'block' : 'none';
        }
        console.log('🐛 Debug:', message);
    }
    
    /**
     * Force initialization for debugging
     */
    forceShowMainInterface() {
        console.log('🔧 Force showing main interface...');
        const modal = document.getElementById('configModal');
        const mainInterface = document.getElementById('mainInterface');
        
        if (modal) {
            modal.style.display = 'none';
        }
        
        if (mainInterface) {
            mainInterface.classList.add('configured');
            mainInterface.style.display = 'grid';
            console.log('✅ Main interface forced to display');
        }
        
        // Force load some demo data
        this.showDemoData();
    }
    
    /**
     * Show demo data when no real data is available
     */
    showDemoData() {
        console.log('📋 Loading demo data...');
        
        // Demo folders
        this.folders = [
            { name: 'INBOX', display_name: 'Inbox', type: 'inbox' },
            { name: 'SENT', display_name: 'Sent', type: 'sent' },
            { name: 'DRAFTS', display_name: 'Drafts', type: 'drafts' },
            { name: 'SPAM', display_name: 'Spam', type: 'spam' },
            { name: 'TRASH', display_name: 'Trash', type: 'trash' }
        ];
        
        // Demo emails
        this.emails = [
            {
                id: '1',
                from: 'demo@example.com',
                subject: 'Welcome to NimbusRelay',
                preview: 'Thank you for trying our Imperial Purple email management solution...',
                date: new Date().toLocaleDateString()
            },
            {
                id: '2', 
                from: 'support@nimbusrelay.com',
                subject: 'Getting Started Guide',
                preview: 'Here are some tips to help you make the most of your email experience...',
                date: new Date().toLocaleDateString()
            }
        ];
        
        this.renderFolders();
        this.renderEmails();
    }
    
    /**
     * Utility function to escape HTML
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Format date for display
     */
    formatDate(date) {
        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const emailDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());
        
        if (emailDate.getTime() === today.getTime()) {
            return date.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
        } else if (emailDate.getTime() === today.getTime() - 86400000) {
            return 'Yesterday';
        } else {
            return date.toLocaleDateString('en-GB', { day: '2-digit', month: '2-digit', year: '2-digit' });
        }
    }
    
    /**
     * Format date and time for details
     */
    formatDateTime(date) {
        return date.toLocaleString('en-GB', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    /**
     * Get field ID from environment variable name
     */
    getFieldIdFromVarName(varName) {
        const mapping = {
            'IMAP_SERVER': 'imapServer',
            'IMAP_PORT': 'imapPort',
            'IMAP_USERNAME': 'imapUsername',
            'IMAP_PASSWORD': 'imapPassword',
            'AZURE_OPENAI_ENDPOINT': 'azureEndpoint',
            'AZURE_OPENAI_API_KEY': 'azureApiKey',
            'AZURE_OPENAI_DEPLOYMENT': 'azureDeployment',
            'AZURE_OPENAI_API_VERSION': 'azureApiVersion',
        };
        return mapping[varName] || varName.toLowerCase();
    }
}

// Initialize the application when the script loads
const app = new NimbusRelayApp();

// Global functions for debugging
window.nimbusDebug = {
    app: app,
    forceShow: () => app.forceShowMainInterface(),
    checkConfig: () => app.checkConfiguration(),
    loadData: () => app.loadInitialData(),
    showDemo: () => app.showDemoData()
};

console.log('🌩️ NimbusRelay loaded. Debug functions available via window.nimbusDebug');
console.log('💡 Try: nimbusDebug.forceShow() to force show the interface');
