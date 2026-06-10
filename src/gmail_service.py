import base64
import re
from email.message import EmailMessage
from email.utils import parseaddr

from googleapiclient.discovery import build


def build_gmail_service(creds):
    return build("gmail", "v1", credentials=creds)


def _decode_base64url(data):
    if not data:
        return ""
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding).decode("utf-8", errors="ignore")


def _extract_plain_text(payload):
    mime_type = payload.get("mimeType", "")
    body_data = payload.get("body", {}).get("data")

    if mime_type == "text/plain" and body_data:
        return _decode_base64url(body_data)

    parts = payload.get("parts", [])
    for part in parts:
        text = _extract_plain_text(part)
        if text:
            return text

    if body_data:
        html_text = _decode_base64url(body_data)
        html_text = re.sub(r"<br\s*/?>", "\n", html_text, flags=re.IGNORECASE)
        html_text = re.sub(r"<[^>]+>", " ", html_text)
        html_text = re.sub(r"\s+", " ", html_text).strip()
        return html_text

    return ""


def clean_email_address(value):
    if not value:
        return None

    _, email_address = parseaddr(value)
    email_address = (email_address or "").strip()

    if "@" not in email_address:
        return None

    return email_address


def list_messages(gmail_service, query="", max_results=10):
    response = gmail_service.users().messages().list(
        userId="me",
        q=query,
        maxResults=max_results
    ).execute()

    return response.get("messages", [])


def get_message_details(gmail_service, message_id):
    message = gmail_service.users().messages().get(
        userId="me",
        id=message_id,
        format="full"
    ).execute()

    headers = message.get("payload", {}).get("headers", [])

    subject = ""
    sender = ""
    message_id_header = ""
    thread_id = message.get("threadId", "")

    for header in headers:
        name = header.get("name", "").lower()
        value = header.get("value", "")
        if name == "subject":
            subject = value
        elif name == "from":
            sender = value
        elif name == "message-id":
            message_id_header = value

    body_text = _extract_plain_text(message.get("payload", {}))

    return {
        "id": message_id,
        "thread_id": thread_id,
        "message_id_header": message_id_header,
        "subject": subject,
        "from": sender,
        "from_email": clean_email_address(sender),
        "body": body_text,
    }


def send_reply(gmail_service, to_email, subject, body_text, thread_id=None, in_reply_to=None):
    recipient = clean_email_address(to_email)
    if not recipient:
        raise ValueError(f"Invalid recipient address: {to_email}")

    message = EmailMessage()
    message["To"] = recipient
    message["Subject"] = subject
    if in_reply_to:
        message["In-Reply-To"] = in_reply_to
        message["References"] = in_reply_to
    message.set_content(body_text)

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

    body = {"raw": raw}
    if thread_id:
        body["threadId"] = thread_id

    return gmail_service.users().messages().send(
        userId="me",
        body=body
    ).execute()


def get_or_create_label(gmail_service, label_name):
    labels = gmail_service.users().labels().list(userId="me").execute().get("labels", [])

    for label in labels:
        if label.get("name") == label_name:
            return label.get("id")

    created = gmail_service.users().labels().create(
        userId="me",
        body={
            "name": label_name,
            "labelListVisibility": "labelShow",
            "messageListVisibility": "show",
        }
    ).execute()

    return created.get("id")


def mark_message_processed(gmail_service, message_id, label_name):
    label_id = get_or_create_label(gmail_service, label_name)
    gmail_service.users().messages().modify(
        userId="me",
        id=message_id,
        body={"addLabelIds": [label_id]}
    ).execute()