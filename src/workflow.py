"""
workflow.py — תיאור זרימת העבודה של הסוכן

זרימת העבודה המלאה מוגדרת ב-main.py.
קובץ זה מתעד את תרשים הזרימה ההגיוני:

1. SCAN     — list_messages(gmail_service, GMAIL_QUERY)
2. PARSE    — get_message_details() → analyze_email() via Gemini LLM
3. DECIDE   — is_meeting? has date+time?
4. CHECK    — is_time_free(calendar_service, start_dt, end_dt)
5a. FREE    — create_event(calendar_service, ...)
5b. BUSY    — send_reply(gmail_service, decline_email)
6. MARK     — mark_message_processed(gmail_service, message_id)

Diagram:
  Gmail → [Scan] → [LLM Parse] → [Decision]
                                      ↓
                              is_meeting=False → Mark & Skip
                                      ↓
                              missing date/time → Mark & Skip
                                      ↓
                              [Check Calendar]
                                   ↙       ↘
                              Free         Busy
                                ↓            ↓
                         Create Event   Send Decline
                                ↓            ↓
                              Mark Processed
"""