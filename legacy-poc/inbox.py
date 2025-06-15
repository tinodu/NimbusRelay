# %%
import os
import json
import email
import imaplib
from email.header import decode_header, make_header
from openai import AzureOpenAI
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

# %%
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
model_name = os.getenv("AZURE_OPENAI_MODEL_NAME")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
apikey = os.getenv("AZURE_OPENAI_API_KEY")
version = os.getenv("AZURE_OPENAI_API_VERSION")
# Print all loaded values
print("Endpoint:", endpoint)
print("Model Name:", model_name)
print("Deployment:", deployment)
print("API Key:", apikey)
print("Version:", version)



# %%
# Replace with your email server details from .env file
imap_server = os.getenv('IMAP_SERVER')
imap_port = int(os.getenv('IMAP_PORT', 993))  # Default to 993 if not specified
username = os.getenv('IMAP_USERNAME')
password = os.getenv('IMAP_PASSWORD')
print("IMAP Server:", imap_server)
print("IMAP Port:", imap_port)
print("Username:", username)
print("Password:", password)

# %%
client = AzureOpenAI(
    api_version=version,
    azure_endpoint=endpoint,
    api_key=apikey,
)

# %%
# Connect to the IMAP server using SSL
mailbox = imaplib.IMAP4_SSL(imap_server, imap_port)
mailbox.login(username, password)

print("Connected to IMAP server successfully.")

# Select the INBOX
mailbox.select('INBOX')

# Get the number of messages
status, messages = mailbox.search(None, 'ALL')
email_ids = messages[0].split()
num_messages = len(email_ids)

print(f"Number of emails in inbox: {num_messages}")

# %%
def decode_mime_header(header_value):
    if header_value is None:
        return None
    try:
        return str(make_header(decode_header(header_value)))
    except Exception:
        return header_value

def get_email_object(raw_email_bytes):
    msg = email.message_from_bytes(raw_email_bytes)
    email_details = {
        "From": decode_mime_header(msg.get("From")),
        "To": decode_mime_header(msg.get("To")),
        "Subject": decode_mime_header(msg.get("Subject")),
        "Date": decode_mime_header(msg.get("Date")),
        "Content-Type": decode_mime_header(msg.get("Content-Type")),
        "Headers": {header: decode_mime_header(value) for header, value in msg.items()},
        "Body": None
    }

    if not email_details["Subject"] or email_details["Subject"].strip() == "":
        email_details["Subject"] = "(no subject)"

    # Extract the email body (only the first text/plain or text/html part)
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type in ("text/plain", "text/html"):
                charset = part.get_content_charset() or "utf-8"
                try:
                    email_details["Body"] = part.get_payload(decode=True).decode(charset, errors="replace")
                except Exception as e:
                    email_details["Body"] = f"Could not decode part: {e}"
                break
    else:
        charset = msg.get_content_charset() or "utf-8"
        email_details["Body"] = msg.get_payload(decode=True).decode(charset, errors="replace")

    return email_details

# %%
def call_llm_email_object(email_obj, system_prompt):
    # Truncate the email body to the first 125000 characters if present
    email_obj_trunc = dict(email_obj)
    if email_obj_trunc.get("Body"):
        email_obj_trunc["Body"] = email_obj_trunc["Body"][:125000]

    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": json.dumps(email_obj_trunc),
            }
        ],
        max_tokens=4096,
        temperature=1.0,
        top_p=1.0,
        model=deployment
    )

    return response.choices[0].message.content

def call_llm(user_prompt, system_prompt):
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": json.dumps(user_prompt),
            }
        ],
        max_tokens=4096,
        temperature=1.0,
        top_p=1.0,
        model=deployment
    )

    return response.choices[0].message.content

# %%
def move_email_to_trash(mailbox, email_id):
    """
    Moves an email to the Trash folder using IMAP.
    """
    try:
        # Try to copy to Trash and mark as deleted in INBOX
        mailbox.copy(email_id, 'Trash')
        mailbox.store(email_id, '+FLAGS', '\\Deleted')
        print(f"Email with id {email_id} moved to Trash.")
    except Exception as e:
        print(f"Failed to move email {email_id} to Trash: {e}")

# %%
def move_email_to_junk(mailbox, email_id):
    """
    Moves an email to the Junk (Spam) folder using IMAP.
    """
    try:
        # Try to copy to Junk and mark as deleted in INBOX
        result = mailbox.copy(email_id, 'INBOX.spam')
        if result[0] != 'OK':
            raise Exception(f"Failed to copy email {email_id} to spam folder: {result[1]}")
        else:
            mailbox.store(email_id, '+FLAGS', '\\Deleted')        
    except Exception as e:
        print(f"Failed to move email {email_id} to Junk: {e}")

# %%
with open('prompts/email-spam.md', 'r', encoding='utf-8') as file:
    email_spam_prompt = file.read()

