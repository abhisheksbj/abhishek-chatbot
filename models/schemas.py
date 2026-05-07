from pydantic import BaseModel


class ChatMessage(BaseModel):
    session_id: str | None = None
    message: str


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    intent: str
