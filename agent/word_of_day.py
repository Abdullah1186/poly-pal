from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from db import supabase
from messenger import send_whatsapp

llm = ChatAnthropic(model="claude-haiku-4-5-20251001")


async def send_word_of_day():
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
        send_whatsapp(user["phone"], f"📖 *Word of the Day*\n\n{text}")
