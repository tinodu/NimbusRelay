# NimbusRelay Quick Start Guide

## 🚀 Get Up and Running in 5 Minutes

### Prerequisites
- Python 3.8 or higher installed
- Modern web browser
- Internet connection
- Email account with IMAP/SMTP access

### Step 1: Installation
```powershell
# Navigate to NimbusRelay directory
cd C:\path\to\NimbusRelay

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Basic Configuration
Create a `.env` file in the root directory with your settings:

```env
# Azure OpenAI (Required for AI features)
AZURE_OPENAI_ENDPOINT=your-endpoint
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o

# Gmail Example
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
IMAP_USERNAME=your-email@gmail.com
IMAP_PASSWORD=your-app-password

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_SENDER_EMAIL=your-email@gmail.com
```

### Step 3: Launch Application
```powershell
python main.py
```
Or double-click `start.bat`

### Step 4: Access Web Interface
1. Open browser to `http://localhost:5000`
2. Complete configuration if not using .env file
3. Click "Connect Services"
4. Start managing your emails!

## 🎯 First Steps

### 1. Test Connection
- Click "Connect Services" button
- Verify both email and AI services connect successfully
- Check for any error messages

### 2. Explore Your Inbox
- Browse folders in the left sidebar
- Click on any email to read it
- Notice the AI analysis panel on the right

### 3. Try AI Features
- Select any email
- View the automatic content analysis
- Try the spam detection on suspicious emails
- Use the compose assistant for new emails

### 4. Customize Your Experience
- Adjust folder visibility settings
- Explore different email views
- Set up filters and search preferences

## 📧 Email Provider Setup

### Gmail Setup
1. **Enable 2-Factor Authentication**
2. **Generate App Password**:
   - Google Account → Security → 2-Step Verification → App passwords
   - Select "Mail" and generate password
   - Use this password in NimbusRelay (not your regular Gmail password)

### Outlook/Hotmail Setup
1. **Enable App Password**:
   - Microsoft Account → Security → Advanced security options
   - Generate app password for email
2. **Use App Password** in NimbusRelay configuration

### Other Providers
Consult your email provider's documentation for IMAP/SMTP settings and app password setup.

## 🤖 Azure OpenAI Setup

### 1. Create Azure OpenAI Resource
1. Log into Azure Portal
2. Create new "Azure OpenAI" resource
3. Note the endpoint URL and keys

### 2. Deploy a Model
1. Go to Azure OpenAI Studio
2. Deploy a GPT-4 or GPT-3.5 model
3. Note the deployment name

### 3. Configure NimbusRelay
```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-from-azure
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
```

## 🔧 Common Issues

### "Cannot connect to email server"
- ✅ Check server address and port
- ✅ Verify username/password
- ✅ Use app-specific password (not regular password)
- ✅ Check firewall settings

### "AI analysis not working"
- ✅ Verify Azure OpenAI endpoint and key
- ✅ Check deployment name
- ✅ Confirm API quota not exceeded
- ✅ Test network connectivity

### "Interface not loading"
- ✅ Clear browser cache
- ✅ Try different browser
- ✅ Check JavaScript is enabled
- ✅ Restart the application

## 🎉 You're Ready!

Congratulations! You now have NimbusRelay running with:
- ✅ Email connectivity
- ✅ AI-powered analysis
- ✅ Modern web interface
- ✅ Real-time updates

### Next Steps
- Read the full [User Manual](USER_MANUAL.md) for detailed features
- Explore the [API Documentation](API_REFERENCE.md) for advanced usage
- Check out [Configuration Guide](CONFIGURATION.md) for customization options

### Need Help?
- Review the [Troubleshooting Guide](TROUBLESHOOTING.md)
- Check the [FAQ](FAQ.md) for common questions
- Refer to the complete [User Manual](USER_MANUAL.md)

---
*Happy emailing with NimbusRelay! 🎯*
