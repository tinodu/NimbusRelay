# NimbusRelay Frequently Asked Questions (FAQ)

## General Questions

### What is NimbusRelay?

**Q: What is NimbusRelay and what does it do?**

A: NimbusRelay is an AI-powered email management system that combines traditional email client functionality with advanced artificial intelligence capabilities. It provides:

- **Intelligent Email Analysis**: Comprehensive content analysis using Azure OpenAI
- **Advanced Spam Detection**: Multi-layered spam filtering with detailed explanations
- **AI-Assisted Composition**: Help with drafting emails and responses
- **Modern Web Interface**: Clean, responsive design with real-time updates
- **Cross-Platform Access**: Web-based interface accessible from any device

### How is NimbusRelay different from other email clients?

**Q: What makes NimbusRelay unique compared to Outlook, Gmail, or Thunderbird?**

A: NimbusRelay stands out through:

1. **AI Integration**: Built-in AI analysis for every email, providing insights into content, tone, and intent
2. **Advanced Spam Detection**: Goes beyond simple filtering with detailed explanations of why emails are classified as spam
3. **Composition Assistant**: AI helps draft professional responses and suggests improvements
4. **Modern Architecture**: Web-based with real-time updates and modern UI/UX
5. **Privacy-Focused**: Processes data locally when possible, with transparent AI usage
6. **Extensible Design**: Modular architecture allows for customization and extensions

## Setup and Installation

### What do I need to run NimbusRelay?

**Q: What are the system requirements?**

A: You need:
- **Python 3.8+** installed on your system
- **Modern web browser** (Chrome, Firefox, Safari, Edge)
- **Internet connection** for email and AI services
- **Email account** with IMAP/SMTP access
- **Azure OpenAI account** (for AI features)
- **2GB RAM minimum** (4GB recommended)
- **500MB storage space**

### Do I need an Azure OpenAI account?

**Q: Is Azure OpenAI required? Can I use other AI services?**

A: Currently, NimbusRelay is designed to work with Azure OpenAI services for its AI capabilities. You can:

- **Use NimbusRelay without AI**: Basic email functionality works without Azure OpenAI
- **Azure OpenAI Required for**: Email analysis, spam detection, and composition assistance
- **Future Plans**: Support for other AI providers may be added in future versions

To get Azure OpenAI:
1. Create an Azure account
2. Request access to Azure OpenAI (may require approval)
3. Create an OpenAI resource and deploy a model

### Can I use NimbusRelay with any email provider?

**Q: What email providers are supported?**

A: NimbusRelay works with any email provider that supports **IMAP and SMTP** protocols, including:

**Fully Tested:**
- Gmail
- Microsoft Outlook/Office 365
- Yahoo Mail

**Should Work:**
- Apple iCloud Mail
- ProtonMail (with IMAP Bridge)
- Custom corporate email servers
- Other IMAP/SMTP providers

**Setup Requirements:**
- Enable IMAP access in your email settings
- Use app-specific passwords for Gmail and Outlook
- Configure correct server settings and ports

## Configuration and Security

### How do I set up app passwords for Gmail/Outlook?

**Q: Why can't I use my regular password?**

A: Gmail and Outlook require **app-specific passwords** for security when accessing email through third-party applications.

**Gmail Setup:**
1. Enable 2-Factor Authentication in Google Account
2. Go to Google Account → Security → 2-Step Verification
3. Scroll to "App passwords" and click it
4. Select "Mail" and generate a password
5. Use this 16-character password in NimbusRelay (not your regular Gmail password)

**Outlook Setup:**
1. Go to Microsoft Account security settings
2. Enable App passwords under Advanced security options
3. Generate an app password for email
4. Use this password in NimbusRelay

### Is my email data secure?

**Q: What happens to my email data? Is it private?**

A: NimbusRelay takes privacy seriously:

