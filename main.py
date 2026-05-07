from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI()

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
# STATIC FILES
# ==============================
app.mount("/static", StaticFiles(directory="static"), name="static")

# ==============================
# HOME PAGE
# ==============================
@app.get("/")
async def root():
    return FileResponse("static/index.html")


# =================================================================
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routers.chat import router as chat_router

app = FastAPI(title="Ticketmaster AI Chatbot")
app.include_router(chat_router)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
