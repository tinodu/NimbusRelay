# NimbusRelay Configuration Guide

## Overview

This guide provides detailed information about configuring NimbusRelay for optimal performance with your email provider and Azure OpenAI services.

## Configuration Methods

### 1. Environment Variables (.env file)
The recommended method for production use.

### 2. Web Interface Configuration
User-friendly method for initial setup and testing.

### 3. Environment Variables (System)
For system-wide or server deployments.

## Detailed Configuration Parameters

### Azure OpenAI Configuration

#### AZURE_OPENAI_ENDPOINT
- **Description**: The endpoint URL for your Azure OpenAI resource
- **Format**: `https://<resource-name>.openai.azure.com/`
- **Example**: `https://mycompany-openai.openai.azure.com/`
- **Required**: Yes (for AI features)
- **How to find**: Azure Portal → Your OpenAI Resource → Keys and Endpoint

#### AZURE_OPENAI_API_KEY
- **Description**: API key for authentication with Azure OpenAI
- **Format**: 32-character alphanumeric string
- **Example**: `1234567890abcdef1234567890abcdef`
- **Required**: Yes (for AI features)
- **Security**: Keep this secret, never commit to version control
- **How to find**: Azure Portal → Your OpenAI Resource → Keys and Endpoint

#### AZURE_OPENAI_DEPLOYMENT
- **Description**: Name of your deployed model
- **Common Values**: `gpt-4o`, `gpt-4`, `gpt-35-turbo`
- **Example**: `gpt-4o`
- **Required**: Yes (for AI features)
- **How to find**: Azure OpenAI Studio → Deployments

#### AZURE_OPENAI_API_VERSION
- **Description**: API version to use
- **Default**: `2024-12-01-preview`
- **Format**: `YYYY-MM-DD-preview` or `YYYY-MM-DD`
- **Example**: `2024-12-01-preview`
- **Required**: No (uses default if not specified)

### IMAP Configuration (Incoming Mail)

#### IMAP_SERVER
- **Description**: IMAP server hostname
- **Examples**:
  - Gmail: `imap.gmail.com`
  - Outlook: `outlook.office365.com`
  - Yahoo: `imap.mail.yahoo.com`
- **Required**: Yes
- **Format**: Hostname or IP address

#### IMAP_PORT
- **Description**: IMAP server port
- **Common Values**:
  - `993` (IMAP over SSL/TLS - recommended)
  - `143` (IMAP with STARTTLS)
- **Default**: `993`
- **Required**: No (uses default if not specified)

#### IMAP_USERNAME
- **Description**: Username for IMAP authentication
- **Format**: Usually your full email address
- **Example**: `john.doe@company.com`
- **Required**: Yes

#### IMAP_PASSWORD
- **Description**: Password for IMAP authentication
- **Important**: Use app-specific passwords for Gmail/Outlook
- **Security**: Store securely, never commit to version control
- **Required**: Yes

### SMTP Configuration (Outgoing Mail)

#### SMTP_SERVER
- **Description**: SMTP server hostname
- **Examples**:
  - Gmail: `smtp.gmail.com`
  - Outlook: `smtp-mail.outlook.com`
  - Yahoo: `smtp.mail.yahoo.com`
- **Required**: Yes (for sending emails)

#### SMTP_PORT
- **Description**: SMTP server port
- **Common Values**:
  - `587` (SMTP with STARTTLS - recommended)
  - `465` (SMTP over SSL/TLS)
  - `25` (Plain SMTP - not recommended)
- **Default**: `587`
- **Required**: No (uses default if not specified)

#### SMTP_USERNAME
- **Description**: Username for SMTP authentication
- **Format**: Usually your full email address
- **Example**: `john.doe@company.com`
- **Required**: Yes (for sending emails)

#### SMTP_PASSWORD
- **Description**: Password for SMTP authentication
- **Important**: Use app-specific passwords for Gmail/Outlook
- **Required**: Yes (for sending emails)

#### SMTP_SENDER_EMAIL
- **Description**: Email address to use as sender
- **Format**: Valid email address
- **Example**: `john.doe@company.com`
- **Required**: Yes (for sending emails)

