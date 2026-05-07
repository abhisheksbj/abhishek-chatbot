# Ticketmaster AI Chatbot — Prototype
**Stage 1 of 2 | Solo Developer | Local Development**

---

## What We Are Building

An AI-powered chatbot prototype for Ticketmaster. Users interact via a chat interface, ask questions in natural language, and get real event data back — smarter than a search bar, more conversational than a filter form.

This is Stage 1 only. No real purchases, no order tracking, no user accounts. The goal is to demonstrate the AI + Discovery API layer to the client and get approval for Stage 2.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python — FastAPI |
| AI | OpenAI API — model: `gpt-4o` |
| Event Data | Ticketmaster Discovery API (free tier) |
| Knowledge Base | In-memory vector store (no external DB needed for prototype) |
| Frontend | Plain HTML + JS chat widget (keep it simple for prototype) |
| Hosting | Local only for now (`uvicorn` dev server) |

---

## Project Structure

```
ticketmaster-chatbot/
├── main.py                  # FastAPI app entry point
├── routers/
│   └── chat.py              # POST /chat endpoint
├── services/
│   ├── ai.py                # OpenAI calls — intent extraction + response generation
│   ├── ticketmaster.py      # Ticketmaster Discovery API calls
│   └── knowledge_base.py    # In-memory FAQ/policy store + search
├── models/
│   └── schemas.py           # Pydantic models — ChatMessage, ChatResponse, etc.
├── static/
│   └── index.html           # Simple chat UI (HTML + JS, no framework needed)
├── .env                     # API keys — never commit this
├── .env.example             # Template for .env
├── requirements.txt
└── CLAUDE.md                # This file
```

---

## Environment Variables

Create a `.env` file in the root with:

```
OPENAI_API_KEY=your_openai_key_here
TM_API_KEY=your_ticketmaster_consumer_key_here
```

Never commit `.env`. Add it to `.gitignore` immediately.

---

## Features to Build (In Priority Order)

### 1. Natural Language Event Search ← build this first
- User sends: `"Rock concerts in Chicago next month"`
- `ai.py` calls OpenAI to extract: `{ intent, genre, city, dateRange }`
- `ticketmaster.py` calls Discovery API with those params
- `ai.py` formats the results into a conversational response
- Return to user

### 2. Conversational Refinement
- Bot maintains `conversation_history` in session state
- User can follow up: `"Something cheaper"` or `"Earlier in the month"`
- Backend passes full history to OpenAI on each call so context is preserved

### 3. Smart Recommendations
- User states a preference: `"I like indie music, what's good this weekend?"`
- AI interprets and queries TM API — same flow as #1 but more open-ended
- AI adds context to results: venue size, trending status, etc.

### 4. Event Deep Dive
- User picks an event and asks follow-ups: `"Tell me more about the venue"`
- Pull event details from TM API
- Answer venue/policy questions from the in-memory knowledge base

### 5. FAQ / Policy Answers
- Simple keyword or embedding-based search over a static list of Q&A pairs
- Load from a `knowledge_base.py` dict at startup
- AI generates a natural answer from the matched content

### 6. Simulated Purchase Flow (mock only)
- After event discovery, user says `"I want 2 tickets"`
- Bot walks through: seat category → quantity → order summary → "Demo Mode" payment screen
- No real transaction. Clearly label everything as demo.

### 7. Escalation Simulation (mock only)
- Trigger: user says `"I want to speak to someone"` or `"this isn't helping"`
- Bot responds: `"Connecting you to a specialist. Average wait: 2 minutes."`
- Log the full conversation transcript to console/file
- No real agent. Clearly label as demo.

---

## How the AI Layer Works

Two-call pattern for event search:

**Call 1 — Extract intent and parameters (structured output)**
```python
system_prompt = """
You are a parameter extractor for a Ticketmaster search assistant.
Extract the following from the user's message and return ONLY valid JSON:
{
  "intent": "event_discovery" | "event_detail" | "faq" | "purchase" | "escalation" | "refine_search" | "other",
  "genre": string or null,
  "city": string or null,
  "keyword": string or null,
  "dateRange": { "start": "YYYY-MM-DD", "end": "YYYY-MM-DD" } or null
}
"""
```

