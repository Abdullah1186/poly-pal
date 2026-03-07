import os
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from twilio.rest import Client as TwilioClient
from db import supabase
from tools import build_user_tools

llm = ChatAnthropic(model="claude-haiku-4-5-20251001")

SYSTEM_PROMPT = (
    "You are a friendly, encouraging language tutor on WhatsApp. "
    "Keep messages concise — this is a chat app, not an essay. "
    "Mix in the target language naturally and gently correct mistakes. "
    "Use your tools to quiz the user, track their progress, and personalise practice."
)


async def handle_whatsapp_message(phone: str, body: str):
    twilio = TwilioClient(os.environ["TWILIO_SID"], os.environ["TWILIO_AUTH_TOKEN"])
    whatsapp_number = os.environ["TWILIO_WHATSAPP_NUMBER"]

    # Look up the user — maybe_single() returns None instead of raising when 0 rows
    result = (
        supabase.table("users")
        .select("language")
        .eq("phone", phone)
        .maybe_single()
        .execute()
    )
    if not result or not result.data:
        twilio.messages.create(
            from_=f"whatsapp:{whatsapp_number}",
            to=phone,
            body="You are not registered yet. Please visit the app to sign up first.",
        )
        return

    language = result.data["language"]

    # Load last 20 messages for context
    history_result = (
        supabase.table("messages")
        .select("role, content")
        .eq("phone", phone)
        .order("created_at", desc=False)
        .limit(20)
        .execute()
    )
    history = history_result.data or []

    chat_history = [
        HumanMessage(content=m["content"]) if m["role"] == "user"
        else AIMessage(content=m["content"])
        for m in history
    ]

    # Build and run agent
    tools = build_user_tools(phone, language)
    agent = create_react_agent(llm, tools, prompt=SYSTEM_PROMPT)

    agent_result = agent.invoke({
        "messages": [*chat_history, HumanMessage(content=body)],
    })

    last_message = agent_result["messages"][-1]
    reply_text = last_message.content if isinstance(last_message.content, str) else str(last_message.content)

    # Persist both sides of the conversation
    supabase.table("messages").insert([
        {"phone": phone, "role": "user", "content": body},
        {"phone": phone, "role": "assistant", "content": reply_text},
    ]).execute()

    twilio.messages.create(
        from_=f"whatsapp:{whatsapp_number}",
        to=phone,
        body=reply_text,
    )
