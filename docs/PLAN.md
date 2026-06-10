# PLAN

## שלב 1
הגדרת Google Cloud, Gmail API, Calendar API, OAuth Desktop Client ו-Test Users.

## שלב 2
התקנת uv ויצירת סביבת הפרויקט.

## שלב 3
כתיבת `config.py` עם paths, scopes ו-query.

## שלב 4
כתיבת `gmail_service.py` לשליפת מיילים, קריאת תוכן, שליחת מייל תשובה וסימון כמעובד.

## שלב 5
כתיבת `calendar_service.py` לבדיקת free/busy וליצירת event.

## שלב 6
כתיבת `meeting_parser.py` לניתוח מיילים בעזרת LLM עם fallback.

## שלב 7
כתיבת `main.py` שמחבר את כל הזרימה.

## שלב 8
בדיקות: מייל פגישה פנוי, מייל פגישה תפוס, מייל רגיל, מייל חסר נתונים.

## שלב 9
סידור GitHub והעלאת README + PRD + PLAN + TODO.