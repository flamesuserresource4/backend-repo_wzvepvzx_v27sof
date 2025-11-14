from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from database import create_document, get_documents, db

app = FastAPI(title="iZakCode Portfolio API", version="1.0.0")

# CORS for dev/preview
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ContactMessageModel(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    message: str = Field(..., min_length=10, max_length=3000)
    source: Optional[str] = Field(None, description="Where the message came from, e.g. landing/contact")


@app.get("/")
async def root():
    return {"status": "ok", "name": "iZakCode Portfolio API"}


@app.get("/test")
async def test_db():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    try:
        _ = db.list_collection_names()
        return {"status": "ok", "db": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/contact")
async def submit_contact(msg: ContactMessageModel):
    try:
        doc_id = create_document("contactmessage", msg)
        return {"ok": True, "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/contact")
async def list_recent_contact(limit: int = 10):
    try:
        docs = get_documents("contactmessage", {}, limit)
        for d in docs:
            if "_id" in d:
                d["_id"] = str(d["_id"]) 
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
