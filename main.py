import sharedVars
import traceback
import re
import json
import requests

from datetime import datetime
import pytz

import discordIntegration
import NotionAPI
from ics import Calendar

ICS_URL = sharedVars.getConfig("ICS_URL")

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip().lower()


def to_eastern(utc_str: str) -> str:
    if not utc_str:
        return ""
    try:
        dt_utc = datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
        eastern = pytz.timezone("America/New_York")
        return dt_utc.astimezone(eastern).isoformat()
    except Exception:
        return utc_str


def getEventsFromICS():
    response = requests.get(ICS_URL)
    print("ICS URL being used:", ICS_URL)
    response.raise_for_status()
    
    cal = Calendar(response.text)
    events = []

    ASSIGNMENT_KEYWORDS = {
        "assignment", "hw", "homework", "quiz",
        "exam", "test", "midterm", "final",
        "lab", "project", "paper", "ps", "submit", "reflection",
        "presentation", "speech", "submission", "due", "turn in", "respond"
    }

    DESCRIPTION_KEYWORDS = {
        "submit", "due", "upload", "gradescope",
        "brightspace", "turn in", "respond", "reflection",
        "presentation", "speech", "submission", "due", "turn in", "respond"
    }

    eastern = pytz.timezone("America/New_York")
    now = datetime.now(eastern)

    for event in cal.events:
        title = (event.name or "").lower()
        desc = (event.description or "").lower()

        #Assignment title filter
        score = 0
        if any(k in title for k in ASSIGNMENT_KEYWORDS):
            score += 2

        #duration
        if not event.end or not event.begin:
            score += 1
        else:
            duration = event.end - event.begin
            if duration.total_seconds() > 2 * 60 * 60:
                score += 1

        #Description signal
        if any(k in desc for k in DESCRIPTION_KEYWORDS):
            score += 1

        if score < 2:
            continue

        #Deadline extraction
        if not event.begin:
            continue

        deadline_utc = event.begin.astimezone(pytz.utc)
        deadline_eastern = deadline_utc.astimezone(eastern)

        #Skip past events
        if deadline_eastern < now:
            continue

        #Course code extraction
        course_code = extract_course_code(
            event.name,
            event.description,
            event.location
        )


        events.append({
            "Assignment Name": event.name or "Untitled Assignment",
            "Deadline": deadline_utc.isoformat(),
            "Course Code": course_code,
            "EventID": event.uid
        })

    sharedVars.EVENTS = events


def extract_course_code(title: str = "", description: str = "", location: str = "") -> str:
    text = f"{location or ''} {title or ''} {description or ''}".upper()

    patterns = [
        r"\b([A-Z]{2,4})\s*[-:]?\s*(\d{3})\b",   # AMS210, AMS 210, AMS-210
        r"\b([A-Z]{2,4})\s*(\d{2}[A-Z])\b",     # BIO 203L
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return f"{match.group(1)} {match.group(2)}"

    return "UNKNOWN"


def EventsToNotion():
    l = open("discordLogs.log", "w", encoding="utf-8")

    try:
        #D2L ICS instead of Google Calendar
        getEventsFromICS()

        existing_event_ids = set()

        #Loads existing assignments in Notion
        for assignment in NotionAPI.getAssignments(NotionAPI.dbID):
            if assignment["properties"]["EventID"]["rich_text"]:
                eventid = assignment["properties"]["EventID"]["rich_text"][0]["text"]["content"]
                existing_event_ids.add(normalize(eventid))

        #New events loading and removing of already existing ones.
        for event in sharedVars.EVENTS[:]:
            event_id = event.get("EventID", "")
            name = event.get("Assignment Name", "")
            course_code = event.get("Course Code", "")
            deadline = event.get("Deadline", "")

            deadline_eastern = to_eastern(deadline)

            if normalize(event_id) in existing_event_ids:
                print(f"Skipping duplicate (EventID): {name}\n", file=l)
                sharedVars.EVENTS.remove(event)
                continue


            NotionAPI.createAssignment(
                NotionAPI.dbID,
                name,
                course_code,
                deadline_eastern,
                event_id
            )

            print(f"Created new assignment: {name}\n", file=l)
            existing_event_ids.add(normalize(event_id))
            sharedVars.EVENTS.remove(event)

        l.close()

    except Exception as error:
        print("Error caught:", error)
        traceback.print_exc()

    try:
        discordIntegration.runBot()
    except Exception as error:
        print(error)
        traceback.print_exc()

EventsToNotion()