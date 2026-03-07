import os
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv
from whatsapp import handle_whatsapp_message
from word_of_day import send_word_of_day

load_dotenv()

app = FastAPI()


@app.get("/webhook")
async def verify_webhook(request: Request):
    """Meta pings this once to verify the webhook URL is yours."""
    params = request.query_params
    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == os.environ.get("META_VERIFY_TOKEN")
    ):
        return PlainTextResponse(params.get("hub.challenge", ""))
    raise HTTPException(status_code=403)


@app.post("/webhook")
async def webhook(request: Request):
    """Receives incoming WhatsApp messages from Meta."""
    data = await request.json()

    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for message in value.get("messages", []):
                if message.get("type") == "text":
                    phone = message["from"]          # e.g. '447739863789'
                    body = message["text"]["body"]
                    await handle_whatsapp_message(phone=phone, body=body)

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
