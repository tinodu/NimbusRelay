# NimbusRelay User Manual

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Configuration](#configuration)
4. [User Interface Guide](#user-interface-guide)
5. [Core Features](#core-features)
6. [AI-Powered Analysis](#ai-powered-analysis)
7. [Email Management](#email-management)
8. [Troubleshooting](#troubleshooting)
9. [Security & Privacy](#security--privacy)
10. [FAQ](#faq)

---

## Introduction

### What is NimbusRelay?

NimbusRelay is an advanced, AI-powered email management system that provides intelligent email analysis, spam detection, and automated email handling capabilities. Built with a modern web interface and powered by Azure OpenAI services, NimbusRelay transforms how you interact with your email.

### Key Features

- **🤖 AI-Powered Email Analysis**: Comprehensive content analysis using Azure OpenAI
- **🛡️ Advanced Spam Detection**: Intelligent spam filtering with detailed explanations
- **📧 Email Composition Assistance**: AI-assisted email drafting and responses
- **🔍 Real-time Email Processing**: Live updates through WebSocket connections
- **🎨 Modern UI**: Clean, responsive interface with Imperial Purple theme
- **🔐 Secure Configuration**: Environment-based configuration management
- **📱 Cross-Platform**: Web-based interface accessible from any device

### System Requirements

- **Operating System**: Windows, macOS, or Linux
- **Python**: Version 3.8 or higher
- **Web Browser**: Modern browser with JavaScript enabled (Chrome, Firefox, Safari, Edge)
- **Network**: Internet connection for AI services and email access
- **Memory**: Minimum 2GB RAM recommended
- **Storage**: At least 500MB free space

---

## Getting Started

### Installation

1. **Clone or Download the Repository**
   ```
   Download NimbusRelay to your desired directory
   ```

2. **Install Python Dependencies**
   ```powershell
   cd C:\path\to\NimbusRelay
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   Create a `.env` file in the root directory (see Configuration section)

4. **Launch the Application**
   ```powershell
   python main.py
   ```
   Or use the provided batch file:
   ```powershell
   start.bat
   ```

### First Launch

When you first launch NimbusRelay:

1. The application will start on `http://localhost:5000`
2. Open your web browser and navigate to the URL
3. You'll be presented with the configuration screen
4. Complete the setup process (detailed in Configuration section)

---

## Configuration

### Required Configuration Parameters

NimbusRelay requires several configuration parameters to function properly. These are set through environment variables or the web interface.

#### Azure OpenAI Configuration

| Parameter | Description | Example |
|-----------|-------------|---------|
| `AZURE_OPENAI_ENDPOINT` | Your Azure OpenAI service endpoint | `https://your-resource.openai.azure.com/` |
| `AZURE_OPENAI_API_KEY` | API key for Azure OpenAI | `your-api-key-here` |
| `AZURE_OPENAI_DEPLOYMENT` | Deployment name | `gpt-4o` |
| `AZURE_OPENAI_API_VERSION` | API version (default: 2024-12-01-preview) | `2024-12-01-preview` |

#### IMAP Configuration (Incoming Mail)

| Parameter | Description | Example |
|-----------|-------------|---------|
| `IMAP_SERVER` | IMAP server address | `imap.gmail.com` |
| `IMAP_PORT` | IMAP port (default: 993) | `993` |
| `IMAP_USERNAME` | Your email username | `your-email@gmail.com` |
| `IMAP_PASSWORD` | Your email password or app password | `your-password` |

#### SMTP Configuration (Outgoing Mail)

| Parameter | Description | Example |
|-----------|-------------|---------|
| `SMTP_SERVER` | SMTP server address | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port (default: 587) | `587` |
| `SMTP_USERNAME` | SMTP username | `your-email@gmail.com` |
| `SMTP_PASSWORD` | SMTP password | `your-password` |
| `SMTP_SENDER_EMAIL` | Sender email address | `your-email@gmail.com` |
| `SMTP_USE_TLS` | Enable TLS encryption (default: true) | `true` |

### Configuration Methods

#### Method 1: Web Interface Configuration

1. Launch NimbusRelay
2. Navigate to `http://localhost:5000`
3. Click on the "Configuration" panel
4. Fill in all required fields
5. Click "Save Configuration"
6. Click "Connect Services" to test the connection

#### Method 2: Environment File (.env)

Create a `.env` file in the root directory:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# IMAP Configuration
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
IMAP_USERNAME=your-email@gmail.com
IMAP_PASSWORD=your-password

# SMTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-password
SMTP_SENDER_EMAIL=your-email@gmail.com
SMTP_USE_TLS=true
```

### Email Provider Setup

#### Gmail Setup

1. **Enable 2-Factor Authentication** in your Google Account
2. **Generate an App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
   - Use this password instead of your regular password

3. **Configuration**:
   - IMAP Server: `imap.gmail.com`
   - IMAP Port: `993`
   - SMTP Server: `smtp.gmail.com`
   - SMTP Port: `587`

#### Outlook/Hotmail Setup

1. **Enable App Passwords** in Microsoft Account security settings
2. **Configuration**:
   - IMAP Server: `outlook.office365.com`
   - IMAP Port: `993`
   - SMTP Server: `smtp-mail.outlook.com`
   - SMTP Port: `587`

#### Custom Email Provider

Consult your email provider's documentation for IMAP/SMTP settings.

---

## User Interface Guide

### Main Interface Layout

The NimbusRelay interface follows a three-panel layout:

```
┌─────────────────────────────────────────────────┐
│                   Header Bar                    │
├──────────┬──────────────────┬───────────────────┤
│          │                  │                   │
│ Sidebar  │   Email List     │   Main Content    │
│          │                  │                   │
│ - Folders│ - Message Items  │ - Email Reader    │
│ - Config │ - Navigation     │ - AI Analysis     │
│ - Status │ - Filters        │ - Composition     │
│          │                  │                   │
└──────────┴──────────────────┴───────────────────┘
```

### Header Bar

- **Application Title**: "NimbusRelay - Imperial Email Management"
- **Connection Status**: Real-time connection indicator
- **Navigation Controls**: Quick access to main functions

### Sidebar Panel

#### Configuration Section
- **Status Indicator**: Shows configuration completeness
- **Configuration Form**: Input fields for all required settings
- **Save/Connect Buttons**: Apply settings and test connections

#### Folder Navigation
- **Folder List**: All email folders with message counts
- **Refresh Button**: Update folder information
- **Filter Options**: Show/hide system folders

### Email List Panel

- **Message Preview Cards**: Compact email summaries
- **Sorting Options**: Sort by date, sender, subject
- **Selection Controls**: Multi-select functionality
- **Pagination**: Navigate through large email lists

### Main Content Panel

- **Email Reader**: Full email content display
- **AI Analysis Panel**: Detailed email analysis results
- **Action Buttons**: Reply, Forward, Delete, Archive
- **Composition Area**: Email drafting interface

### Theme and Visual Design

NimbusRelay uses an **Imperial Purple** theme:
- **Primary Color**: Deep purple (#4B0082)
- **Background**: Dark theme for reduced eye strain
- **Accent Colors**: Complementary purples and whites
- **Typography**: Modern, readable fonts
- **Animations**: Smooth transitions and micro-interactions

---

## Core Features

### Email Management

#### Viewing Emails

1. **Select a Folder**: Choose from the sidebar folder list
2. **Browse Messages**: Scroll through the email list
3. **Read Email**: Click on any message to view full content
4. **Multi-select**: Use Ctrl+Click for multiple selection

#### Email Actions

- **Reply**: Respond to the sender
- **Reply All**: Respond to all recipients
- **Forward**: Send email to new recipients
- **Delete**: Move to trash folder
- **Archive**: Move to archive folder
- **Mark as Spam**: Train the spam filter

#### Folder Management

- **View All Folders**: Access inbox, sent, drafts, etc.
- **Custom Folders**: Support for user-created folders
- **Hidden Folders**: Toggle visibility of system folders
- **Folder Counts**: Real-time message counts

### Real-time Updates

NimbusRelay uses WebSocket technology for:
- **Live Email Updates**: New messages appear instantly
- **Status Notifications**: Connection and processing status
- **Analysis Progress**: Real-time AI processing updates
- **Error Reporting**: Immediate feedback on issues

### Search and Filtering

- **Text Search**: Find emails by content, sender, or subject
- **Date Filters**: Search within date ranges
- **Folder Filters**: Limit search to specific folders
- **Status Filters**: Unread, flagged, important emails

---

## AI-Powered Analysis

### Email Content Analysis

NimbusRelay provides comprehensive AI-powered email analysis:

#### Analysis Components

1. **Structural Analysis**
   - Email sections identification
   - Content hierarchy mapping
   - Format and layout analysis

2. **Language & Tone Analysis**
   - Sentiment detection (positive, neutral, negative)
   - Formality level assessment
   - Language style identification
   - Cultural context recognition

3. **Content Extraction**
   - Key information extraction
   - Important dates and deadlines
   - Action items identification
   - Contact information detection

4. **Intent Analysis**
   - Primary purpose identification
   - Request type classification
   - Urgency level assessment
   - Response requirements

#### Using Email Analysis

1. **Select an Email**: Choose any email from your inbox
2. **View Analysis**: Analysis appears automatically in the main panel
3. **Interpret Results**: Review the detailed breakdown
4. **Take Action**: Use insights to prioritize and respond

### Spam Detection

#### Advanced Spam Analysis

NimbusRelay uses multi-layered spam detection:

1. **Header Analysis**
   - Sender authentication (SPF, DKIM, DMARC)
   - IP reputation checking
   - Domain verification
   - Routing path analysis

2. **Content Analysis**
   - Trigger word detection
   - Grammar and language patterns
   - Formatting anomalies
   - Link verification

3. **Behavioral Analysis**
   - Mass distribution patterns
   - Frequency analysis
   - Historical comparison
   - Reputation scoring

#### Spam Detection Results

- **Classification**: "Spam/Junk" or "Valid"
- **Confidence Score**: Probability rating
- **Detailed Explanation**: Reasoning behind classification
- **Risk Factors**: Specific suspicious elements identified
- **Recommendations**: Suggested actions

#### Manual Spam Management

1. **Review Classification**: Check AI spam determination
2. **Override Decision**: Mark as spam/not spam if needed
3. **Train Filter**: Help improve future detection
4. **Whitelist/Blacklist**: Manage trusted/blocked senders

### Email Drafting Assistance

#### AI-Powered Composition

1. **Draft Suggestions**: AI-generated email templates
2. **Tone Adjustment**: Modify formality and style
3. **Content Enhancement**: Improve clarity and structure
4. **Response Generation**: Automated reply suggestions

#### Using Draft Assistance

1. **Compose New Email**: Click compose button
2. **Describe Intent**: Briefly describe your email purpose
3. **Review Suggestions**: AI provides draft options
4. **Customize Content**: Edit and personalize the draft
5. **Send or Save**: Complete your email workflow

---

## Email Management

### Inbox Organization

#### Folder Structure

NimbusRelay supports standard email folders:
- **INBOX**: Primary incoming messages
- **Sent**: Messages you've sent
- **Drafts**: Unsent draft messages
- **Trash**: Deleted messages
- **Archive**: Archived messages
- **Spam/Junk**: Filtered spam messages
- **Custom Folders**: User-created organization folders

#### Message Management

1. **Reading Messages**
   - Single-click to preview
   - Double-click for full view
   - Keyboard navigation support

2. **Organizing Messages**
   - Drag and drop between folders
   - Bulk operations for multiple emails
   - Automatic categorization options

3. **Search and Filter**
   - Quick search bar
   - Advanced filter options
   - Saved search queries

### Email Composition

#### Creating New Emails

1. **Compose Button**: Click to start new email
2. **Recipient Fields**: To, CC, BCC support
3. **Subject Line**: Clear, descriptive subjects
4. **Message Body**: Rich text editing capabilities
5. **Attachments**: File attachment support
6. **AI Assistance**: Optional AI-powered suggestions

#### Reply and Forward

1. **Reply Options**
   - Reply to sender only
   - Reply to all recipients
   - Forward to new recipients

2. **Quote Handling**
   - Automatic quote formatting
   - Selective quote inclusion
   - Threading maintenance

### Email Threading

- **Conversation View**: Related messages grouped together
- **Thread Navigation**: Easy movement between related emails
- **Context Preservation**: Maintain conversation history

---

## Troubleshooting

### Common Issues and Solutions

#### Connection Problems

**Issue**: Cannot connect to email server
**Solutions**:
1. Verify server settings (IMAP/SMTP addresses and ports)
2. Check username and password
3. Ensure network connectivity
4. Verify firewall/antivirus settings
5. Try different ports (993/143 for IMAP, 587/465 for SMTP)

**Issue**: Authentication failures
**Solutions**:
1. Use app-specific passwords for Gmail/Outlook
2. Enable "Less secure app access" if required
3. Check 2-factor authentication settings
4. Verify account permissions

#### AI Service Issues

**Issue**: AI analysis not working
**Solutions**:
1. Verify Azure OpenAI configuration
2. Check API key validity
3. Confirm deployment name and API version
4. Monitor API usage limits
5. Check network connectivity to Azure services

**Issue**: Slow AI responses
**Solutions**:
1. Check internet connection speed
2. Verify Azure service region
3. Monitor API rate limits
4. Consider upgrading Azure OpenAI tier

#### Interface Problems

**Issue**: Interface not loading properly
**Solutions**:
1. Clear browser cache and cookies
2. Try different web browser
3. Disable browser extensions temporarily
4. Check JavaScript is enabled
5. Refresh the page

**Issue**: WebSocket connection failures
**Solutions**:
1. Check firewall settings
2. Verify port 5000 is available
3. Try restarting the application
4. Check for proxy/VPN interference

### Performance Optimization

#### System Performance

1. **Memory Usage**
   - Monitor RAM usage during operation
   - Restart application if memory issues occur
   - Close unused browser tabs

2. **Network Optimization**
   - Use wired connection when possible
   - Close bandwidth-heavy applications
   - Consider email sync frequency

3. **Storage Management**
   - Regularly clean temporary files
   - Archive old emails
   - Monitor disk space

### Error Messages

#### Common Error Messages and Solutions

**"Configuration incomplete"**
- Complete all required configuration fields
- Save configuration before connecting

**"Failed to connect to IMAP server"**
- Verify server address and port
- Check network connectivity
- Confirm credentials

**"Azure OpenAI API error"**
- Verify API key and endpoint
- Check service availability
- Monitor usage quotas

**"WebSocket connection failed"**
- Restart the application
- Check firewall settings
- Try different browser

### Logging and Debugging

#### Application Logs

- Check console output for error messages
- Browser developer tools for client-side issues
- Network tab for connection problems

#### Debug Mode

Enable debug mode for detailed logging:
1. Set `DEBUG=True` in configuration
2. Restart application
3. Monitor enhanced log output
4. Report issues with log details

---

## Security & Privacy

### Data Protection

#### Email Data Security

1. **Local Processing**: Emails processed locally when possible
2. **Encrypted Connections**: All email connections use TLS/SSL
3. **Secure Storage**: Credentials stored in environment variables
4. **No Data Retention**: AI analysis results not permanently stored

#### API Security

1. **Secure Endpoints**: All API endpoints protected
2. **Authentication**: Email server authentication required
3. **CORS Protection**: Cross-origin request filtering
4. **Input Validation**: All inputs validated and sanitized

### Privacy Considerations

#### Data Usage

- **Email Content**: Processed for analysis but not stored permanently
- **AI Processing**: Content sent to Azure OpenAI for analysis
- **Metadata**: Connection and usage statistics collected locally
- **No Third-party Sharing**: Data not shared with unauthorized parties

#### User Control

- **Opt-out Options**: Disable AI features if privacy-sensitive
- **Local Mode**: Run without cloud AI services
- **Data Deletion**: Clear all data when desired
- **Consent Management**: Clear disclosure of data usage

### Best Practices

#### Security Recommendations

1. **Strong Passwords**
   - Use app-specific passwords for email accounts
   - Regularly rotate API keys and passwords
   - Enable 2-factor authentication where possible

2. **Network Security**
   - Use secure networks for sensitive operations
   - Avoid public WiFi for email access
   - Consider VPN for enhanced privacy

3. **Regular Updates**
   - Keep NimbusRelay updated to latest version
   - Update Python and dependencies regularly
   - Monitor security advisories

#### Privacy Best Practices

1. **Minimize Data Sharing**
   - Only configure necessary services
   - Review privacy settings regularly
   - Understand data flow and usage

2. **Access Control**
   - Secure the device running NimbusRelay
   - Use browser security features
   - Log out when finished

---

## FAQ

### General Questions

**Q: What makes NimbusRelay different from other email clients?**
A: NimbusRelay combines traditional email management with advanced AI capabilities, providing intelligent analysis, spam detection, and composition assistance in a modern web interface.

**Q: Do I need an Azure OpenAI account?**
A: Yes, NimbusRelay requires Azure OpenAI services for AI-powered features. You can still use basic email functionality without AI services.

**Q: Can I use NimbusRelay with any email provider?**
A: Yes, NimbusRelay works with any email provider that supports IMAP and SMTP protocols, including Gmail, Outlook, Yahoo, and custom email servers.

**Q: Is my email data secure?**
A: Yes, NimbusRelay uses encrypted connections and processes data locally when possible. AI analysis is performed using secure Azure services.

### Technical Questions

**Q: What browsers are supported?**
A: NimbusRelay works with all modern browsers including Chrome, Firefox, Safari, and Edge. JavaScript must be enabled.

**Q: Can I run NimbusRelay on a server?**
A: Yes, NimbusRelay can be deployed on any server that supports Python and web applications. Configure the host and port settings accordingly.

**Q: How do I backup my configuration?**
A: Configuration is stored in the `.env` file. Back up this file to preserve your settings.

**Q: Can multiple users use the same NimbusRelay instance?**
A: Currently, NimbusRelay is designed for single-user use. Each user should run their own instance with their own configuration.

### Troubleshooting Questions

**Q: Why isn't AI analysis working?**
A: Check your Azure OpenAI configuration, verify your API key, and ensure you have sufficient quota. Network connectivity to Azure services is also required.

**Q: Email sync is slow. How can I improve performance?**
A: Reduce the number of emails fetched per folder, ensure good network connectivity, and consider the email server's rate limits.

**Q: Can I use NimbusRelay offline?**
A: Basic email reading of previously downloaded messages is possible offline, but live sync and AI features require internet connectivity.

**Q: How do I report bugs or request features?**
A: Check the project documentation for bug reporting procedures and feature request processes.

### Advanced Questions

**Q: Can I customize the AI prompts?**
A: Advanced users can modify the prompt templates in the `prompts/` folder to customize AI behavior.

**Q: How do I integrate NimbusRelay with other tools?**
A: NimbusRelay provides a REST API that can be integrated with other applications. See the API documentation for details.

**Q: Can I extend NimbusRelay's functionality?**
A: Yes, NimbusRelay is designed with modular architecture. Developers can add new services, routes, and features following the established patterns.

---

## Support and Resources

### Getting Help

- **Documentation**: Comprehensive guides in the `docs/` folder
- **Configuration Guide**: Step-by-step setup instructions
- **Troubleshooting**: Common issues and solutions
- **FAQ**: Frequently asked questions

### Community and Development

- **Source Code**: Available for review and contribution
- **Bug Reports**: Report issues through proper channels
- **Feature Requests**: Suggest improvements and new features
- **Contributing**: Guidelines for code contributions

### Updates and Maintenance

- **Version Updates**: Keep NimbusRelay updated for best performance
- **Security Patches**: Apply security updates promptly
- **Dependency Updates**: Regularly update Python packages
- **Configuration Reviews**: Periodically review and update settings

---

*NimbusRelay User Manual - Version 1.0*  
*Last Updated: June 26, 2025*