**Call 2 — Generate conversational response (after TM API call)**
```python
system_prompt = """
You are a friendly, helpful Ticketmaster assistant.
Answer the user's question using ONLY the event data provided below.
Do not invent events, prices, or dates. If data is missing, say so honestly.
Keep responses concise and conversational. Use emojis sparingly.

Event data:
{tm_api_results}
"""
```

---

## Ticketmaster Discovery API — Key Endpoints

Base URL: `https://app.ticketmaster.com/discovery/v2/`

**Search events:**
```
GET /events.json
  ?apikey={TM_API_KEY}
  &city={city}
  &classificationName={genre}
  &startDateTime={YYYY-MM-DDTHH:MM:SSZ}
  &endDateTime={YYYY-MM-DDTHH:MM:SSZ}
  &keyword={keyword}
  &size=5
```

**Get event details:**
```
GET /events/{eventId}.json?apikey={TM_API_KEY}
```

**Rate limits:** 5000 calls/day, 5 requests/second. More than enough for prototype.

---

## Session / Conversation State

Use a simple in-memory dict for prototype (no database needed):

```python
# In memory — resets on server restart, fine for prototype
sessions = {}  # { session_id: { "history": [], "last_search": {} } }
```

Each chat message appends to `history`. Pass full history to OpenAI on every call so the model has context for refinement queries.

Generate `session_id` on first message, return it to frontend, frontend sends it back on every subsequent message.

---

## In-Memory Knowledge Base (for FAQ)

Hardcode a list of Q&A pairs at startup:

```python
knowledge_base = [
    {
        "q": "What is the refund policy?",
        "a": "Ticketmaster's standard policy is no refunds unless the event is cancelled or postponed. Some events offer refund protection at purchase."
    },
    {
        "q": "Can I transfer my tickets?",
        "a": "Yes, most tickets can be transferred digitally via your Ticketmaster account."
    },
    # Add more...
]
```

For prototype, simple keyword matching is fine. No embeddings needed unless time permits.

---

## Frontend (Keep It Simple)

Single `static/index.html` file. No React, no build step. Just:
- A chat message list (scrollable div)
- A text input + send button
- Vanilla JS `fetch()` to POST to `/chat`
- Show "typing..." indicator while waiting
- Show a `[DEMO MODE]` badge on simulated purchase and escalation screens

Serve it from FastAPI:
```python
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="static", html=True), name="static")
```

---

## What NOT to Build in This Stage

- No user authentication / login
- No real payment processing
- No real order lookup
- No external vector database (Pinecone etc.) — in-memory only
- No deployment / cloud hosting — local only
- No mobile app
- No real human agent integration

---

## Running the App

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# Open http://localhost:8000
```

---

## Definition of Done for Prototype

The prototype is ready to demo when:
1. User can type a natural language event query and get real TM results back
2. User can refine results in follow-up messages without repeating themselves
3. User can ask a FAQ question and get a grounded answer
4. Simulated purchase flow is walkable end-to-end (even if mocked)
5. Escalation trigger works and shows handoff message
6. No crashes on common inputs. Graceful error messages on API failures.

---

## Stage 2 (Do Not Build Now)

When client approves prototype, Stage 2 adds:
- Ticketmaster Commerce API (real purchase, seat maps, orders)
- User authentication (OAuth)
- CRM / purchase history for personalisation
- Real payment gateway (Stripe)
- Live agent handoff (Zendesk / Intercom)
- Production hosting (cloud)
- Proper vector DB (Pinecone / Weaviate)

---

## Notes

- If OpenAI calls feel slow during testing, swap `gpt-4o` to `gpt-4o-mini` for faster/cheaper iteration. Switch back to `gpt-4o` for the client demo.
- If TM API returns no results for a query, tell the user honestly — do not hallucinate events.
- Keep all prompts in `services/ai.py` — do not scatter them across files.
- Commit frequently. One feature at a time.
