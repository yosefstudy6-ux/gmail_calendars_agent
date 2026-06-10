from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from src.config import (
    CREDENTIALS_FILE,
    TOKEN_FILE,
    SCOPES,
    GMAIL_QUERY,
    CALENDAR_ID,
    MEETING_DURATION_MINUTES,
    DECLINE_SUBJECT,
    PROCESSED_LABEL_NAME,
)
from src.gmail_service import (
    build_gmail_service,
    list_messages,
    get_message_details,
    send_reply,
    mark_message_processed,
)
from src.calendar_service import (
    build_calendar_service,
    is_time_free,
    create_event,
    build_time_range,
)
from src.meeting_parser import analyze_email


def get_credentials():
    creds = None

    if Path(TOKEN_FILE).exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)

        Path(TOKEN_FILE).write_text(creds.to_json(), encoding="utf-8")

    return creds


def main():
    if not CREDENTIALS_FILE.exists():
        raise FileNotFoundError(f"Missing credentials file: {CREDENTIALS_FILE}")

    creds = get_credentials()
    gmail_service = build_gmail_service(creds)
    calendar_service = build_calendar_service(creds)

    messages = list_messages(gmail_service, GMAIL_QUERY, max_results=10)
    print(f"Found {len(messages)} messages")

    for item in messages:
        try:
            email_data = get_message_details(gmail_service, item["id"])

            print("=" * 60)
            print("SUBJECT:", email_data.get("subject", ""))
            print("FROM:", email_data.get("from", ""))

            parsed = analyze_email(email_data)
            print("PARSED:", parsed)

            if not parsed.get("is_meeting"):
                print("Not a meeting invitation")
                mark_message_processed(gmail_service, email_data["id"], PROCESSED_LABEL_NAME)
                continue

            if not parsed.get("date") or not parsed.get("time"):
                print("Meeting detected but date/time missing")
                mark_message_processed(gmail_service, email_data["id"], PROCESSED_LABEL_NAME)
                continue

            start_dt, end_dt = build_time_range(
                parsed["date"],
                parsed["time"],
                MEETING_DURATION_MINUTES
            )

            free = is_time_free(
                calendar_service=calendar_service,
                start_dt=start_dt,
                end_dt=end_dt,
                calendar_id=CALENDAR_ID,
            )
            if free:
                event = create_event(
                    calendar_service=calendar_service,
                    summary=parsed.get("summary") or "Email Meeting",
                    description=(
                        f"Created from email subject: {email_data.get('subject', '')}\n"
                        f"Sender: {email_data.get('from', '')}\n"
                        f"Reason: {parsed.get('reason', '')}"
                    ),
                    start_dt=start_dt,
                    end_dt=end_dt,
                    attendees=parsed.get("participants", []),
                    location=parsed.get("location"),
                    calendar_id=CALENDAR_ID,
                )
                print("Created event:", event.get("htmlLink"))
            else:
                send_reply(
                    gmail_service=gmail_service,
                    to_email=email_data.get("from_email", ""),
                    subject=DECLINE_SUBJECT,
                    body_text="לא ניתן לבצע את הפגישה במועד המבוקש משום שהיומן תפוס.",
                    thread_id=email_data.get("thread_id"),
                    in_reply_to=email_data.get("message_id_header"),
                )
                print("Sent decline email")

            mark_message_processed(gmail_service, email_data["id"], PROCESSED_LABEL_NAME)

        except Exception as exc:
            print("ERROR:", exc)

    print("Done")


if __name__ == "__main__":
    main()