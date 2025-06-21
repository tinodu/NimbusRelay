// Persist connection config before refresh and restore after reload

window.addEventListener('beforeunload', () => {
    // Save config to localStorage if available
    if (window.nimbusConfig) {
        localStorage.setItem('nimbusConfig', JSON.stringify(window.nimbusConfig));
    }
    // Optionally, call disconnect API to clean up server-side
    navigator.sendBeacon && navigator.sendBeacon('/api/disconnect');
});

window.addEventListener('load', () => {
    // Restore config from localStorage and reconnect if needed
    const configStr = localStorage.getItem('nimbusConfig');
    if (configStr) {
        try {
            window.nimbusConfig = JSON.parse(configStr);
            // Auto-reconnect using saved config
            if (window.nimbusConfig && typeof connectServices === 'function') {
                connectServices();
            }
        } catch (e) {
            console.warn('Failed to restore Nimbus config from localStorage:', e);
        }
    }
});
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

        // Tool result box elements
        this.toolResultBox = null;
        this.toolResultContent = null;
        this.closeToolResultBoxBtn = null;
        
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

        // Setup tool result box
        this.toolResultBox = document.getElementById('toolResultBox');
        this.toolResultContent = document.getElementById('toolResultContent');
        this.closeToolResultBoxBtn = document.getElementById('closeToolResultBox');
        if (this.closeToolResultBoxBtn) {
            this.closeToolResultBoxBtn.addEventListener('click', () => this.hideToolResultBox());
        }

        this.setupEmailDetailListeners();

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
        
        const moveSpamBtn = document.getElementById('moveSpamBtn');
        if (moveSpamBtn) {
            moveSpamBtn.addEventListener('click', () => this.moveAllSpamToJunk());
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
        await this.loadFolders();
        await this.loadEmails();
        // Load folder counts after folders are loaded
        await this.loadFolderCounts();
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
     * Load folder counts
     */
    async loadFolderCounts() {
        try {
            console.log('📊 Loading folder counts...');
            const response = await fetch('/api/folder-counts');
            const data = await response.json();
            
            if (data.counts) {
                console.log('✅ Loaded folder counts:', data.counts);
                // Update count badges for each folder
                Object.entries(data.counts).forEach(([folderName, count]) => {
                    const countElement = document.getElementById(`count-${folderName.replace(/[^a-zA-Z0-9]/g, '_')}`);
                    if (countElement) {
                        countElement.textContent = count;
                        // Always show the count, even if it's 0
                        countElement.style.display = 'inline-block';
                    }
                });
            } else if (data.error) {
                console.error('❌ Failed to load folder counts:', data.error);
            }
        } catch (error) {
            console.error('❌ Failed to load folder counts:', error);
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
                    <div style="font-size: 16px; margin-bottom: 8px;">No emails found in this folder</div>
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
        // Auto-select the first folder if available and not already selected
        if (this.folders.length > 0 && !this.currentFolder) {
            const firstFolder = this.folders[0].name;
            console.log('[DEBUG] Auto-selecting first folder:', firstFolder);
            this.selectFolder(firstFolder);
        }
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
            <span class="folder-count" id="count-${folder.name.replace(/[^a-zA-Z0-9]/g, '_')}">0</span>
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
            // Show 5 shimmer placeholders
            emailList.innerHTML = `
                <div>
                    ${Array(5).fill(`
                        <div class="email-item" style="padding:16px 0;display:flex;flex-direction:column;gap:8px;">
                            <div class="loading-shimmer" style="width:80px;height:12px;border-radius:6px;"></div>
                            <div class="loading-shimmer" style="width:160px;height:16px;border-radius:6px;"></div>
                            <div class="loading-shimmer" style="width:220px;height:14px;border-radius:6px;"></div>
                            <div class="loading-shimmer" style="width:100%;height:10px;border-radius:6px;"></div>
                        </div>
                    `).join('')}
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
        const formattedDateTime = this.formatDateTime(date);

        div.innerHTML = `
            <div class="email-date">${formattedDateTime}</div>
            <div class="email-sender">${this.escapeHtml(email.from || 'Unknown Sender')}</div>
            <div class="email-subject">${this.escapeHtml(email.subject || '(no subject)')}</div>
        `;

        div.addEventListener('click', () => this.selectEmail(email));

        return div;
    }
    
    /**
     * Select an email and show details
     */
    selectEmail(email) {
        this.hideToolResultBox(); // Close tool boxes when switching to preview
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

        // Prepare both plain and HTML bodies
        let plainBody = '';
        let htmlBody = '';
        if (email.text_body) {
            plainBody = `<pre style="white-space: pre-wrap; color: #E6E6E6; font-size: 15px; margin:0;">${this.escapeHtml(email.text_body)}</pre>`;
        } else if (email.body) {
            plainBody = `<pre style="white-space: pre-wrap; color: #E6E6E6; font-size: 15px; margin:0;">${this.escapeHtml(email.body)}</pre>`;
        }
        if (email.html_body) {
            htmlBody = `<div class="email-html-body html-bg">${this.sanitizeHtml(email.html_body)}</div>`;
// DEBUG: Log original and sanitized HTML for diagnosis
console.log('[DEBUG] Original HTML body:', email.html_body);
console.log('[DEBUG] Sanitized HTML body:', this.sanitizeHtml(email.html_body));
        }

        // Decide which toggle to show
        const hasPlain = !!plainBody;
        const hasHtml = !!htmlBody;
        let showToggle = hasPlain && hasHtml;

        // Default view: HTML if available, else plain
        if (!this.emailContentView) this.emailContentView = {};
        const emailId = email.id || 'current';
        if (!this.emailContentView[emailId]) {
            this.emailContentView[emailId] = hasHtml ? 'html' : 'plain';
        }
        let view = this.emailContentView[emailId];

        // Render the main details panel (no toggle/buttons inline)
        detailsPanel.innerHTML = `
            <div class="email-header" style="margin-bottom: 24px;">
                <h3 style="color: #A88EBC; margin-bottom: 8px;">${this.escapeHtml(email.subject || '(no subject)')}</h3>
                <div style="color: #C0C0C0; margin-bottom: 4px;">From: <span>${this.escapeHtml(email.from || 'Unknown Sender')}</span></div>
                <div style="color: #999999; font-size: 12px;">${formattedDate}</div>
            </div>
            <div class="email-body" id="emailBodyContent">
                ${
                    view === 'html'
                        ? (htmlBody || plainBody || `<div style="color:#777;">(No content)</div>`)
                        : (plainBody || htmlBody || `<div style="color:#777;">(No content)</div>`)
                }
            </div>
        `;

        // Set up toolbar toggle/source buttons
        const plainBtn = document.getElementById('togglePlainBtn');
        const htmlBtn = document.getElementById('toggleHtmlBtn');
        const viewHtmlSourceBtn = document.getElementById('viewHtmlSourceBtn');

        // Hide all by default
        if (plainBtn) plainBtn.style.display = 'none';
        if (htmlBtn) htmlBtn.style.display = 'none';
        if (viewHtmlSourceBtn) viewHtmlSourceBtn.style.display = 'none';

        if (showToggle || hasHtml) {
            // Show/hide and set up toggle buttons
            if (plainBtn && htmlBtn && showToggle) {
                plainBtn.style.display = '';
                htmlBtn.style.display = '';
                plainBtn.classList.toggle('active', view === 'plain');
                htmlBtn.classList.toggle('active', view === 'html');
                plainBtn.onclick = () => {
                    this.emailContentView[emailId] = 'plain';
                    this.renderEmailDetails(email);
                };
                htmlBtn.onclick = () => {
                    this.emailContentView[emailId] = 'html';
                    this.renderEmailDetails(email);
                };
            }
            // Show/hide and set up HTML source button
            if (viewHtmlSourceBtn) {
                if (hasHtml) {
                    viewHtmlSourceBtn.style.display = '';
                    viewHtmlSourceBtn.disabled = false;
                    viewHtmlSourceBtn.onclick = () => {
                        this.showToolResultBox(`
                            <div style="background: rgba(30, 27, 69, 0.3); padding: 16px; border-radius: 6px; border: 1px solid rgba(75, 0, 130, 0.3); max-height: 60vh; overflow:auto;">
                                <div style="margin-bottom: 12px; font-weight: 600; color: #A88EBC;">HTML Source:</div>
                                <pre style="white-space: pre-wrap; font-size: 13px; line-height: 1.5; margin: 0; color: #E6E6E6;">${this.escapeHtml(email.html_body || '')}</pre>
                            </div>
                        `);
                    };
                } else {
                    viewHtmlSourceBtn.style.display = 'none';
                    viewHtmlSourceBtn.onclick = null;
                    viewHtmlSourceBtn.disabled = true;
                }
            }
        }
    }

    /**
     * Basic HTML sanitizer: strips script/style and dangerous tags/attributes.
     * Allows only a safe subset of tags (b, i, u, a, p, br, ul, ol, li, strong, em, span, div, pre, code, blockquote).
     */
    sanitizeHtml(html) {
        // Remove script/style tags and their content
        html = html.replace(/<script[\s\S]*?>[\s\S]*?<\/script>/gi, '');
        html = html.replace(/<style[\s\S]*?>[\s\S]*?<\/style>/gi, '');
        // Remove event handlers and javascript: links
        html = html.replace(/ on\w+="[^"]*"/gi, '');
        html = html.replace(/ on\w+='[^']*'/gi, '');
        html = html.replace(/javascript:/gi, '');
        // Allow a safe subset of tags commonly used in emails, including all table tags (case-insensitive)
        const allowedTagsList = [
            'b','i','u','a','p','br','ul','ol','li','strong','em','span','div','pre','code','blockquote',
            'table','thead','tbody','tfoot','tr','td','th','img','hr',
            'h1','h2','h3','h4','h5','h6'
        ];
        const allowedTags = new RegExp(
            `^/?(${allowedTagsList.join('|')})$`,
            'i'
        );
        // Remove all tags not in allowedTagsList (case-insensitive)
        html = html.replace(/<\/?([a-z][a-z0-9]*)\b[^>]*>/gi, function (match, tag) {
            return allowedTags.test(tag) ? match : '';
        });
        // Remove hrefs except http(s)/mailto
        html = html.replace(/<a\s+([^>]*?)href\s*=\s*(['"])(?!https?:|mailto:)[^'"]*\2([^>]*)>/gi, '<a $1$3>');
        // Remove dangerous img attributes
        html = html.replace(/<img([^>]+)>/gi, function (imgTag, attrs) {
            // Only allow src, alt, width, height, style
            const safeAttrs = attrs.match(/(src|alt|width|height|style)=["'][^"']*["']/gi);
            return `<img${safeAttrs ? ' ' + safeAttrs.join(' ') : ''}>`;
        });
        return html;
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

        const showRawBtn = document.getElementById('showRawEmailBtn');
        if (showRawBtn) {
            showRawBtn.addEventListener('click', () => this.showRawEmail(this.currentEmail));
        }
    }

    /**
     * Show RAW email content in the tool result box
     */
    async showRawEmail(email) {
        if (!email || !email.id) {
            this.showToolResultBox('<div class="status-error" style="padding: 12px; border-radius: 6px;">No email selected</div>');
            return;
        }
        try {
            this.showToolResultBox('<div class="loading"><div class="spinner"></div>Loading raw email...</div>');
            const response = await fetch(`/api/email-raw?id=${encodeURIComponent(email.id)}`);
            const result = await response.json();
            if (result.error) {
                this.showToolResultBox(`<div class="status-error" style="padding: 12px; border-radius: 6px;">Error: ${this.escapeHtml(result.error)}</div>`);
            } else {
                this.showToolResultBox(`
                    <div style="background: rgba(30, 27, 69, 0.3); padding: 16px; border-radius: 6px; border: 1px solid rgba(75, 0, 130, 0.3); max-height: 60vh; overflow:auto;">
                        <div style="margin-bottom: 12px; font-weight: 600; color: #A88EBC;">RAW Email Source:</div>
                        <pre style="white-space: pre-wrap; font-size: 13px; line-height: 1.5; margin: 0; color: #E6E6E6;">${this.escapeHtml(result.raw || '')}</pre>
                    </div>
                `);
            }
        } catch (error) {
            this.showToolResultBox('<div class="status-error" style="padding: 12px; border-radius: 6px;">Failed to load raw email</div>');
        }
    }

    /**
     * Show the tool result box with given HTML content
     */
    showToolResultBox(content) {
        if (this.toolResultBox && this.toolResultContent) {
            this.toolResultContent.innerHTML = content;
            this.toolResultBox.style.display = 'block';
        }
    }

    /**
     * Hide the tool result box
     */
    hideToolResultBox() {
        if (this.toolResultBox && this.toolResultContent) {
            this.toolResultBox.style.display = 'none';
            this.toolResultContent.innerHTML = '';
        }
    }
    
    /**
     * Analyze email for spam
     */
    async analyzeEmailSpam(email) {
        try {
            const button = document.getElementById('analyzeSpamSingleBtn');
            let originalContent;
            if (button) {
                button.disabled = true;
                originalContent = button.innerHTML;
                // Do not change button.innerHTML; keep icon + text visible
            }
            this.showToolResultBox('<div class="loading"><div class="spinner"></div>Analyzing for spam...</div>');
            
            const response = await fetch('/api/analyze-spam', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(email),
            });
            
            const result = await response.json();
            
            if (button) {
                button.disabled = false;
                // No need to restore innerHTML; it was never changed
            }
            
            if (result.error) {
                this.showToolResultBox(`<div class="status-error" style="padding: 12px; border-radius: 6px;">Error: ${result.error}</div>`);
            } else {
                // Check if classification indicates spam - handle multiple formats
                const classification = result.classification || '';
                const isSpam = classification.toLowerCase().includes('spam') ||
                              classification.toLowerCase().includes('junk') ||
                              classification === 'Spam/Junk';
                const statusClass = isSpam ? 'spam' : 'not-spam';
                this.showToolResultBox(`
                    <div class="spam-result ${statusClass}">
                        <strong>${result.classification}</strong>
                        ${result.confidence ? `<br>Confidence: ${Math.round(result.confidence * 100)}%` : ''}
                        ${result.reason ? `<br><small>${result.reason}</small>` : ''}
                    </div>
                `);
            }
        } catch (error) {
            console.error('Failed to analyze spam:', error);
            const button = document.getElementById('analyzeSpamSingleBtn');
            if (button) {
                button.disabled = false;
                button.innerHTML = '🛡️';
            }
            this.showToolResultBox('<div class="status-error" style="padding: 12px; border-radius: 6px;">Failed to analyze email</div>');
        }
    }
    
    /**
     * Analyze email content
     */
    async analyzeEmailContent(email) {
        try {
            const button = document.getElementById('analyzeEmailBtn');
            if (button) {
                button.disabled = true;
                var originalContent = button.innerHTML;
                // Do not change button.innerHTML; keep icon + text visible
            }
            this.showToolResultBox('<div class="loading"><div class="spinner"></div>Analyzing email content...</div>');
            
            const response = await fetch('/api/analyze-email', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(email),
            });
            
            const result = await response.json();
            
            if (button) {
                button.disabled = false;
                // No need to restore innerHTML; it was never changed
            }
            
            if (result.error) {
                this.showToolResultBox(`<div class="status-error" style="padding: 12px; border-radius: 6px;">Error: ${result.error}</div>`);
            } else {
                // Clean up markdown code block if present
                let analysis = result.analysis || '';
                // Remove triple backticks and optional "markdown" language tag
                analysis = analysis.trim().replace(/^```(?:markdown)?\s*/i, '').replace(/\s*```$/, '');
                let html = '';
                if (window.marked) {
                    html = window.marked.parse(analysis);
                } else {
                    // fallback: show as pre if marked is not loaded
                    html = `<pre style="white-space: pre-wrap; font-size: 13px; line-height: 1.5; margin: 0; color: #C0C0C0;">${this.escapeHtml(analysis)}</pre>`;
                }
                this.showToolResultBox(`
                    <div class="analysis-section">
                        <div class="analysis-title">🔍 Email Analysis</div>
                        <div class="markdown-body">${html}</div>
                    </div>
                `);
            }
        } catch (error) {
            console.error('Failed to analyze email:', error);
            const button = document.getElementById('analyzeEmailBtn');
            if (button) {
                button.disabled = false;
                button.innerHTML = '🔍';
            }
            this.showToolResultBox('<div class="status-error" style="padding: 12px; border-radius: 6px;">Failed to analyze email</div>');
        }
    }
    
    /**
     * Generate draft response for email
     */
    async generateEmailDraft(email) {
        try {
            const button = document.getElementById('generateDraftBtn');
            if (button) {
                button.disabled = true;
                var originalContent = button.innerHTML;
            }
            this.showToolResultBox('<div class="loading"><div class="spinner"></div>Generating draft response...</div>');
            
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
            
            if (button) {
                button.disabled = false;
            }
            
            // Compose quoted original email (plain text, modern style)
            function quoteEmail(text) {
                if (!text) return '';
                return text.split('\n').map(line => '> ' + line).join('\n');
            }
            // Prefer text_body, fallback to body
            const originalBody = email.text_body || email.body || '';
            const quotedOriginal = quoteEmail(originalBody);

            // Compose the content for the editor
            const draftText = draftResult.draft || '';
            const combinedContent = draftText + '\n\n' + quotedOriginal;

            // Create a full-screen modal dialog for the editor
            const modalHtml = `
                <div id="draftEditorModal" style="
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100vw;
                    height: 100vh;
                    background: rgba(0, 0, 0, 0.9);
                    backdrop-filter: blur(5px);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 2000;
                ">
                    <div style="
                        background: #1A1A1A;
                        border: 2px solid #4B0082;
                        border-radius: 12px;
                        width: 90vw;
                        max-width: 1200px;
                        height: 90vh;
                        display: flex;
                        flex-direction: column;
                        box-shadow: 0 16px 32px rgba(75, 0, 130, 0.4);
                    ">
                        <div style="
                            display: flex;
                            align-items: center;
                            justify-content: space-between;
                            padding: 20px 24px;
                            border-bottom: 1px solid rgba(75, 0, 130, 0.3);
                            flex-shrink: 0;
                        ">
                            <h2 style="color: #A88EBC; margin: 0; font-size: 20px;">✍️ Edit Draft Response</h2>
                            <fast-button id="closeDraftEditor" appearance="stealth" style="padding: 8px;">✖</fast-button>
                        </div>
                        <div style="
                            flex: 1;
                            padding: 24px;
                            display: flex;
                            flex-direction: column;
                            overflow: hidden;
                            box-sizing: border-box;
                        ">
                            <!-- Email fields section -->
                            <div style="
                                margin-bottom: 20px;
                                display: flex;
                                flex-direction: column;
                                gap: 12px;
                            ">
                                <div style="display: flex; align-items: center; gap: 16px;">
                                    <label style="color: #A88EBC; width: 80px; text-align: right;">To:</label>
                                    <input type="email" id="draftTo" style="
                                        flex: 1;
                                        padding: 8px 12px;
                                        background: #0F0F0F;
                                        border: 1px solid rgba(75, 0, 130, 0.3);
                                        border-radius: 4px;
                                        color: #E6E6E6;
                                        font-size: 14px;
                                        outline: none;
                                        transition: border-color 0.2s ease;
                                    " onfocus="this.style.borderColor='#A88EBC'" onblur="this.style.borderColor='rgba(75, 0, 130, 0.3)'" value="${this.escapeHtml(email.from || '')}" />
                                </div>
                                <div style="display: flex; align-items: center; gap: 16px;">
                                    <label style="color: #A88EBC; width: 80px; text-align: right;">Cc:</label>
                                    <input type="email" id="draftCc" style="
                                        flex: 1;
                                        padding: 8px 12px;
                                        background: #0F0F0F;
                                        border: 1px solid rgba(75, 0, 130, 0.3);
                                        border-radius: 4px;
                                        color: #E6E6E6;
                                        font-size: 14px;
                                        outline: none;
                                        transition: border-color 0.2s ease;
                                    " onfocus="this.style.borderColor='#A88EBC'" onblur="this.style.borderColor='rgba(75, 0, 130, 0.3)'" />
                                </div>
                                <div style="display: flex; align-items: center; gap: 16px;">
                                    <label style="color: #A88EBC; width: 80px; text-align: right;">Bcc:</label>
                                    <input type="email" id="draftBcc" style="
                                        flex: 1;
                                        padding: 8px 12px;
                                        background: #0F0F0F;
                                        border: 1px solid rgba(75, 0, 130, 0.3);
                                        border-radius: 4px;
                                        color: #E6E6E6;
                                        font-size: 14px;
                                        outline: none;
                                        transition: border-color 0.2s ease;
                                    " onfocus="this.style.borderColor='#A88EBC'" onblur="this.style.borderColor='rgba(75, 0, 130, 0.3)'" />
                                </div>
                                <div style="display: flex; align-items: center; gap: 16px;">
                                    <label style="color: #A88EBC; width: 80px; text-align: right;">Subject:</label>
                                    <input type="text" id="draftSubject" style="
                                        flex: 1;
                                        padding: 8px 12px;
                                        background: #0F0F0F;
                                        border: 1px solid rgba(75, 0, 130, 0.3);
                                        border-radius: 4px;
                                        color: #E6E6E6;
                                        font-size: 14px;
                                        outline: none;
                                        transition: border-color 0.2s ease;
                                    " onfocus="this.style.borderColor='#A88EBC'" onblur="this.style.borderColor='rgba(75, 0, 130, 0.3)'" value="${email.subject ? 'Re: ' + this.escapeHtml(email.subject) : ''}" />
                                </div>
                            </div>
                            <textarea id="draftRichEditor" style="
                                flex: 1;
                                width: 100%;
                                height: 100%;
                                font-size: 16px;
                                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                                resize: none;
                                box-sizing: border-box;
                                background: #0F0F0F;
                                border: 1px solid rgba(75, 0, 130, 0.3);
                                border-radius: 6px;
                                color: #E6E6E6;
                                padding: 16px;
                                outline: none;
                                transition: border-color 0.2s ease;
                            " onfocus="this.style.borderColor='#A88EBC'" onblur="this.style.borderColor='rgba(75, 0, 130, 0.3)'"></textarea>
                        </div>
                        <div style="
                            display: flex;
                            gap: 12px;
                            justify-content: flex-end;
                            padding: 20px 24px;
                            border-top: 1px solid rgba(75, 0, 130, 0.3);
                            flex-shrink: 0;
                        ">
                            <fast-button id="cancelDraft" appearance="stealth">Cancel</fast-button>
                            <fast-button id="sendDraft" appearance="accent">Send Draft</fast-button>
                        </div>
                    </div>
                </div>
            `;

            // Insert the modal into the body
            document.body.insertAdjacentHTML('beforeend', modalHtml);

            // Set up event listeners and populate content
            setTimeout(() => {
                const editor = document.getElementById('draftRichEditor');
                const closeBtn = document.getElementById('closeDraftEditor');
                const cancelBtn = document.getElementById('cancelDraft');
                const sendBtn = document.getElementById('sendDraft');
                const modal = document.getElementById('draftEditorModal');

                if (editor) {
                    editor.value = combinedContent;
                    editor.focus();
                    // Set cursor to the beginning of the text
                    editor.setSelectionRange(0, 0);
                    // Scroll to the top to show the cursor
                    editor.scrollTop = 0;
                }

                // Close modal function
                const closeModal = () => {
                    if (modal) {
                        modal.remove();
                    }
                };

                // Set up close handlers
                if (closeBtn) closeBtn.addEventListener('click', closeModal);
                if (cancelBtn) cancelBtn.addEventListener('click', closeModal);
                if (sendBtn) {
                    sendBtn.addEventListener('click', () => {
                        // Get email field values
                        const toField = document.getElementById('draftTo');
                        const ccField = document.getElementById('draftCc');
                        const bccField = document.getElementById('draftBcc');
                        const subjectField = document.getElementById('draftSubject');
                        
                        const emailData = {
                            to: toField ? toField.value : '',
                            cc: ccField ? ccField.value : '',
                            bcc: bccField ? bccField.value : '',
                            subject: subjectField ? subjectField.value : '',
                            body: editor ? editor.value : ''
                        };
                        
                        // TODO: Implement actual send functionality via API
                        console.log('Sending draft with email data:', emailData);
                        
                        // Show success message
                        this.showStatus('Draft prepared successfully', 'success');
                        closeModal();
                    });
                }

                // Close on Escape key
                const handleEscape = (e) => {
                    if (e.key === 'Escape') {
                        closeModal();
                        document.removeEventListener('keydown', handleEscape);
                    }
                };
                document.addEventListener('keydown', handleEscape);

                console.log('[DEBUG] Draft editor modal created and displayed');
            }, 100);

            // Hide the tool result box
            this.hideToolResultBox();

        } catch (error) {
            console.error('Failed to generate draft:', error);
            const button = document.getElementById('generateDraftBtn');
            if (button) {
                button.disabled = false;
            }
            this.showToolResultBox('<div class="status-error" style="padding: 12px; border-radius: 6px;">Failed to generate draft</div>');
        }
    }
    
    /**
     * Analyze all emails for spam
     */
    async analyzeAllSpam() {
        this.showStatus('Analyzing all emails for spam...', 'info');
        console.log('Analyzing all emails for spam...');
        
        try {
            if (!this.emails || this.emails.length === 0) {
                this.showStatus('No emails to analyze', 'warning');
                return;
            }
            
            let spamCount = 0;
            let totalAnalyzed = 0;
            const results = [];
            
            for (const email of this.emails) {
                try {
                    const response = await fetch('/api/analyze-spam', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(email)
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        totalAnalyzed++;
                        
                        // Check if classification indicates spam
                        const isSpam = result.classification && 
                                      (result.classification.toLowerCase().includes('spam') || 
                                       result.classification.toLowerCase().includes('junk'));
                        
                        if (isSpam) {
                            spamCount++;
                        }
                        
                        results.push({
                            email: email,
                            result: { ...result, is_spam: isSpam }
                        });
                        
                        // Update status with progress
                        this.showStatus(`Analyzed ${totalAnalyzed}/${this.emails.length} emails...`, 'info');
                    } else {
                        const errorResult = await response.json().catch(() => ({ error: 'Unknown error' }));
                        console.error('Failed to analyze email:', email.subject, 'Error:', errorResult);
                        this.showStatus(`Error analyzing ${email.subject}: ${errorResult.error || 'Unknown error'}`, 'error');
                    }
                } catch (error) {
                    console.error('Error analyzing email:', email.subject, error);
                }
            }
            
            // Show final results
            const message = `Spam analysis complete: ${spamCount} spam emails found out of ${totalAnalyzed} analyzed`;
            this.showStatus(message, spamCount > 0 ? 'warning' : 'success');
            
            // Update UI to highlight spam emails
            this.highlightSpamEmails(results);
            
        } catch (error) {
            console.error('Error during spam analysis:', error);
            this.showStatus('Failed to analyze emails for spam', 'error');
        }
    }
    
    /**
     * Move all spam emails to INBOX.spam folder
     */
    async moveAllSpamToJunk() {
        this.showStatus('Moving spam emails to junk folder...', 'info');
        console.log('Moving already marked spam emails to junk folder...');
        
        try {
            // Find all emails that are already marked as spam in the UI
            const spamEmailElements = document.querySelectorAll('.email-item.spam-detected');
            
            if (spamEmailElements.length === 0) {
                this.showStatus('No emails marked as spam found. Please run "Analyze Spam" first to identify spam emails.', 'warning');
                return;
            }
            
            let movedCount = 0;
            const errors = [];
            
            console.log(`Found ${spamEmailElements.length} emails already marked as spam`);
            
            // Move each spam-marked email
            for (const emailElement of spamEmailElements) {
                try {
                    const emailId = emailElement.getAttribute('data-email-id');
                    
                    // Find the corresponding email object
                    const email = this.emails.find(e => e.id === emailId);
                    if (!email) {
                        console.warn(`Email with ID ${emailId} not found in emails array`);
                        continue;
                    }
                    
                    console.log(`Moving spam email: ${email.subject} from ${email.from}`);
                    
                    // Move to spam folder
                    const moveResponse = await fetch('/api/move-email', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            email_id: email.id,
                            source_folder: this.currentFolder,
                            target_folder: 'INBOX.spam'
                        })
                    });
                    
                    if (moveResponse.ok) {
                        movedCount++;
                        console.log(`Successfully moved spam email: ${email.subject}`);
                        
                        // Remove the email element from the UI immediately
                        emailElement.remove();
                    } else {
                        const moveError = await moveResponse.json().catch(() => ({ error: 'Unknown error' }));
                        errors.push(`Failed to move "${email.subject}": ${moveError.error || 'Unknown error'}`);
                    }
                    
                    // Update status with progress
                    this.showStatus(`Moved ${movedCount}/${spamEmailElements.length} spam emails...`, 'info');
                    
                } catch (moveError) {
                    console.error('Error moving email:', moveError);
                    errors.push(`Failed to move email: ${moveError.message}`);
                }
            }
            
            // Show final results
            let message = `Spam move complete: ${movedCount} already marked spam emails moved to junk folder`;
            
            if (errors.length > 0) {
                message += ` (${errors.length} errors occurred)`;
                console.error('Errors during spam move operation:', errors);
            }
            
            this.showStatus(message, errors.length > 0 ? 'warning' : 'success');
            
            // Refresh the email list to reflect changes if any emails were moved
            if (movedCount > 0) {
                await this.loadEmails();
            }
            
        } catch (error) {
            console.error('Error during spam move operation:', error);
            this.showStatus('Failed to move spam emails', 'error');
        }
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
        
        // No demo data: only show shimmer/loading states on force show
        // this.showDemoData();
    }
    
    /**
     * Highlight spam emails in the UI
     */
    highlightSpamEmails(analysisResults) {
        analysisResults.forEach(({ email, result }) => {
            if (result.is_spam) {
                const emailElement = document.querySelector(`.email-item[data-email-id="${email.id}"]`);
                if (emailElement) {
                    emailElement.classList.add('spam-detected');
                    
                    // Add spam indicator
                    const spamIndicator = document.createElement('span');
                    spamIndicator.className = 'spam-indicator';
                    spamIndicator.innerHTML = '🚨 SPAM';
                    spamIndicator.style.cssText = `
                        color: #EF5350;
                        font-weight: bold;
                        font-size: 10px;
                        background: rgba(239, 83, 80, 0.1);
                        padding: 2px 6px;
                        border-radius: 4px;
                        margin-left: 8px;
                    `;
                    
                    const subjectElement = emailElement.querySelector('.email-subject');
                    if (subjectElement && !subjectElement.querySelector('.spam-indicator')) {
                        subjectElement.appendChild(spamIndicator);
                    }
                }
            }
        });
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
                to: 'user@nimbusrelay.com',
                subject: 'Welcome to NimbusRelay',
                preview: 'Thank you for trying our Imperial Purple email management solution...',
                date: new Date().toLocaleDateString(),
                content_type: 'text/plain',
                body: 'Thank you for trying our Imperial Purple email management solution. We hope you enjoy the experience and find it useful for managing your emails efficiently.',
            },
            {
                id: '2', 
                from: 'support@nimbusrelay.com',
                to: 'user@nimbusrelay.com',
                subject: 'Getting Started Guide',
                preview: 'Here are some tips to help you make the most of your email experience...',
                date: new Date().toLocaleDateString(),
                content_type: 'text/plain',
                body: 'Here are some tips to help you make the most of your email experience with NimbusRelay. Please refer to our documentation for more detailed information.',
            },
            {
                id: '3', 
                from: 'spam@fake.org',
                to: 'user@nimbusrelay.com',
                subject: 'FREE PRIZE - ACT NOW!',
                preview: 'You have won a guaranteed prize! Click here to claim your free reward...',
                date: new Date().toLocaleDateString(),
                content_type: 'text/html',
                body: 'URGENT! You have won a guaranteed prize worth $1000! This is a limited time offer, act now! Click here to claim your free reward immediately!',
            },
            {
                id: '4', 
                from: 'noreply@scam.net',
                to: 'user@nimbusrelay.com',
                subject: '(no subject)',
                preview: 'Urgent message regarding your account...',
                date: new Date().toLocaleDateString(),
                content_type: 'text/plain',
                body: 'Your account needs immediate attention. Please click the link below to verify your identity.',
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
