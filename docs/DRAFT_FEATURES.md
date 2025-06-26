# Draft and Email Sending Features

## Overview

NimbusRelay now supports creating and sending email drafts with full IMAP and SMTP integration.

## New Features

### 1. Save Draft
- **Location**: Available when generating draft responses to emails
- **Functionality**: Saves draft emails directly to the IMAP "INBOX.Drafts" folder
- **API Endpoint**: `POST /api/save-draft`

### 2. Send Reply
- **Location**: Available when generating draft responses to emails  
- **Functionality**: Sends emails immediately via SMTP and saves a copy to "INBOX.Sent" folder
- **API Endpoint**: `POST /api/send-email`

## How to Use

### Step 1: Configure Email Settings
Ensure your IMAP and SMTP settings are configured:
- **IMAP Server**: For reading emails (e.g., `imap.gmail.com`)
- **SMTP Server**: Auto-configured based on IMAP server
  - Gmail: `smtp.gmail.com:587` (TLS)
  - Outlook: `smtp-mail.outlook.com:587` (TLS)
  - Yahoo: `smtp.mail.yahoo.com:587` (TLS)
- **SMTP Sender Email**: Optional full sender email address (defaults to IMAP username if not provided)

### Step 2: Generate Draft Response
1. Select an email from your inbox
2. Click "Generate Draft" button (✍️)
3. AI will analyze the email and generate a response
4. A full-screen editor will open with the draft

### Step 3: Edit and Send/Save
In the draft editor:
- **To/CC/BCC Fields**: Edit recipients as needed
- **Subject**: Modify the subject line
- **Body**: Edit the email content (includes quoted original)
- **Save Draft** (💾): Saves to INBOX.Drafts folder
- **Send Reply** (🚀): Sends immediately and saves copy to INBOX.Sent

## Technical Implementation

### Backend Components

1. **DraftEmail Model** (`src/models/email_models.py`)
   - Represents draft email structure
   - Includes to, cc, bcc, subject, body, reply_to_id fields

2. **SMTPEmailService** (`src/email_service/smtp_service.py`)
   - Handles SMTP connections and email sending
   - Supports TLS encryption
   - Auto-configures SMTP settings based on IMAP provider

3. **IMAP Draft Saving** (`src/email_service/imap_email_service.py`)
   - `save_draft()` method appends emails to IMAP folders
   - Creates folders if they don't exist
   - Properly formats email headers and content

4. **Service Manager Integration** (`src/services/service_manager.py`)
   - `save_draft()` and `send_email()` methods
   - Coordinates IMAP and SMTP operations
   - Handles error reporting and logging

5. **API Endpoints** (`src/routes/api_routes.py`)
   - `POST /api/save-draft`: Save draft to IMAP folder
   - `POST /api/send-email`: Send email via SMTP

### Frontend Integration

The JavaScript client (`static/js/app.js`) includes:
- Full-screen draft editor modal
- Form validation for required fields
- Progress indicators during save/send operations
- Error handling and user feedback
- Confirmation dialogs for sending emails

## SMTP Auto-Configuration

The system automatically configures SMTP settings based on your IMAP server:

| IMAP Server | SMTP Server | Port | Encryption |
|-------------|-------------|------|------------|
| imap.gmail.com | smtp.gmail.com | 587 | TLS |
| outlook.office365.com | smtp-mail.outlook.com | 587 | TLS |
| imap.mail.yahoo.com | smtp.mail.yahoo.com | 587 | TLS |
| Custom | Replace 'imap' with 'smtp' | 587 | TLS |

## Error Handling

The system provides comprehensive error handling:
- **Network errors**: Connection timeouts, server unavailable
- **Authentication errors**: Invalid credentials
- **Validation errors**: Missing recipient, invalid email format
- **IMAP errors**: Folder access issues, quota exceeded
- **SMTP errors**: Sending failures, recipient rejected

## Security Considerations

- All credentials are handled securely
- TLS encryption is used for SMTP connections
- Email content is validated and sanitized
- No sensitive data is logged

## Future Enhancements

Potential improvements:
- HTML email composition
- File attachments support
- Email templates
- Scheduled sending
- Multiple account support
- Email signatures

## Testing

Run the test suite to verify functionality:
```bash
python test_draft_email.py
```

This validates:
- Model serialization/deserialization
- SMTP auto-configuration
- Service initialization