#### SMTP_USE_TLS
- **Description**: Enable TLS encryption for SMTP
- **Values**: `true`, `false`
- **Default**: `true`
- **Recommended**: `true` for security
- **Required**: No

## Email Provider Specific Settings

### Gmail Configuration

#### Prerequisites
1. Enable 2-Factor Authentication
2. Generate App Password

#### Settings
```env
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
IMAP_USERNAME=your-email@gmail.com
SMTP_USERNAME=your-email@gmail.com
IMAP_PASSWORD=your-app-password
SMTP_PASSWORD=your-app-password
SMTP_SENDER_EMAIL=your-email@gmail.com
SMTP_USE_TLS=true
```

#### App Password Setup
1. Google Account → Security → 2-Step Verification
2. App passwords → Generate password for "Mail"
3. Use generated password (not your regular Gmail password)

### Microsoft Outlook/Office 365

#### Prerequisites
1. Enable App Passwords (if using personal account)
2. For business accounts, use regular credentials

#### Settings
```env
IMAP_SERVER=outlook.office365.com
IMAP_PORT=993
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
IMAP_USERNAME=your-email@outlook.com
SMTP_USERNAME=your-email@outlook.com
IMAP_PASSWORD=your-password-or-app-password
SMTP_PASSWORD=your-password-or-app-password
SMTP_SENDER_EMAIL=your-email@outlook.com
SMTP_USE_TLS=true
```

### Yahoo Mail

#### Prerequisites
1. Enable App Passwords in Yahoo Account Security
2. Generate App Password for email access

#### Settings
```env
IMAP_SERVER=imap.mail.yahoo.com
IMAP_PORT=993
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
IMAP_USERNAME=your-email@yahoo.com
SMTP_USERNAME=your-email@yahoo.com
IMAP_PASSWORD=your-app-password
SMTP_PASSWORD=your-app-password
SMTP_SENDER_EMAIL=your-email@yahoo.com
SMTP_USE_TLS=true
```

### Custom/Corporate Email

#### Common Settings
For custom email servers, contact your IT administrator for:
- IMAP/SMTP server addresses
- Port numbers
- Authentication requirements
- Security settings (TLS/SSL)

#### Typical Configuration
```env
IMAP_SERVER=mail.yourcompany.com
IMAP_PORT=993
SMTP_SERVER=mail.yourcompany.com
SMTP_PORT=587
IMAP_USERNAME=your-username
SMTP_USERNAME=your-username
IMAP_PASSWORD=your-password
SMTP_PASSWORD=your-password
SMTP_SENDER_EMAIL=your-email@yourcompany.com
SMTP_USE_TLS=true
```

## Configuration File Examples

### Complete .env File Example

```env
# Application Configuration
SECRET_KEY=your-secret-key-for-flask-sessions

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-32-character-api-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# IMAP Configuration (Incoming Mail)
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
IMAP_USERNAME=your-email@gmail.com
IMAP_PASSWORD=your-16-character-app-password

# SMTP Configuration (Outgoing Mail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-character-app-password
SMTP_SENDER_EMAIL=your-email@gmail.com
SMTP_USE_TLS=true
```

### Development vs Production Configuration

#### Development (.env.development)
```env
# Development-specific settings
DEBUG=true
FLASK_ENV=development

# Use development Azure OpenAI resource
AZURE_OPENAI_ENDPOINT=https://dev-openai.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-35-turbo

# Test email account
IMAP_USERNAME=test@example.com
SMTP_SENDER_EMAIL=test@example.com
```

#### Production (.env.production)
```env
# Production settings
DEBUG=false
FLASK_ENV=production

# Production Azure OpenAI resource
AZURE_OPENAI_ENDPOINT=https://prod-openai.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o

# Production email account
IMAP_USERNAME=noreply@yourcompany.com
SMTP_SENDER_EMAIL=noreply@yourcompany.com
```

## Configuration Validation

### Testing Your Configuration

1. **Use Web Interface Validation**
   - Navigate to `http://localhost:5000`
   - Go to Configuration section
   - Click "Connect Services"
   - Review connection results

