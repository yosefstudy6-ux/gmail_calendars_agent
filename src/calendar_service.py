from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from googleapiclient.discovery import build


def build_calendar_service(creds):
    return build("calendar", "v3", credentials=creds)


def get_local_tz():
    return datetime.now().astimezone().tzinfo


def ensure_local_timezone(dt):
    local_tz = get_local_tz()

    if dt.tzinfo is None:
        return dt.replace(tzinfo=local_tz)

    return dt.astimezone(local_tz)


def get_calendar_timezone(calendar_service, calendar_id="primary"):
    try:
        calendar_data = calendar_service.calendars().get(calendarId=calendar_id).execute()
        return calendar_data.get("timeZone", "Asia/Jerusalem")
    except Exception:
        return "Asia/Jerusalem"


def is_time_free(calendar_service, start_dt, end_dt, calendar_id="primary"):
    start_dt = ensure_local_timezone(start_dt)
    end_dt = ensure_local_timezone(end_dt)

    body = {
        "timeMin": start_dt.isoformat(),
        "timeMax": end_dt.isoformat(),
        "items": [{"id": calendar_id}],
    }

    response = calendar_service.freebusy().query(body=body).execute()
    busy_slots = response.get("calendars", {}).get(calendar_id, {}).get("busy", [])

    return len(busy_slots) == 0


def create_event(
    calendar_service,
    summary,
    description,
    start_dt,
    end_dt,
    attendees=None,
    location=None,
    calendar_id="primary",
):
    start_dt = ensure_local_timezone(start_dt)
    end_dt = ensure_local_timezone(end_dt)
    calendar_tz = get_calendar_timezone(calendar_service, calendar_id)

    event = {
        "summary": summary,
        "description": description,
        "start": {
            "dateTime": start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "timeZone": calendar_tz,
        },
        "end": {
            "dateTime": end_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "timeZone": calendar_tz,
        },
    }

    if attendees:
        clean_attendees = [email for email in attendees if email]
        if clean_attendees:
            event["attendees"] = [{"email": email} for email in clean_attendees]

    if location:
        event["location"] = location

    return calendar_service.events().insert(
        calendarId=calendar_id,
        body=event
    ).execute()


def build_time_range(meeting_date, meeting_time, duration_minutes=60):
    start_dt = datetime.fromisoformat(f"{meeting_date}T{meeting_time}")
    start_dt = ensure_local_timezone(start_dt)
    end_dt = start_dt + timedelta(minutes=duration_minutes)
    return start_dt, end_dt