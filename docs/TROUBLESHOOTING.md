# NimbusRelay Troubleshooting Guide

## Quick Diagnostic Checklist

When encountering issues with NimbusRelay, run through this checklist first:

- [ ] All required environment variables are set
- [ ] Internet connectivity is working
- [ ] Email credentials are correct (use app passwords for Gmail/Outlook)
- [ ] Azure OpenAI service is accessible and has quota
- [ ] No firewall blocking connections
- [ ] Application has necessary permissions
- [ ] Python dependencies are installed correctly

## Common Issues and Solutions

### Configuration Issues

#### "Configuration incomplete" Error

**Symptoms:**
- Cannot connect to services
- Missing configuration warning in UI
- API returns configuration errors

**Solutions:**
1. **Check Environment Variables**
   ```powershell
   # Verify .env file exists and contains all required variables
   Get-Content .env
   ```

2. **Use Configuration API**
   ```
   GET /api/config
   ```
   Review the `missing_vars` array to see what's missing.

3. **Complete Configuration**
   - Fill in all required fields in the web interface
   - Or add missing variables to your `.env` file

**Required Variables:**
```env
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_DEPLOYMENT=
IMAP_SERVER=
IMAP_USERNAME=
IMAP_PASSWORD=
SMTP_SERVER=
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_SENDER_EMAIL=
```

#### Invalid Configuration Values

**Symptoms:**
- Connection attempts fail
- "Invalid endpoint" or similar errors

**Solutions:**
1. **Azure OpenAI Endpoint Format**
   ```
   ✅ Correct: https://resource.openai.azure.com/
   ❌ Wrong: resource.openai.azure.com
   ❌ Wrong: https://resource.openai.azure.com
   ```

2. **Email Server Settings**
   - Use correct server addresses (e.g., `imap.gmail.com`, not `gmail.com`)
   - Verify port numbers (993 for IMAP, 587 for SMTP)
   - Check username format (usually full email address)

### Connection Issues

#### Cannot Connect to Email Server

**Error Messages:**
- "Failed to connect to IMAP server"
- "SMTP connection failed"
- "Authentication failed"

**Diagnosis Steps:**
1. **Test Network Connectivity**
   ```powershell
   # Test IMAP connection
   Test-NetConnection imap.gmail.com -Port 993
   
   # Test SMTP connection
   Test-NetConnection smtp.gmail.com -Port 587
   ```

2. **Verify Credentials**
   - Use app-specific passwords for Gmail/Outlook
   - Check if 2-factor authentication is properly configured
   - Verify username is complete email address

3. **Check Email Provider Settings**

   **Gmail:**
   ```env
   IMAP_SERVER=imap.gmail.com
   IMAP_PORT=993
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   ```

   **Outlook:**
   ```env
   IMAP_SERVER=outlook.office365.com
   IMAP_PORT=993
   SMTP_SERVER=smtp-mail.outlook.com
   SMTP_PORT=587
   ```

**Solutions:**
1. **Enable App Passwords**
   - Gmail: Google Account → Security → 2-Step Verification → App passwords
   - Outlook: Microsoft Account → Security → Advanced security options

2. **Check Firewall/Antivirus**
   - Allow Python.exe through firewall
   - Temporarily disable antivirus to test
   - Add exceptions for email ports (993, 587, 465)

3. **Try Alternative Ports**
   ```env
   # Alternative IMAP ports
   IMAP_PORT=143  # IMAP with STARTTLS
   
   # Alternative SMTP ports
   SMTP_PORT=465  # SMTP over SSL
   ```

#### Azure OpenAI Connection Issues

**Error Messages:**
- "AI service unavailable"
- "Azure OpenAI API error"
- "Authentication failed"

**Diagnosis Steps:**
1. **Verify Azure OpenAI Resource**
   - Check resource exists in Azure Portal
   - Verify resource is not paused or deleted
   - Confirm deployment is active

