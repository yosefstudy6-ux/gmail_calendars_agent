# Prompt — Meeting Parser (Gemini)

## גרסה 1 (ראשונית)
Extract if this is a meeting request. Return JSON.


**בעיה:** LLM החזיר JSON לא עקבי, לפעמים עם ```json wrapper, לפעמים בלי.

---

## גרסה 2 (שיפור)
You extract meeting details from emails.
Return JSON only with keys: is_meeting, date, time, participants, location, summary, reason.

text

**בעיה:** LLM לא ידע לטפל בתאריכים יחסיים כמו "מחר" ו"יום שני הקרוב".

---

## גרסה 3 (סופית — בשימוש)
You extract meeting details from emails.
Return JSON only with keys: is_meeting, date, time, participants, location, summary, reason.
Rules:

date must be YYYY-MM-DD or null.

time must be HH:MM:SS or null.

participants must contain only email addresses if present.

Infer relative dates like tomorrow using today's date.

If not a meeting invitation, set is_meeting false and others null.

Today: {today}
From: {sender}
Subject: {subject}
Body:
{body}

text

**שיפורים לעומת גרסה 2:**
- הוספת `Today: {today}` לאפשר חישוב תאריכים יחסיים
- הבהרה ש-participants = כתובות מייל בלבד
- הוספת `temperature: 0.0` לתוצאות עקביות

---

## ניתוח ביצועים

| תרחיש | גרסה 1 | גרסה 2 | גרסה 3 |
|---|---|---|---|
| מייל עם תאריך מפורש | ✅ | ✅ | ✅ |
| מייל עם "מחר" | ❌ | ❌ | ✅ |
| מייל רגיל | ✅ | ✅ | ✅ |
| מייל ללא שעה | ❌ (החזיר 00:00) | ❌ | ✅ (null) |
