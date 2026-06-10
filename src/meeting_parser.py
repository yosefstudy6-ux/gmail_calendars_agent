import json
import os
import re
import urllib.request
from urllib.error import HTTPError
from datetime import datetime
from dotenv import load_dotenv

# פקודה שקוראת את קובץ הסודות שיצרת
load_dotenv()

def _normalize_time(value):
    if not value: return None
    value = str(value).strip()
    if re.fullmatch(r"\d{2}:\d{2}", value): return f"{value}:00"
    if re.fullmatch(r"\d{2}:\d{2}:\d{2}", value): return value
    return None

def parse_llm_json(text):
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text).strip()
    
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start:end + 1]

    try:
        data = json.loads(text)
    except:
        return {"is_meeting": False}

    return {
        "is_meeting": bool(data.get("is_meeting", False)),
        "date": data.get("date"),
        "time": _normalize_time(data.get("time")),
        "participants": data.get("participants") or [],
        "location": data.get("location"),
        "summary": data.get("summary"),
        "reason": data.get("reason", ""),
    }

def _get_best_model(api_key):
    # פונקציה חכמה ששואלת את גוגל אילו מודלים באמת זמינים למפתח הזה
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        request = urllib.request.Request(url)
        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            valid_models = []
            for m in data.get("models", []):
                if "generateContent" in m.get("supportedGenerationMethods", []):
                    valid_models.append(m["name"].replace("models/", ""))
            
            if not valid_models:
                return None
                
            # מנסה לבחור את המודלים החכמים ביותר מהרשימה שחזרה
            for pref in ["gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-1.5-pro", "gemini-1.0-pro", "gemini-pro"]:
                if pref in valid_models:
                    return pref
                    
            # אם לא מצא את המועדפים, פשוט לוקח את הראשון שזמין ועובד!
            return valid_models[0]
    except Exception as e:
        print(f"Failed to auto-discover models: {e}")
        return None

def _call_gemini_api(api_key, model_name, system_prompt, user_prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}],
        "generationConfig": {"temperature": 0.0}
    }

    request = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST"
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        response_data = json.loads(response.read().decode("utf-8"))
        return response_data["candidates"][0]["content"]["parts"][0]["text"]

def _call_llm(email_data):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: The GEMINI_API_KEY is missing from .env file!")
        return None

    # מפעיל את הגילוי האוטומטי
    print("Auto-discovering available Gemini models...")
    best_model = _get_best_model(api_key)
    
    if not best_model:
        print("\n[CRITICAL ERROR] Google says your API key has NO models available.")
        print("Please enable 'Generative Language API' in your Google Cloud Console.")
        return None
        
    print(f"[*] Success! Found available model: {best_model}")

    today = datetime.now().date().isoformat()
    system_prompt = (
        "You extract meeting details from emails. "
        "Return JSON only with keys: is_meeting, date, time, participants, location, summary, reason. "
        "Rules: 1) date must be YYYY-MM-DD or null. 2) time must be HH:MM:SS or null. "
        "3) participants must contain only email addresses if present. "
        "4) Infer relative dates like tomorrow using today's date. "
        "5) If not a meeting invitation, set is_meeting false and others null."
    )
    user_prompt = f"Today: {today}\nFrom: {email_data.get('from', '')}\nSubject: {email_data.get('subject', '')}\nBody:\n{email_data.get('body', '')}\n"

    try:
        text = _call_gemini_api(api_key, best_model, system_prompt, user_prompt)
        return parse_llm_json(text)
    except HTTPError as e:
        print(f"\n[!] Google API Error for {best_model}:\n--> Message: {e.read().decode('utf-8')}\n")
        return None

def analyze_email(email_data):
    try:
        result = _call_llm(email_data)
        if result: return result
    except Exception as e:
        print(f"Error reading email with LLM: {e}")
    
    return {"is_meeting": False}