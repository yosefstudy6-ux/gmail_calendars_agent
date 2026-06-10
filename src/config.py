from pathlib import Path
import os
from dotenv import load_dotenv

# טעינת משתני סביבה מקובץ .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# נתיבים לקבצי האימות — נקראים ממשתני סביבה, או מהתיקייה הנוכחית כברירת מחדל
CREDENTIALS_FILE = Path(os.environ.get("GOOGLE_CREDENTIALS_PATH", "credentials.json"))
TOKEN_FILE = Path(os.environ.get("GOOGLE_TOKEN_PATH", "token.json"))

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