2. **Test API Manually**
   ```powershell
   # Test API endpoint
   curl -X POST "https://resource.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-12-01-preview" `
     -H "Content-Type: application/json" `
     -H "api-key: YOUR_API_KEY" `
     -d '{"messages":[{"role":"user","content":"Hello"}],"max_tokens":10}'
   ```

**Solutions:**
1. **Regenerate API Key**
   - Go to Azure Portal → Your OpenAI Resource → Keys and Endpoint
   - Regenerate key and update configuration

2. **Check Deployment Status**
   - Azure OpenAI Studio → Deployments
   - Ensure model is deployed and running

3. **Verify Quota**
   - Check usage and quotas in Azure Portal
   - Upgrade tier if necessary

4. **Update API Version**
   ```env
   AZURE_OPENAI_API_VERSION=2024-12-01-preview
   ```

### Application Issues

#### Application Won't Start

**Error Messages:**
- "Failed to start application"
- Import errors
- Port already in use

**Solutions:**
1. **Check Python Installation**
   ```powershell
   python --version
   # Should be 3.8 or higher
   ```

2. **Install Dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Check Port Availability**
   ```powershell
   # Check if port 5000 is in use
   netstat -an | findstr :5000
   
   # Kill process using port 5000 if needed
   Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess | Stop-Process
   ```

4. **Run with Different Port**
   ```powershell
   $env:PORT=5001
   python main.py
   ```

#### Web Interface Not Loading

**Symptoms:**
- Blank page in browser
- "This site can't be reached" error
- JavaScript errors in console

**Solutions:**
1. **Check Application Status**
   - Verify application is running and shows "Running on http://localhost:5000"
   - Check for error messages in console

2. **Browser Issues**
   ```
   # Clear browser cache and cookies
   # Try different browser
   # Disable browser extensions
   # Enable JavaScript
   ```

3. **Network Configuration**
   ```powershell
   # Test local connection
   Invoke-WebRequest http://localhost:5000
   ```

4. **Check Firewall**
   - Add exception for Python application
   - Allow connections on port 5000

#### WebSocket Connection Failed

**Symptoms:**
- No real-time updates
- "WebSocket connection failed" in browser console
- Features requiring live updates don't work

**Solutions:**
1. **Check WebSocket Support**
   - Modern browser required
   - JavaScript enabled
   - No proxy/VPN blocking WebSockets

2. **Firewall Configuration**
   - Allow WebSocket connections
   - Check corporate firewall settings

3. **Application Configuration**
   ```python
   # Check socketio configuration in settings
   SOCKETIO_ASYNC_MODE = 'threading'
   ```

### Performance Issues

#### Application Running Slowly

**Symptoms:**
- Slow response times
- High CPU/memory usage
- Timeouts on operations

**Solutions:**
1. **Monitor Resource Usage**
   ```powershell
   # Check memory usage
   Get-Process python | Select-Object ProcessName, WS, CPU
   ```

2. **Reduce Email Fetch Limit**
   ```
   # In API calls, reduce limit parameter
   GET /api/emails?folder=INBOX&limit=25
   ```

3. **Close Unused Applications**
   - Free up system memory
   - Close browser tabs
   - Stop unnecessary services

4. **Check Network Speed**
   ```powershell
   # Test internet speed
   Test-NetConnection 8.8.8.8
   ```

#### AI Analysis Taking Too Long

**Symptoms:**
- Long wait times for analysis results
- Timeouts on AI operations
- Slow spam detection

**Solutions:**
1. **Check Azure OpenAI Service**
   - Verify service region (closer is faster)
   - Check service tier and limits
   - Monitor quota usage

2. **Network Optimization**
   - Use wired connection instead of WiFi
   - Close bandwidth-heavy applications
   - Check for VPN/proxy delays

3. **Reduce Analysis Complexity**
   - Shorten email content if possible
   - Batch similar requests

### Email-Specific Issues

#### Emails Not Syncing

**Symptoms:**
- Old or missing emails in interface
- Folder counts incorrect
- New emails not appearing

**Solutions:**
1. **Manual Refresh**
   - Click refresh button in interface
   - Or call API endpoint: `GET /api/folder-counts`

2. **Check IMAP Permissions**
   - Verify account has IMAP access enabled
   - Check folder access permissions

3. **IMAP Connection Issues**
   ```python
   # Debug IMAP connection
   from src.email_service.imap_connection import IMAPConnectionManager
   # Check connection status
   ```

#### Cannot Send Emails

**Symptoms:**
- "Failed to send email" errors
- SMTP authentication errors
- Emails stuck in drafts

**Solutions:**
1. **Verify SMTP Configuration**
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USE_TLS=true
   ```