for i, email_id in enumerate(reversed(email_ids), 1):
    success = False
    retry = 0
    
    status, msg_data = mailbox.fetch(email_id, '(RFC822)')
    if status != 'OK':
        print(f"Failed to fetch email {len(email_ids) - i + 1}")
        continue
    raw_email = msg_data[0][1]
    email_obj = get_email_object(raw_email)
    
    print(f"Email {len(email_ids) - i + 1} is being analyzed. Subject: {email_obj['Subject']}, Sender: {email_obj['From']}")
    while not success and retry < 3:
        if retry > 0:
            print(f"Retrying... Attempt {retry}")

        is_spam = call_llm_email_object(email_obj, email_spam_prompt)
        try:
            spam_result = json.loads(is_spam)
            if spam_result.get("classification") == "Spam/Junk":
                move_email_to_junk(mailbox, email_id)
                print(f"Email {len(email_ids) - i + 1} moved to Junk.")
            else:
                print(f"Email {len(email_ids) - i + 1} is valid.")
            success = True
        except Exception as e:
            print(f"Success {success}. Retry {retry}. Failed to parse classification response: {e}")
            retry += 1
            success = False
    
    print("\n")


# %%
# Permanently remove emails marked as deleted from the INBOX
mailbox.expunge()
print("Inbox changes confirmed. Junk emails have been moved to Spam.")

# %%

# Connect to the IMAP server using SSL
mailbox = imaplib.IMAP4_SSL(imap_server, imap_port)
mailbox.login(username, password)

print("Connected to IMAP server successfully.")

# Select the INBOX
mailbox.select('INBOX')

# Get the number of messages
status, messages = mailbox.search(None, 'ALL')
email_ids = messages[0].split()
num_messages = len(email_ids)

print(f"Number of emails in inbox: {num_messages}")

# %%
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import time

def save_draft_response(mailbox, email_obj, draft_body):
    """
    Save a draft response to the IMAP 'Drafts' folder without sending it.
    The draft will be addressed to the original sender and reference the original subject.
    The previous email will be included below the draft body in the most common quoted format.
    """

    # Prepare quoted original message (simple plain text quoting)
    original_body = email_obj.get('Body', '')
    quoted_body = "\n".join([f"> {line}" for line in original_body.splitlines()])
    original_headers = (
        f"On {email_obj.get('Date')}, {email_obj.get('From')} wrote:\n"
    )
    full_body = f"{draft_body}\n\n{original_headers}{quoted_body}"

    # Prepare draft email
    msg = MIMEMultipart()
    msg['From'] = email_obj.get('To')
    msg['To'] = email_obj.get('From')
    msg['Subject'] = f"Re: {email_obj.get('Subject')}"
    msg['Date'] = datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
    msg.attach(MIMEText(full_body, 'plain', 'utf-8'))

    # Convert to RFC822 format
    draft_bytes = msg.as_bytes()

    # Append to Drafts folder
    try:
        result = mailbox.append('INBOX.Drafts', '', imaplib.Time2Internaldate(time.time()), draft_bytes)
        if result[0] == 'OK':
            print("Draft saved to 'Drafts' folder successfully.")
        else:
            print(f"Failed to save draft: {result}")
    except Exception as e:
        print(f"Error saving draft: {e}")

# Example usage:
# save_draft_response(mailbox, email_obj, draft_result)

# %%
# Load the content of the file with UTF-8 decoding
with open('prompts/email-analyze.md', 'r', encoding='utf-8') as file:
    email_analyze_prompt = file.read()

# Load the content of the file with UTF-8 decoding
with open('prompts/email-draft.md', 'r', encoding='utf-8') as file:
    email_draft_prompt = file.read()

take = 10

for i, email_id in enumerate(reversed(email_ids[-take:]), 1):
    status, msg_data = mailbox.fetch(email_id, '(RFC822)')
    if status != 'OK':
        print(f"Failed to fetch email {len(email_ids) - i + 1}")
        continue
    raw_email = msg_data[0][1]
    email_obj = get_email_object(raw_email)
    
    print(f"Analyzing Email {len(email_ids) - i + 1}. Subject: {email_obj['Subject']}, Sender: {email_obj['From']}")
    
    try:
        analysis_result = call_llm_email_object(email_obj, email_analyze_prompt)
        print(f"Analysis Result for Email {len(email_ids) - i + 1}: {analysis_result}")
    except Exception as e:
        print(f"Failed to analyze Email {len(email_ids) - i + 1}: {e}")
    
    print("\n")

    try:
        draft_result = call_llm(analysis_result, email_draft_prompt)
        print(f"Draft for Email {len(email_ids) - i + 1}:\n -- DRAFT_START--\n{draft_result}\n-- DRAFT_END--")

        # Save the draft response to the 'Drafts' folder
        save_draft_response(mailbox, email_obj, draft_result)
    except Exception as e:
        print(f"Failed to draft email response {len(email_ids) - i + 1}: {e}")


# %%



