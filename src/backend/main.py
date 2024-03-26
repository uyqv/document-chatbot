import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from chain import ChatbotWithHistory

"""
FastAPI Chatbot Backend:
- Manages chat sessions (start, terminate, process messages).
- Allows all origins via CORS for web compatibility.
- Configured logging and runs on Uvicorn ASGI server.
"""

app = FastAPI()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
chatbot = ChatbotWithHistory()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Query(BaseModel):
    text: str


@app.post("/chat/")
async def chat(query: Query):
    global chatbot
    try:
        if query.text.strip().lower() == "new conversation":
            chatbot.terminate_conversation()
            chatbot = ChatbotWithHistory()
            return {"response": "Conversation reset successfully."}
        else:
            response = chatbot.process_query(query.text)
            return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("shutdown")
def shutdown_event():
    chatbot.terminate_conversation()
    logging.info("Server is shutting down: chatbot conversations terminated.")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