2. **Check Configuration Status**
   ```
   GET /api/config
   ```
   Returns configuration status and missing variables

3. **Manual Testing**
   ```python
   from src.config.settings import Config
   env_vars = Config.get_required_env_vars()
   missing = [k for k, v in env_vars.items() if not v]
   print(f"Missing variables: {missing}")
   ```

### Common Configuration Errors

#### "Configuration incomplete"
- **Cause**: Required environment variables not set
- **Solution**: Ensure all required variables have values
- **Check**: Use `/api/config` endpoint to see missing variables

#### "Invalid Azure OpenAI endpoint"
- **Cause**: Malformed endpoint URL
- **Solution**: Ensure URL starts with `https://` and ends with `/`
- **Example**: `https://resource.openai.azure.com/`

#### "IMAP authentication failed"
- **Cause**: Incorrect username/password or server settings
- **Solutions**:
  - Use app-specific passwords for Gmail/Outlook
  - Verify server address and port
  - Check 2-factor authentication settings

#### "SMTP connection failed"
- **Cause**: Incorrect SMTP settings or authentication
- **Solutions**:
  - Verify SMTP server and port
  - Ensure TLS settings match server requirements
  - Check authentication credentials

## Security Best Practices

### Environment Variable Security

1. **Never Commit Secrets**
   - Add `.env` to `.gitignore`
   - Use separate files for different environments
   - Rotate keys regularly

2. **Use App-Specific Passwords**
   - Enable 2FA on email accounts
   - Generate dedicated app passwords
   - Revoke unused app passwords

3. **Secure Storage**
   - Use environment variable managers
   - Encrypt configuration files
   - Limit file permissions (chmod 600)

### Network Security

1. **Use Encrypted Connections**
   - Always use TLS/SSL for email
   - Verify certificate validation
   - Use secure ports (993, 587)

2. **Firewall Configuration**
   - Allow outbound connections to email servers
   - Allow outbound HTTPS for Azure OpenAI
   - Restrict inbound access to application port

## Advanced Configuration

### Custom Configuration Sources

#### Database Configuration
For enterprise deployments, configuration can be stored in databases:

```python
# Custom configuration loader
from src.config.settings import Config

class DatabaseConfig(Config):
    @classmethod
    def load_from_database(cls):
        # Implementation for loading from database
        pass
```

#### Azure Key Vault Integration
For Azure deployments:

```python
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

def load_from_keyvault():
    client = SecretClient(
        vault_url="https://vault.vault.azure.net/",
        credential=DefaultAzureCredential()
    )
    # Load secrets from Key Vault
```

### Environment-Specific Configuration

#### Using Configuration Profiles
```bash
# Set environment
export FLASK_ENV=production

# Application will load appropriate configuration
python main.py
```

#### Configuration Inheritance
```python
class StagingConfig(ProductionConfig):
    """Staging inherits from production with overrides"""
    DEBUG = True
    AZURE_OPENAI_DEPLOYMENT = "gpt-35-turbo"
```

## Troubleshooting Configuration

### Configuration Checklist

- [ ] All required environment variables set
- [ ] Email credentials are app-specific passwords
- [ ] Azure OpenAI endpoint includes protocol and trailing slash
- [ ] API key is valid and has sufficient quota
- [ ] Deployment name matches Azure OpenAI Studio
- [ ] Network allows connections to email and Azure services
- [ ] Firewall/antivirus not blocking connections
- [ ] Environment file has correct permissions
- [ ] No trailing spaces in configuration values

### Debug Configuration Issues

1. **Enable Debug Logging**
   ```env
   DEBUG=true
   ```

2. **Test Individual Components**
   ```python
   # Test email connection only
   from src.email_service.imap_connection import IMAPConnectionManager
   # Test AI service only
   from src.ai.azure_service import AzureOpenAIService
   ```

3. **Use Configuration Endpoint**
   ```
   GET /api/config
   ```
   Provides detailed configuration status

4. **Check Application Logs**
   Monitor console output for configuration-related errors

---

This configuration guide should help you set up NimbusRelay for your specific environment and requirements. For additional help, refer to the troubleshooting section or the main user manual.
