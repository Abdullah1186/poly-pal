from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from twilio.rest import Client as TwilioClient
import os
from db import supabase

llm = ChatAnthropic(model="claude-haiku-4-5-20251001")


async def send_word_of_day():
    twilio = TwilioClient(os.environ["TWILIO_SID"], os.environ["TWILIO_AUTH_TOKEN"])
    whatsapp_number = os.environ["TWILIO_WHATSAPP_NUMBER"]

    result = supabase.table("users").select("phone, language").execute()
    users = result.data or []

    for user in users:
        response = llm.invoke([
            HumanMessage(
                f"Give a single interesting {user['language']} word of the day for a language learner. "
                f"Format: the word in {user['language']}, its pronunciation, its English meaning, "
                f"and one example sentence. Keep it short."
            )
        ])
        text = response.content if isinstance(response.content, str) else str(response.content)

        twilio.messages.create(
            from_=f"whatsapp:{whatsapp_number}",
            to=user["phone"],
            body=f"📖 *Word of the Day*\n\n{text}",
        )
