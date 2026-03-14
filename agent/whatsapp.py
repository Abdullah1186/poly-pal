from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception
from anthropic import InternalServerError
from db import supabase
from tools import build_user_tools
from messenger import send_whatsapp

llm = ChatAnthropic(model="claude-haiku-4-5-20251001")

def build_system_prompt(language: str) -> str:
    return (
        f"You are a friendly, encouraging WhatsApp tutor helping the user learn {language}. "
        f"You already know their target language is {language} — never ask them what they are learning. "
        f"Keep messages concise — this is WhatsApp, not an essay. "
        f"Converse naturally in both English and {language}. Gently correct mistakes. "
        f"Use your tools to run quizzes, track progress, and personalise practice. "
        f"When the user answers a quiz question, always call save_progress to record the result."
    )


def _is_overloaded(e: BaseException) -> bool:
    return isinstance(e, InternalServerError) and getattr(e, "status_code", None) == 529


@retry(
    retry=retry_if_exception(_is_overloaded),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    stop=stop_after_attempt(4),
)
def _run_agent(agent, messages):
    return agent.invoke({"messages": messages})


async def handle_whatsapp_message(phone: str, body: str):
    result = (
        supabase.table("users")
        .select("language")
        .eq("phone", phone)
        .maybe_single()
        .execute()
    )
    if not result or not result.data:
        send_whatsapp(phone, "You are not registered yet. Please visit the app to sign up first.")
        return

    language = result.data["language"]

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

    try:
        tools = build_user_tools(phone, language)
        agent = create_react_agent(llm, tools, prompt=build_system_prompt(language))
        agent_result = _run_agent(agent, [*chat_history, HumanMessage(content=body)])

        last_message = agent_result["messages"][-1]
        reply_text = last_message.content if isinstance(last_message.content, str) else str(last_message.content)

        supabase.table("messages").insert([
            {"phone": phone, "role": "user", "content": body},
            {"phone": phone, "role": "assistant", "content": reply_text},
        ]).execute()

        send_whatsapp(phone, reply_text)

    except Exception as e:
        print(f"Agent error: {e}")
        send_whatsapp(phone, "Sorry, I'm having a moment — try again in a few seconds!")