2. **Check Sender Permissions**
   - Verify sender email matches authenticated account
   - Check for sending limits on email provider

3. **Test SMTP Manually**
   ```python
   import smtplib
   # Test SMTP connection manually
   ```

#### Spam Detection Not Working

**Symptoms:**
- All emails marked as valid
- No spam analysis results
- Incorrect spam classifications

**Solutions:**
1. **Verify AI Service**
   - Check Azure OpenAI connection
   - Verify spam analysis prompt is loaded

2. **Check Email Headers**
   - Ensure email headers are available
   - Verify SPF/DKIM/DMARC data

3. **Manual Classification**
   - Use manual spam marking to train system
   - Review spam detection rules

## Debug Mode

### Enable Debug Logging

1. **Environment Variable**
   ```env
   DEBUG=true
   FLASK_ENV=development
   ```

2. **Restart Application**
   ```powershell
   python main.py
   ```

3. **Monitor Console Output**
   - Look for detailed error messages
   - Note API call logs
   - Check database queries

### Browser Developer Tools

1. **Open Developer Tools**
   - Press F12 in browser
   - Or right-click → Inspect

2. **Check Console Tab**
   - Look for JavaScript errors
   - Note network request failures
   - Check WebSocket connection status

3. **Network Tab**
   - Monitor API calls
   - Check response times
   - Verify request/response formats

### Log Files

#### Application Logs
```powershell
# Check console output for errors
# Look for patterns in error messages
# Note timestamps of issues
```

#### System Logs
```powershell
# Windows Event Viewer
# Check Application and System logs
# Look for Python or network-related errors
```

## Advanced Troubleshooting

### Database Issues

If using persistent storage:

1. **Check Database Connection**
2. **Verify Schema**
3. **Check Permissions**
4. **Clear Cache/Temporary Data**

### Network Diagnostics

```powershell
# Test DNS resolution
nslookup imap.gmail.com

# Test port connectivity
Test-NetConnection imap.gmail.com -Port 993 -InformationLevel Detailed

# Check routing
tracert imap.gmail.com

# Test HTTPS connectivity
Invoke-WebRequest https://your-resource.openai.azure.com
```

### Memory Issues

```powershell
# Monitor memory usage
Get-Process python | Select-Object ProcessName, WS, PagedMemorySize

# Check available memory
Get-WmiObject -Class Win32_OperatingSystem | Select-Object TotalVisibleMemorySize, FreePhysicalMemory
```

### Security Software Interference

1. **Antivirus Exceptions**
   - Add Python.exe to exceptions
   - Add application folder to exceptions
   - Allow network connections

2. **Firewall Rules**
   - Allow inbound connections on port 5000
   - Allow outbound connections to email servers
   - Allow HTTPS connections to Azure

## Getting Support

### Information to Collect

When seeking support, gather:

1. **System Information**
   - Operating system version
   - Python version
   - Browser and version

2. **Error Details**
   - Complete error messages
   - Console output
   - Browser developer tools output

3. **Configuration**
   - Sanitized configuration (no passwords/keys)
   - Email provider information
   - Azure OpenAI service details

4. **Steps to Reproduce**
   - Detailed steps that cause the issue
   - Expected vs actual behavior
   - Frequency of occurrence

### Support Channels

1. **Documentation Review**
   - Check User Manual
   - Review Configuration Guide
   - Browse FAQ section

2. **Community Support**
   - Check project documentation
   - Search existing issues
   - Community forums

3. **Bug Reports**
   - Include all collected information
   - Provide clear reproduction steps
   - Attach relevant logs (sanitized)

---

This troubleshooting guide covers the most common issues encountered with NimbusRelay. For issues not covered here, refer to the complete documentation or seek community support.
