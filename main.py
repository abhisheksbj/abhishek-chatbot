from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routers.chat import router as chat_router

app = FastAPI(title="Ticketmaster AI Chatbot")
app.include_router(chat_router)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
