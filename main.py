from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

from routers.chat import router as chat_router

# Load environment variables
load_dotenv()

# Create FastAPI app only ONCE
app = FastAPI(title="Ticketmaster AI Chatbot")

# ==============================
# ENVIRONMENT VARIABLE TEST API
# ==============================
@app.get("/env-test")
def env_test():
    return {
        "openai": bool(os.getenv("OPENAI_API_KEY")),
        "ticketmaster": bool(os.getenv("TICKETMASTER_API_KEY"))
    }

# ==============================
# CHAT ROUTER
# ==============================
app.include_router(chat_router)

# ==============================
# STATIC FILES / HOME PAGE
# ==============================
app.mount("/", StaticFiles(directory="static", html=True), name="static")