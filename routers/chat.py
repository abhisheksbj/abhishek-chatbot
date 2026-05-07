import json
import uuid
from datetime import date

from fastapi import APIRouter, HTTPException

from models.schemas import ChatMessage, ChatResponse
from services import ai, ticketmaster
from services.knowledge_base import search as kb_search

router = APIRouter()

# In-memory session store — resets on server restart, fine for prototype
sessions: dict[str, dict] = {}


def _get_session(session_id: str | None) -> tuple[str, dict]:
    if not session_id or session_id not in sessions:
        session_id = str(uuid.uuid4())
        sessions[session_id] = {"history": [], "last_search": {}}
    return session_id, sessions[session_id]


def _format_events(events: list[dict]) -> str:
    if not events:
        return "No events found."
    lines = []
    for i, e in enumerate(events, 1):
        line = f"{i}. {e['name']} — {e['date']}"
        if e.get("time"):
            line += f" at {e['time']}"
        line += f"\n   Venue: {e['venue']}, {e['city']}"
        line += f"\n   Price: {e['price']}"
        line += f"\n   Tickets: {e['url']}"
        line += f"\n   ID: {e['id']}"
        lines.append(line)
    return "\n\n".join(lines)


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatMessage) -> ChatResponse:
    session_id, session = _get_session(body.session_id)
    history = session["history"]
    last_search = session["last_search"]
    today = date.today().isoformat()

    # Extract intent + params
    try:
        params = await ai.extract_intent(body.message, history, today)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {e}")

    intent = params.get("intent", "other")
    context = ""

    try:
        if intent == "event_discovery":
            search_params = {
                "city": params.get("city"),
                "genre": params.get("genre"),
                "keyword": params.get("keyword"),
                "start_date": (params.get("dateRange") or {}).get("start"),
                "end_date": (params.get("dateRange") or {}).get("end"),
            }
            session["last_search"] = search_params
            events = await ticketmaster.search_events(**search_params)
            context = _format_events(events)
            if not events:
                context = "No events were found for that search. The user should be told honestly."

        elif intent == "refine_search":
            merged = {**last_search}
            if params.get("city"):
                merged["city"] = params["city"]
            if params.get("genre"):
                merged["genre"] = params["genre"]
            if params.get("keyword"):
                merged["keyword"] = params["keyword"]
            if params.get("dateRange"):
                merged["start_date"] = params["dateRange"].get("start")
                merged["end_date"] = params["dateRange"].get("end")
            session["last_search"] = merged
            events = await ticketmaster.search_events(**merged)
            context = _format_events(events)
            if not events:
                context = "No events were found after refining the search."

        elif intent == "event_detail":
            event_id = params.get("event_id")
            if event_id:
                event = await ticketmaster.get_event(event_id)
                context = json.dumps(event, indent=2) if event else "Event not found."
            else:
                context = "No specific event ID provided. Ask the user to clarify which event they mean."

        elif intent == "faq":
            matches = kb_search(body.message)
            if matches:
                context = "\n\n".join(f"Q: {m['q']}\nA: {m['a']}" for m in matches)
            else:
                context = "No matching FAQ entry found. Answer as best you can based on general Ticketmaster knowledge."

        elif intent in ("purchase", "escalation"):
            if intent == "escalation":
                _log_transcript(session_id, history, body.message)
            context = ""

        elif intent == "clarify":
            context = ""

        else:
            context = "The user's message does not match a known intent. Respond helpfully and ask them to clarify."

    except Exception as e:
        context = f"There was an error retrieving data: {e}. Tell the user there was a temporary issue and to try again."

    # Generate conversational response
    try:
        reply = await ai.generate_response(body.message, history, context, intent)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI response error: {e}")

    # Update history
    history.append({"role": "user", "content": body.message})
    history.append({"role": "assistant", "content": reply})

    # Keep history bounded to last 20 turns
    if len(history) > 20:
        session["history"] = history[-20:]

    return ChatResponse(session_id=session_id, reply=reply, intent=intent)


def _log_transcript(session_id: str, history: list[dict], final_message: str) -> None:
    print(f"\n--- ESCALATION TRANSCRIPT [{session_id}] ---")
    for turn in history:
        role = turn["role"].upper()
        print(f"{role}: {turn['content']}")
    print(f"USER: {final_message}")
    print("--- END TRANSCRIPT ---\n")
