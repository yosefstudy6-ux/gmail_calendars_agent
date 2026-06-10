# PRD — Gmail Calendar Agent

## סקירה כללית

סוכן AI אוטומטי שמחבר בין Gmail ל-Google Calendar. הסוכן סורק מיילים נכנסים,
מזהה בקשות פגישה בטקסט חופשי בעזרת מודל Gemini, בודק זמינות ביומן, ומבצע פעולה
מתאימה (יצירת אירוע או שליחת מייל דחייה) — כל זאת ללא התערבות אנושית.

## משתמש יעד

כל בעל חשבון Gmail שרוצה לאוטומט את תהליך תיאום הפגישות הנכנסות — מנהלים, יועצים,
אנשי עסקים — ללא צורך בידע תכנותי לאחר ההגדרה הראשונית.

## ארכיטקטורת המערכת
[Gmail Inbox]
↓ Gmail API (OAuth2)
[gmail_service.py] — שליפת מיילים, שליחת תשובה, סימון PROCESSED
↓
[meeting_parser.py] — שליחת prompt ל-Gemini LLM
↓ Gemini API
[Gemini LLM] → מחזיר JSON: {is_meeting, date, time, participants, location}
↓
[calendar_service.py] — בדיקת freebusy / יצירת event
↓ Google Calendar API (OAuth2)
[Google Calendar]



## קלטים

- מיילים נכנסים ב-Gmail (subject + body בטקסט חופשי)
- זמינות ביומן Google Calendar של המשתמש
- משתנה סביבה: `GEMINI_API_KEY`

## פלטים

| תרחיש | פלט |
|---|---|
| מייל הוא בקשת פגישה, הזמן פנוי | אירוע חדש נוצר ב-Google Calendar |
| מייל הוא בקשת פגישה, הזמן תפוס | מייל דחייה נשלח לשולח |
| מייל אינו בקשת פגישה | המייל מסומן כמעובד, לא בוצעה פעולה |
| בקשת פגישה חסרת תאריך/שעה | לא נוצר אירוע, מסומן כמעובד |

## דרישות פונקציונליות

1. סריקת מיילים מ-7 הימים האחרונים שלא טופלו עדיין
2. זיהוי בקשות פגישה בשפה חופשית (עברית ואנגלית) — לא רק Calendar Invite
3. חילוץ: תאריך, שעה, מיקום, משתתפים
4. בדיקת freebusy ב-Google Calendar
5. יצירת אירוע או שליחת דחייה לפי התוצאה
6. סימון מיילים שטופלו כ-PROCESSED_BY_AGENT למניעת עיבוד כפול

## דרישות לא-פונקציונליות

- **אבטחה:** credentials.json ו-token.json אסורים ב-Git. כל מפתח רגיש — משתנה סביבה
- **ניידות:** הקוד רץ על Windows, Mac, ו-Linux ללא שינויים
- **זמן תגובה:** עיבוד מייל בודד — עד 10 שניות (כולל קריאת Gemini API)
- **עלות:** כל ניתוח מייל צורך כ-300-700 טוקנים. ב-Gemini Flash: ~0.001$ למייל
- **עמידות בשגיאות:** כל מייל עטוף ב-try/except — שגיאה במייל אחד לא עוצרת את הסוכן

## כללי קבלת החלטות
if is_meeting == False → mark processed, skip
if is_meeting == True AND (date is None OR time is None) → mark processed, skip
if is_meeting == True AND time is free → create calendar event
if is_meeting == True AND time is busy → send decline email
## אילוצים

- Gmail בלבד (לא Outlook)
- OAuth2 Desktop Client — לא Service Account
- Python 3.10+ עם uv לניהול תלויות







