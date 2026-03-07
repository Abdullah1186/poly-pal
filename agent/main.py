import os
from fastapi import FastAPI, Form, Header, HTTPException
from dotenv import load_dotenv
from whatsapp import handle_whatsapp_message
from word_of_day import send_word_of_day

load_dotenv()

app = FastAPI()


@app.post("/webhook")
async def webhook(From: str = Form(...), Body: str = Form(...)):
    """Twilio sends form-encoded POST requests."""
    await handle_whatsapp_message(phone=From, body=Body)
    return {}


@app.post("/cron/word-of-day")
async def cron_word_of_day(x_cron_secret: str = Header(None)):
    if x_cron_secret != os.environ.get("CRON_SECRET"):
        raise HTTPException(status_code=401)
    await send_word_of_day()
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