**Data Processing:**
- Emails are processed **locally** when possible
- AI analysis sends content to **Azure OpenAI** (Microsoft's secure service)
- No permanent storage of email content on local system
- Credentials stored as **environment variables** (not in code)

**Security Measures:**
- All email connections use **TLS/SSL encryption**
- API communications are **encrypted**
- No data sharing with unauthorized third parties
- You control all configuration and data

**Your Control:**
- Disable AI features if privacy-sensitive
- Use only local email processing
- Delete all data when desired
- Full transparency in data usage

### Can I run NimbusRelay without internet?

**Q: Does NimbusRelay work offline?**

A: **Limited offline functionality:**

**Works Offline:**
- Reading previously downloaded emails
- Basic interface navigation
- Local email search (cached emails)

**Requires Internet:**
- Syncing new emails (IMAP connection)
- Sending emails (SMTP connection)
- AI analysis and spam detection
- Real-time updates

**Recommendation:** Use with stable internet connection for full functionality.

## Features and Usage

### How does the AI email analysis work?

**Q: What kind of analysis does the AI provide?**

A: NimbusRelay's AI analysis includes:

**Content Analysis:**
- **Summary**: Key points and main message
- **Tone Detection**: Formal, casual, urgent, friendly, etc.
- **Sentiment Analysis**: Positive, neutral, or negative
- **Intent Recognition**: Meeting request, information request, complaint, etc.

**Actionable Insights:**
- **Action Items**: Tasks or follow-ups required
- **Key Information**: Important dates, names, deadlines
- **Response Suggestions**: Whether and how to respond
- **Priority Assessment**: Urgency and importance levels

**Use Cases:**
- Quickly understand email content without reading in detail
- Identify important emails that need immediate attention
- Get help deciding how to respond
- Extract key information for follow-up

### How accurate is the spam detection?

**Q: How reliable is the AI spam filtering?**

A: NimbusRelay uses **multi-layered spam detection** with high accuracy:

**Detection Methods:**
- **Header Analysis**: SPF, DKIM, DMARC authentication
- **Content Analysis**: Language patterns, trigger words
- **Sender Reputation**: Domain and IP reputation
- **Behavioral Analysis**: Mass distribution patterns

**Accuracy:**
- **High Precision**: Low false positives (legitimate emails marked as spam)
- **Good Recall**: Catches most spam emails
- **Detailed Explanations**: Shows why emails are classified as spam
- **Learning Capability**: Improves with manual corrections

**What You Get:**
- Clear "Spam/Junk" or "Valid" classification
- Confidence score (0-100%)
- Detailed explanation of decision factors
- Specific risk factors identified
- Recommended actions

### Can I customize the AI prompts?

**Q: Can I modify how the AI analyzes emails?**

A: **Advanced users** can customize AI behavior:

**What Can Be Customized:**
- Email analysis prompts (in `prompts/email-analyze.md`)
- Spam detection criteria (in `prompts/email-spam.md`)
- Draft assistance templates (in `prompts/email-draft.md`)

**How to Customize:**
1. Edit the markdown files in the `prompts/` folder
2. Modify the instructions and criteria
3. Restart NimbusRelay to apply changes

**Caution:**
- Backup original prompts before editing
- Test changes with sample emails
- Poor prompts can reduce AI accuracy
- Technical knowledge recommended

## Technical Questions

### Can multiple users use the same NimbusRelay instance?

**Q: Is NimbusRelay multi-user?**

A: **Currently single-user designed:**

- Each NimbusRelay instance connects to **one email account**
- Configuration is **per-instance**, not per-user
- No user authentication or session management

**For Multiple Users:**
- Run **separate instances** for each user
- Each user needs their own configuration
- Use different ports for each instance (5000, 5001, 5002, etc.)

**Future Considerations:**
- Multi-user support may be added in future versions
- Enterprise features under consideration

### Can I integrate NimbusRelay with other applications?

**Q: Does NimbusRelay have an API for integration?**

A: **Yes!** NimbusRelay provides a comprehensive **REST API**:

**Available Endpoints:**
- Email management (read, send, organize)
- AI analysis and spam detection
- Configuration management
- Real-time WebSocket updates

**Common Integrations:**
- Custom dashboards and reports
- Automated email processing workflows
- Integration with CRM systems
- Custom AI analysis applications

**Documentation:**
- Complete API reference in `docs/API_REFERENCE.md`
- Example code in JavaScript and Python
- WebSocket event documentation

### Can I run NimbusRelay on a server?

**Q: Can I deploy NimbusRelay for remote access?**

A: **Yes**, NimbusRelay can be deployed on servers:

**Deployment Options:**
- Windows/Linux servers
- Cloud instances (AWS, Azure, Google Cloud)
- Docker containers (configuration required)
- Local network servers

**Configuration Changes:**
```python
# Change host and port in configuration
app.run(host='0.0.0.0', port=5000)
```

**Security Considerations:**
- Use HTTPS in production
- Configure proper firewall rules
- Secure environment variable storage
- Regular security updates

### How do I backup my configuration?

**Q: How do I save my NimbusRelay settings?**

A: **Configuration backup is simple:**

**Method 1: Environment File**
```powershell
# Backup your .env file
Copy-Item .env .env.backup
```

**Method 2: Export Settings**
```powershell
# Save all environment variables
$env:* | Out-File env-backup.txt
```

**What to Backup:**
- `.env` file (contains all configuration)
- Custom prompt files (if modified)
- Any custom configuration files

**Restore Process:**
1. Copy `.env` file to new installation
2. Install dependencies: `pip install -r requirements.txt`
3. Run application: `python main.py`

## Troubleshooting

### Why isn't the AI analysis working?

**Q: I'm not getting AI analysis results. What's wrong?**

A: **Common causes and solutions:**

1. **Azure OpenAI Configuration**
   - Check endpoint URL format: `https://resource.openai.azure.com/`
   - Verify API key is correct and active
   - Confirm deployment name matches Azure OpenAI Studio
   - Check API version compatibility

2. **Network Issues**
   - Test internet connectivity
   - Check firewall blocking HTTPS connections
   - Verify no proxy/VPN interference

3. **Service Limits**
   - Check Azure OpenAI quota usage
   - Verify service is not paused or suspended
   - Consider upgrading service tier

4. **Configuration Test**
   ```
   GET /api/config
   ```
   Check for missing Azure OpenAI configuration.

### Why are emails not syncing?

**Q: I don't see new emails or folders are empty.**

A: **Troubleshooting steps:**

1. **Connection Issues**
   - Verify IMAP server settings
   - Check username/password (use app passwords)
   - Test network connectivity to email server

2. **Account Settings**
   - Ensure IMAP is enabled in email account
   - Check folder access permissions
   - Verify account is not locked or suspended

3. **Application Issues**
   - Restart NimbusRelay
   - Check for error messages in console
   - Try manual refresh in interface

4. **Server Limits**
   - Some providers limit IMAP connections
   - Check for rate limiting
   - Verify account is in good standing

### The interface won't load. What should I do?

**Q: I get a blank page or connection error.**

A: **Step-by-step troubleshooting:**

1. **Check Application Status**
   ```powershell
   # Verify application is running
   # Look for "Running on http://localhost:5000" message
   ```

2. **Test Connection**
   ```powershell
   # Try accessing directly
   Invoke-WebRequest http://localhost:5000
   ```

3. **Browser Issues**
   - Clear browser cache and cookies
   - Try different browser
   - Disable browser extensions
   - Ensure JavaScript is enabled

4. **Port Conflicts**
   ```powershell
   # Check if port 5000 is available
   netstat -an | findstr :5000
   ```

5. **Firewall Settings**
   - Allow Python.exe through firewall
   - Add exception for port 5000
   - Temporarily disable firewall to test

## Performance and Optimization

### NimbusRelay is running slowly. How can I improve performance?

**Q: The application feels sluggish. What can I do?**

A: **Performance optimization:**

1. **Reduce Email Load**
   - Decrease email fetch limit (25 instead of 50)
   - Archive old emails
   - Use specific folder searches instead of "All"

2. **System Resources**
   - Close unnecessary applications
   - Ensure adequate RAM (4GB+ recommended)
   - Use SSD storage if possible

3. **Network Optimization**
   - Use wired connection instead of WiFi
   - Check internet speed
   - Close bandwidth-heavy applications

4. **AI Service Optimization**
   - Choose Azure OpenAI region closer to you
   - Consider higher service tier for better performance
   - Batch similar requests when possible

### How much does it cost to run NimbusRelay?

**Q: What are the ongoing costs?**

A: **Cost breakdown:**

**Free Components:**
- NimbusRelay software (open source)
- Email access (using existing accounts)
- Basic hosting/server costs

**Paid Components:**
- **Azure OpenAI Service**: Pay-per-use pricing
  - Typically $0.002-0.060 per 1K tokens
  - Average email analysis: ~$0.01-0.05 per email
  - Monthly cost depends on usage volume

**Estimation Examples:**
- **Light Usage** (50 analyses/day): ~$15-75/month
- **Medium Usage** (200 analyses/day): ~$60-300/month
- **Heavy Usage** (500 analyses/day): ~$150-750/month

**Cost Optimization:**
- Use AI analysis selectively
- Choose appropriate Azure OpenAI tier
- Monitor usage in Azure Portal
- Consider usage quotas and limits

## Future Development

### What features are planned for future releases?

**Q: What's on the roadmap?**

A: **Potential future features** (not guaranteed):

**Enhanced AI Capabilities:**
- Support for additional AI providers (OpenAI, Anthropic)
- Custom AI model training
- Advanced email automation
- Smart email categorization

**User Experience:**
- Mobile-responsive design improvements
- Offline mode enhancements
- Customizable themes and layouts
- Advanced search and filtering

**Enterprise Features:**
- Multi-user support
- Role-based access control
- Audit logging and compliance
- Integration with enterprise systems

**Technical Improvements:**
- Performance optimizations
- Database storage options
- Enhanced security features
- Plugin/extension system

### How can I contribute to NimbusRelay?

**Q: Can I help improve NimbusRelay?**

A: **Contribution opportunities:**

**For Users:**
- Report bugs and issues
- Suggest new features
- Provide feedback on usability
- Test new releases

**For Developers:**
- Submit bug fixes
- Develop new features
- Improve documentation
- Create integrations and extensions

**For Technical Writers:**
- Improve documentation
- Create tutorials and guides
- Translate to other languages
- Write blog posts and articles

**Getting Started:**
1. Review the project structure and code
2. Check existing issues and feature requests
3. Follow contribution guidelines
4. Submit pull requests for improvements

---

## Still Have Questions?

If your question isn't answered here:

1. **Check the Documentation**
   - [User Manual](USER_MANUAL.md) - Comprehensive guide
   - [Configuration Guide](CONFIGURATION.md) - Detailed setup instructions
   - [Troubleshooting Guide](TROUBLESHOOTING.md) - Common issues and solutions

2. **Review the Code**
   - Browse the source code for technical details
   - Check existing issues and discussions
   - Look for similar questions

3. **Seek Community Support**
   - Join community forums or discussions
   - Ask questions with detailed information
   - Share your use case and requirements

4. **Submit Feedback**
   - Report bugs with detailed steps to reproduce
   - Suggest improvements with clear descriptions
   - Provide feedback on documentation quality

---

*This FAQ is regularly updated based on user questions and feedback. Last updated: June 26, 2025*
