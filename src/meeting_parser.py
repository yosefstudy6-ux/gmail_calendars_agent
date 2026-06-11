import json
import os
import re
import time
import urllib.request
from urllib.error import HTTPError
from datetime import datetime
from dotenv import load_dotenv

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
                return []
            preferred = ["gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-2.0-flash",
                         "gemini-1.5-pro", "gemini-2.5-flash", "gemini-1.0-pro", "gemini-pro"]
            ordered = [p for p in preferred if p in valid_models]
            remaining = [m for m in valid_models if m not in ordered]
            return ordered + remaining
    except Exception as e:
        print(f"Failed to auto-discover models: {e}")
        return []

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
        print("Error: GEMINI_API_KEY is missing from .env file!")
        return None

    print("Auto-discovering available Gemini models...")
    models = _get_best_model(api_key)

    if not models:
        print("[CRITICAL ERROR] No available models found for this API key.")
        return None

    today = datetime.now().date().isoformat()
    system_prompt = (
        "You extract meeting details from emails. "
        "Return JSON only with keys: is_meeting, date, time, participants, location, summary, reason. "
        "Rules: 1) date must be YYYY-MM-DD or null. 2) time must be HH:MM:SS or null. "
        "3) participants is a list of email addresses or empty list. "
        "4) Infer relative dates using today's date. "
        "5) If not a meeting invitation, set is_meeting to false and others to null."
    )
    user_prompt = (
        f"Today: {today}\n"
        f"From: {email_data.get('from', '')}\n"
        f"Subject: {email_data.get('subject', '')}\n"
        f"Body:\n{email_data.get('body', '')}\n"
    )

    for model in models:
        print(f"[*] Trying model: {model}")
        try:
            text = _call_gemini_api(api_key, model, system_prompt, user_prompt)
            print(f"[✓] Success with model: {model}")
            return parse_llm_json(text)
        except HTTPError as e:
            error_body = e.read().decode("utf-8")
            error_data = json.loads(error_body)
            code = error_data.get("error", {}).get("code", 0)
            print(f"[!] Model {model} failed with code {code}")
            if code in (429, 503):
                print(f"    → Rate limited or unavailable, trying next model...")
                time.sleep(2)
                continue
            print(f"    → Unrecoverable error: {error_body}")
            return None

    print("[CRITICAL] All available models failed. Cannot analyze email.")
    return None

def analyze_email(email_data):
    try:
        result = _call_llm(email_data)
        if result:
            return result
    except Exception as e:
        print(f"Error reading email with LLM: {e}")
    return {"is_meeting": False}