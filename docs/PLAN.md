# PLAN — Gmail Calendar Agent

## שלב 1 — הגדרת סביבה ✅
- [x] יצירת פרויקט Google Cloud
- [x] הפעלת Gmail API + Calendar API
- [x] יצירת OAuth Desktop Client
- [x] הוספת Test Users
- [x] שמירת credentials.json מחוץ ל-Git

## שלב 2 — התקנת סביבת פיתוח ✅
- [x] התקנת uv
- [x] יצירת pyproject.toml
- [x] uv sync — התקנת כל התלויות

## שלב 3 — פיתוח מודולי הליבה ✅
- [x] config.py — הגדרות מרכזיות ו-Environment Variables
- [x] gmail_service.py — שליפה, שליחה, סימון
- [x] calendar_service.py — freebusy, create event
- [x] meeting_parser.py — ניתוח LLM עם Gemini, auto-discover model

## שלב 4 — אינטגרציה ✅
- [x] main.py — חיבור כל המודולים לזרימה אחת

## שלב 5 — בדיקות ✅
- [x] תרחיש 1: "לשבת לקפה" — רביעי 08:00 — זמן פנוי → אירוע נוצר
- [x] תרחיש 2: "פגישה ביום חמישי" — 07:00, מאור ושי, זום → אירוע נוצר
- [x] תרחיש 3: "ישיבת קפה" — חמישי 07:00 — זמן תפוס → מייל דחייה נשלח
- [x] תרחיש 4: מייל אימות GitHub → זוהה נכון כלא-פגישה

## שלב 6 — תיעוד ואבטחה ✅
- [x] .gitignore מגן על credentials.json ו-token.json
- [x] README.md עם כל הסעיפים הנדרשים
- [x] docs/PRD.md, PLAN.md, TODO.md
- [x] tests/test_cases.md עם 4 תרחישי בדיקה מתועדים