import json
import os
from openai import AsyncOpenAI

_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client


INTENT_SYSTEM_PROMPT = """You are a parameter extractor for a Ticketmaster search assistant.
Extract the following from the user's message and conversation history, then return ONLY valid JSON with no extra text:
{
  "intent": "event_discovery" | "event_detail" | "faq" | "purchase" | "escalation" | "refine_search" | "clarify" | "other",
  "genre": string or null,
  "city": string or null,
  "keyword": string or null,
  "event_id": string or null,
  "dateRange": { "start": "YYYY-MM-DD", "end": "YYYY-MM-DD" } or null
}

Intent definitions:
- event_discovery: user wants to find events AND has enough info to search (at minimum a city or genre or keyword)
- refine_search: user wants to modify a previous search (cheaper, different date, same city etc.)
- event_detail: user wants more info about a specific event (use event_id if mentioned)
- faq: user has a policy or general question (refunds, transfers, fees, will call, etc.)
- purchase: user wants to buy tickets
- escalation: user wants to speak to a human or is frustrated
- clarify: the user's event request is too vague to search — no city, genre, keyword, or date can be extracted. Use this when the query is open-ended (e.g. "what's good?", "show me events", "something fun") and there is no prior search context to fall back on
- other: anything else unrelated to events or Ticketmaster

Today's date is injected by the system at runtime."""

RESPONSE_SYSTEM_PROMPT = """You are a friendly, helpful Ticketmaster assistant.
Answer the user's question using ONLY the context data provided below.
Do not invent events, prices, or dates. If data is missing, say so honestly.
Keep responses concise and conversational. Use emojis sparingly — at most one per response.

Context data:
{context}"""

PURCHASE_PROMPT = """You are a Ticketmaster assistant guiding a user through a simulated ticket purchase.
This is DEMO MODE — no real transaction will occur. Make this clear to the user.
Walk the user through: confirming the event → seat category → quantity → order summary → demo payment screen.
Keep it realistic but always label it as [DEMO MODE]."""

ESCALATION_PROMPT = """You are a Ticketmaster assistant. The user wants to speak with a human agent.
Respond warmly, acknowledge their request, and say: 'I'm connecting you to a Ticketmaster specialist now. Estimated wait time: 2 minutes.'
This is a DEMO — no real agent is being connected. Label the handoff clearly."""

CLARIFY_PROMPT = """You are a friendly Ticketmaster assistant. The user wants to find events but hasn't given you enough to search on.
Ask ONE focused follow-up question to get what you need. Keep it short and conversational.
Good clarifying questions cover: city or location, type of event or genre, preferred date or time range, or a specific artist/team they have in mind.
Do not ask multiple questions at once. Pick the single most important missing detail."""


async def extract_intent(message: str, history: list[dict], today: str) -> dict:
    system = INTENT_SYSTEM_PROMPT + f"\n\nToday's date: {today}"
    messages = [{"role": "system", "content": system}]
    messages.extend(history[-6:])
    messages.append({"role": "user", "content": message})

    response = await get_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"intent": "other"}


async def generate_response(
    message: str,
    history: list[dict],
    context: str,
    intent: str,
) -> str:
    if intent == "purchase":
        system = PURCHASE_PROMPT
    elif intent == "escalation":
        system = ESCALATION_PROMPT
    elif intent == "clarify":
        system = CLARIFY_PROMPT
    else:
        system = RESPONSE_SYSTEM_PROMPT.format(context=context or "No additional context available.")

    messages = [{"role": "system", "content": system}]
    messages.extend(history[-6:])
    messages.append({"role": "user", "content": message})

    response = await get_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
    )
    return response.choices[0].message.content
