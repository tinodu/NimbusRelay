# NimbusRelay API Reference

## Overview

NimbusRelay provides a comprehensive REST API for email management and AI-powered analysis. This document covers all available endpoints, request/response formats, and usage examples.

## Base URL

```
http://localhost:5000/api
```

## Authentication

Currently, NimbusRelay uses session-based authentication. Email and AI service credentials are configured through environment variables or the configuration API.

## Content Types

- **Request Content-Type**: `application/json`
- **Response Content-Type**: `application/json`

## Error Handling

All API endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "Error description",
  "code": "ERROR_CODE"
}
```

## Configuration Endpoints

### Get Configuration Status

Retrieve current configuration status and missing variables.

```http
GET /api/config
```

**Response:**
```json
{
  "configured": true,
  "missing_vars": [],
  "current_config": {
    "AZURE_OPENAI_ENDPOINT": true,
    "AZURE_OPENAI_API_KEY": true,
    "IMAP_SERVER": true,
    "IMAP_USERNAME": true
  },
  "values": {
    "AZURE_OPENAI_ENDPOINT": "https://resource.openai.azure.com/",
    "AZURE_OPENAI_API_KEY": "****",
    "IMAP_SERVER": "imap.gmail.com"
  }
}
```

### Save Configuration

Save configuration parameters to environment.

```http
POST /api/config
Content-Type: application/json
```

**Request Body:**
```json
{
  "AZURE_OPENAI_ENDPOINT": "https://resource.openai.azure.com/",
  "AZURE_OPENAI_API_KEY": "your-api-key",
  "AZURE_OPENAI_DEPLOYMENT": "gpt-4o",
  "IMAP_SERVER": "imap.gmail.com",
  "IMAP_USERNAME": "user@gmail.com",
  "IMAP_PASSWORD": "app-password"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Configuration saved successfully"
}
```

## Connection Management

### Connect Services

Establish connections to email and AI services.

```http
POST /api/connect
```

**Response:**
```json
{
  "success": true,
  "message": "All services connected successfully",
  "services": {
    "email": {
      "connected": true,
      "status": "Connected to imap.gmail.com"
    },
    "ai": {
      "connected": true,
      "status": "Connected to Azure OpenAI"
    }
  }
}
```

### Disconnect Services

Disconnect from email and AI services.

```http
POST /api/disconnect
```

**Response:**
```json
{
  "status": "disconnected"
}
```

## Folder Management

### List Email Folders

Retrieve list of available email folders.

```http
GET /api/folders?include_hidden=false
```

**Query Parameters:**
- `include_hidden` (boolean, optional): Include system/hidden folders. Default: `false`

**Response:**
```json
{
  "success": true,
  "folders": [
    {
      "name": "INBOX",
      "display_name": "Inbox",
      "type": "inbox",
      "selectable": true
    },
    {
      "name": "Sent",
      "display_name": "Sent",
      "type": "sent",
      "selectable": true
    }
  ]
}
```

### Get Folder Counts

Retrieve message counts for all folders.

```http
GET /api/folder-counts
```

**Response:**
```json
{
  "success": true,
  "counts": {
    "INBOX": {
      "total": 150,
      "unread": 12,
      "recent": 5
    },
    "Sent": {
      "total": 45,
      "unread": 0,
      "recent": 0
    }
  }
}
```

## Email Management

### Get Emails

Retrieve emails from specified folder.

```http
GET /api/emails?folder=INBOX&limit=50
```

**Query Parameters:**
- `folder` (string, optional): Folder name. Default: `INBOX`
- `limit` (integer, optional): Maximum number of emails to retrieve. Default: `50`

**Response:**
```json
{
  "success": true,
  "emails": [
    {
      "id": "12345",
      "uid": "67890",
      "subject": "Meeting Tomorrow",
      "from": "john@example.com",
      "to": ["user@gmail.com"],
      "date": "2025-06-26T10:30:00Z",
      "body": "Email body content...",
      "html_body": "<p>Email HTML content...</p>",
      "attachments": [],
      "flags": ["\\Seen"],
      "size": 1024
    }
  ],
  "folder": "INBOX",
  "total_count": 150
}
```

### Get Single Email

Retrieve details of a specific email.

```http
GET /api/email/{email_id}?folder=INBOX
```

**Path Parameters:**
- `email_id` (string): Email ID or UID

**Query Parameters:**
- `folder` (string, optional): Folder containing the email. Default: `INBOX`

**Response:**
```json
{
  "success": true,
  "email": {
    "id": "12345",
    "uid": "67890",
    "subject": "Meeting Tomorrow",
    "from": "john@example.com",
    "to": ["user@gmail.com"],
    "cc": [],
    "bcc": [],
    "reply_to": "john@example.com",
    "date": "2025-06-26T10:30:00Z",
    "body": "Email body content...",
    "html_body": "<p>Email HTML content...</p>",
    "headers": {
      "Message-ID": "<message-id@example.com>",
      "Return-Path": "john@example.com"
    },
    "attachments": [],
    "flags": ["\\Seen"],
    "size": 1024
  }
}
```

## AI Analysis

### Analyze Email Content

Perform comprehensive AI analysis of email content.

```http
POST /api/analyze-email
Content-Type: application/json
```

**Request Body:**
```json
{
  "subject": "Meeting Tomorrow",
  "from": "john@example.com",
  "to": ["user@gmail.com"],
  "body": "Hi there, let's meet tomorrow at 3 PM in the conference room.",
  "date": "2025-06-26T10:30:00Z"
}
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "summary": "Meeting request for tomorrow at 3 PM",
    "tone": "friendly",
    "sentiment": "positive",
    "urgency": "medium",
    "action_items": [
      "Attend meeting tomorrow at 3 PM",
      "Go to conference room"
    ],
    "key_information": {
      "meeting_time": "tomorrow at 3 PM",
      "location": "conference room",
      "participants": ["john@example.com", "user@gmail.com"]
    },
    "intent": "meeting_request",
    "requires_response": true,
    "suggested_response": "formal_acceptance"
  }
}
```

### Analyze Email for Spam

Analyze email for spam detection.

```http
POST /api/analyze-spam
Content-Type: application/json
```

**Request Body:**
```json
{
  "subject": "URGENT: Claim your prize now!",
  "from": "noreply@suspicious-domain.com",
  "to": ["user@gmail.com"],
  "body": "Congratulations! You've won $1000! Click here to claim...",
  "headers": {
    "Return-Path": "bounce@suspicious-domain.com",
    "SPF": "fail"
  }
}
```

**Response:**
```json
{
  "success": true,
  "classification": "Spam/Junk",
  "confidence": 0.95,
  "score": 85,
  "explanation": "Multiple spam indicators detected including suspicious sender domain, promotional language, urgency tactics, and failed SPF authentication.",
  "risk_factors": [
    {
      "factor": "sender_domain",
      "severity": "high",
      "description": "Sender domain not associated with legitimate business"
    },
    {
      "factor": "promotional_language",
      "severity": "medium",
      "description": "Contains typical spam phrases like 'Congratulations' and 'Claim your prize'"
    },
    {
      "factor": "spf_failure",
      "severity": "high",
      "description": "SPF authentication failed"
    }
  ],
  "recommendations": [
    "Move to spam folder",
    "Block sender domain",
    "Do not click any links"
  ]
}
```

### Draft Email Assistance

Get AI assistance for drafting emails.

```http
POST /api/draft-email
Content-Type: application/json
```

**Request Body:**
```json
{
  "context": "Reply to meeting request",
  "tone": "professional",
  "key_points": [
    "Accept meeting invitation",
    "Confirm time and location",
    "Ask about agenda"
  ],
  "recipient": "john@example.com",
  "original_email": {
    "subject": "Meeting Tomorrow",
    "body": "Hi there, let's meet tomorrow at 3 PM in the conference room."
  }
}
```

**Response:**
```json
{
  "success": true,
  "draft": {
    "subject": "Re: Meeting Tomorrow",
    "body": "Dear John,\n\nThank you for the meeting invitation. I confirm my availability for tomorrow at 3 PM in the conference room.\n\nCould you please share the agenda so I can prepare accordingly?\n\nBest regards,\n[Your name]",
    "tone_analysis": "professional",
    "suggestions": [
      "Consider adding specific topics you'd like to discuss",
      "Mention if you need to reschedule due to conflicts"
    ]
  }
}
```

## Email Operations

### Send Email

Send a new email.

```http
POST /api/send-email
Content-Type: application/json
```

**Request Body:**
```json
{
  "to": ["recipient@example.com"],
  "cc": ["cc@example.com"],
  "bcc": ["bcc@example.com"],
  "subject": "Email Subject",
  "body": "Email body content",
  "html_body": "<p>HTML email content</p>",
  "attachments": [
    {
      "filename": "document.pdf",
      "content": "base64-encoded-content",
      "content_type": "application/pdf"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Email sent successfully",
  "message_id": "<generated-message-id@domain.com>"
}
```

### Reply to Email

Reply to an existing email.

```http
POST /api/reply-email
Content-Type: application/json
```

**Request Body:**
```json
{
  "original_email_id": "12345",
  "folder": "INBOX",
  "reply_type": "reply", // "reply" or "reply_all"
  "subject": "Re: Original Subject",
  "body": "Reply content",
  "html_body": "<p>Reply HTML content</p>"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Reply sent successfully",
  "message_id": "<reply-message-id@domain.com>"
}
```

### Forward Email

Forward an existing email.

```http
POST /api/forward-email
Content-Type: application/json
```

**Request Body:**
```json
{
  "original_email_id": "12345",
  "folder": "INBOX",
  "to": ["newrecipient@example.com"],
  "subject": "Fwd: Original Subject",
  "body": "Forwarding this email...",
  "include_attachments": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Email forwarded successfully",
  "message_id": "<forward-message-id@domain.com>"
}
```

### Move Email

Move email to different folder.

```http
POST /api/move-email
Content-Type: application/json
```

**Request Body:**
```json
{
  "email_ids": ["12345", "67890"],
  "source_folder": "INBOX",
  "destination_folder": "Archive"
}
```

**Response:**
```json
{
  "success": true,
  "message": "2 emails moved to Archive",
  "moved_count": 2
}
```

### Delete Email

Delete emails (move to trash).

```http
POST /api/delete-email
Content-Type: application/json
```

**Request Body:**
```json
{
  "email_ids": ["12345", "67890"],
  "folder": "INBOX",
  "permanent": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "2 emails deleted",
  "deleted_count": 2
}
```

### Mark Email Flags

Mark emails with flags (read, unread, flagged, etc.).

```http
POST /api/mark-email
Content-Type: application/json
```

**Request Body:**
```json
{
  "email_ids": ["12345", "67890"],
  "folder": "INBOX",
  "flags": {
    "seen": true,
    "flagged": false,
    "deleted": false
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Email flags updated",
  "updated_count": 2
}
```

## Search and Filtering

### Search Emails

Search for emails across folders.

```http
GET /api/search?query=meeting&folder=INBOX&limit=25
```

**Query Parameters:**
- `query` (string): Search terms
- `folder` (string, optional): Folder to search in. Default: all folders
- `limit` (integer, optional): Maximum results. Default: 25
- `from` (string, optional): Filter by sender
- `subject` (string, optional): Filter by subject
- `date_from` (string, optional): Start date (ISO 8601)
- `date_to` (string, optional): End date (ISO 8601)
- `has_attachments` (boolean, optional): Filter emails with attachments

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "id": "12345",
      "subject": "Meeting Tomorrow",
      "from": "john@example.com",
      "date": "2025-06-26T10:30:00Z",
      "folder": "INBOX",
      "snippet": "...meeting tomorrow at 3 PM..."
    }
  ],
  "total_count": 1,
  "query": "meeting"
}
```

## Statistics and Reporting

### Get Email Statistics

Retrieve email statistics and analytics.

```http
GET /api/stats?period=30d
```

**Query Parameters:**
- `period` (string, optional): Time period (`7d`, `30d`, `90d`, `1y`). Default: `30d`

**Response:**
```json
{
  "success": true,
  "stats": {
    "period": "30d",
    "total_emails": 1250,
    "received": 1100,
    "sent": 150,
    "spam_detected": 45,
    "ai_analyses": 234,
    "folders": {
      "INBOX": 850,
      "Sent": 150,
      "Archive": 200,
      "Spam": 45
    },
    "daily_counts": [
      {
        "date": "2025-06-26",
        "received": 12,
        "sent": 3,
        "spam": 2
      }
    ]
  }
}
```

## WebSocket Events

NimbusRelay supports real-time updates via WebSocket connections.

### Connection

```javascript
const socket = io('http://localhost:5000');
```

### Events

#### Email Received
```javascript
socket.on('email_received', function(data) {
  console.log('New email:', data);
  // data: { email: EmailObject, folder: string }
});
```

#### Analysis Complete
```javascript
socket.on('analysis_complete', function(data) {
  console.log('Analysis result:', data);
  // data: { email_id: string, analysis: AnalysisResult }
});
```

#### Connection Status
```javascript
socket.on('connection_status', function(data) {
  console.log('Connection status:', data);
  // data: { service: string, status: string, connected: boolean }
});
```

#### Error Notification
```javascript
socket.on('error_notification', function(data) {
  console.log('Error:', data);
  // data: { error: string, code: string, severity: string }
});
```

## Rate Limits

- **Email Operations**: 60 requests per minute
- **AI Analysis**: 30 requests per minute (Azure OpenAI limits apply)
- **Configuration**: 10 requests per minute

## Error Codes

| Code | Description |
|------|-------------|
| `CONFIG_INCOMPLETE` | Required configuration missing |
| `SERVICE_UNAVAILABLE` | Email or AI service not available |
| `AUTH_FAILED` | Authentication failure |
| `QUOTA_EXCEEDED` | API rate limit exceeded |
| `INVALID_REQUEST` | Invalid request format |
| `EMAIL_NOT_FOUND` | Requested email not found |
| `FOLDER_NOT_FOUND` | Requested folder not found |
| `SEND_FAILED` | Email sending failed |
| `AI_SERVICE_ERROR` | AI analysis service error |

## SDK Examples

### JavaScript/Node.js

```javascript
class NimbusRelayClient {
  constructor(baseUrl = 'http://localhost:5000/api') {
    this.baseUrl = baseUrl;
  }

  async getEmails(folder = 'INBOX', limit = 50) {
    const response = await fetch(
      `${this.baseUrl}/emails?folder=${folder}&limit=${limit}`
    );
    return response.json();
  }

  async analyzeEmail(emailData) {
    const response = await fetch(`${this.baseUrl}/analyze-email`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(emailData)
    });
    return response.json();
  }

  async sendEmail(emailData) {
    const response = await fetch(`${this.baseUrl}/send-email`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(emailData)
    });
    return response.json();
  }
}

// Usage
const client = new NimbusRelayClient();
const emails = await client.getEmails('INBOX', 10);
```

### Python

```python
import requests
import json

class NimbusRelayClient:
    def __init__(self, base_url='http://localhost:5000/api'):
        self.base_url = base_url
        self.session = requests.Session()

    def get_emails(self, folder='INBOX', limit=50):
        response = self.session.get(
            f'{self.base_url}/emails',
            params={'folder': folder, 'limit': limit}
        )
        return response.json()

    def analyze_email(self, email_data):
        response = self.session.post(
            f'{self.base_url}/analyze-email',
            json=email_data
        )
        return response.json()

    def send_email(self, email_data):
        response = self.session.post(
            f'{self.base_url}/send-email',
            json=email_data
        )
        return response.json()

# Usage
client = NimbusRelayClient()
emails = client.get_emails('INBOX', 10)
```

---

This API reference provides comprehensive documentation for integrating with and extending NimbusRelay's functionality. For additional examples and use cases, refer to the main user manual and configuration guide.
