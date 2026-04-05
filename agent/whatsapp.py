from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception
from anthropic import InternalServerError
from langchain_mcp_adapters.client import MultiServerMCPClient
from db import supabase
from tools import build_user_tools
from messenger import send_whatsapp

MCP_CONFIG = {
    "language-learn-mcp": {
        "url": "https://language-learn-mcp-production.up.railway.app/sse",
        "transport": "sse",
    }
}

llm = ChatAnthropic(model="claude-haiku-4-5-20251001")

# How much of the target language to use at each CEFR level
LEVEL_GUIDANCE = {
    'A1': 'Write almost entirely in English. Sprinkle in single target-language words or very short phrases (greetings, numbers, colours). Always translate anything you say in the target language immediately afterwards.',
    'A2': 'Write mostly in English. Include short simple sentences in the target language — greetings, basic questions, simple statements. Always follow with an English translation in brackets.',
    'B1': 'Mix English and the target language roughly 50/50. Use the target language for straightforward sentences and switch to English for anything complex. Provide translations for new or tricky vocabulary.',
    'B2': 'Write mainly in the target language. Use English only to clarify genuinely difficult concepts or vocabulary. Do not translate unless the user seems confused.',
    'C1': 'Write almost entirely in the target language. Use English only very occasionally for nuanced explanation. Treat the user as a confident speaker.',
    'C2': 'Write entirely in the target language. Treat the user as near-native. Never translate unless explicitly asked.',
}


def build_system_prompt(language: str, level: str) -> str:
    guidance = LEVEL_GUIDANCE.get(level, LEVEL_GUIDANCE['A1'])
    return (
        f"You are a friendly, curious pen pal who is a native {language} speaker. "
        f"You chat naturally about everyday life — your day, interests, culture, food, travel, opinions. "
        f"You are NOT a teacher or tutor. Never give formal lessons, grammar tables, or structured exercises. "
        f"If the user makes a mistake, correct it naturally and warmly in passing, the way a friend would, then move on. "
        f"The user's CEFR level is {level}. {guidance} "
        f"Always be the one to keep the conversation going — ask follow-up questions, share your own thoughts, suggest new topics. "
        f"Never ask the user what they want to practise or what topic they want. Just chat."
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
        .select("language, level")
        .eq("phone", phone)
        .maybe_single()
        .execute()
    )
    if not result or not result.data:
        send_whatsapp(phone, "You are not registered yet. Please visit the app to sign up first.")
        return

    language = result.data["language"]
    level = result.data.get("level", "A1")

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
        mcp_client = MultiServerMCPClient(MCP_CONFIG)
        mcp_tools = await mcp_client.get_tools()
        tools = build_user_tools(phone, language, level) + mcp_tools
        agent = create_react_agent(llm, tools, prompt=build_system_prompt(language, level))
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
