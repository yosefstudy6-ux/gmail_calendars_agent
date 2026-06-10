from pathlib import Path
import os
from dotenv import load_dotenv

# טעינת קובץ הסודות (.env)
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
# נתיב לתיקיית המפתחות הפרטית שלך
PRIVATE_DIR = Path(r"C:\study\private_google")

CREDENTIALS_FILE = PRIVATE_DIR / "credentials.json"
TOKEN_FILE = PRIVATE_DIR / "token.json"

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar",
]

GMAIL_QUERY = 'newer_than:7d -in:trash -category:promotions -label:PROCESSED_BY_AGENT'
CALENDAR_ID = "primary"
PROCESSED_LABEL_NAME = "PROCESSED_BY_AGENT"

MEETING_DURATION_MINUTES = 60
DECLINE_SUBJECT = "Re: לא ניתן לאשר את הפגישה"

DEFAULT_TIMEZONE = "Asia/Jerusalem"