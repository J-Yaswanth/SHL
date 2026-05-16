from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Literal

from app.agent import get_agent_reply
from catalog import load_catalog

app = FastAPI()

# Load catalog once at startup
catalog = load_catalog("data/catalog.json")


# -----------------------------
# Request Models
# -----------------------------

class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]


# -----------------------------
# Response Models
# -----------------------------

class Recommendation(BaseModel):
    name: str
    url: str
    test_type: str


class ChatResponse(BaseModel):
    reply: str
    recommendations: List[Recommendation]
    end_of_conversation: bool


# -----------------------------
# Health Endpoint
# -----------------------------

@app.get("/health")
def health():

    if catalog:
        return {"status": "ok"}

    return {"status": "catalog_not_loaded"}


# -----------------------------
# Chat Endpoint
# -----------------------------

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    try:

        # Validate empty message list
        if not request.messages:
            raise HTTPException(
                status_code=400,
                detail="Messages cannot be empty"
            )

        # Convert Pydantic models to dictionaries
        messages = [m.dict() for m in request.messages]

        # Get agent response
        reply, recs, end_flag = get_agent_reply(
            messages,
            catalog
        )

        # Ensure maximum 10 recommendations
        recs = recs[:10]

        # Validate recommendation schema
        recommendations = [
            Recommendation(**rec)
            for rec in recs
        ]

        # Final response
        return ChatResponse(
            reply=reply,
            recommendations=recommendations,
            end_of_conversation=end_flag
        )

    except HTTPException:
        raise

    except Exception:

        # Avoid exposing internal errors
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
