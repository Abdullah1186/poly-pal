from langchain_core.tools import tool
from db import supabase


def build_user_tools(phone: str, language: str):
    """Return LangChain tools bound to a specific user."""

    @tool
    def save_progress(word: str, correct: bool) -> str:
        """
        Call this after the user answers a vocabulary or translation quiz
        to record whether they got it right. Use it every time you give a
        word quiz and the user responds.
        """
        # Fetch existing row if any
        result = (
            supabase.table("user_progress")
            .select("times_seen, times_correct")
            .eq("phone", phone)
            .eq("word", word)
            .single()
            .execute()
        )
        existing = result.data or {}
        times_seen = (existing.get("times_seen") or 0) + 1
        times_correct = (existing.get("times_correct") or 0) + (1 if correct else 0)

        supabase.table("user_progress").upsert(
            {
                "phone": phone,
                "word": word,
                "language": language,
                "times_seen": times_seen,
                "times_correct": times_correct,
            },
            on_conflict="phone,word",
        ).execute()

        return (
            f'Great — marked "{word}" as correct. Keep it up!'
            if correct
            else f'Noted — "{word}" needs more practice.'
        )

    @tool
    def get_weak_words(limit: int = 5) -> str:
        """
        Fetch the words this user has struggled with most.
        Use this to decide what to quiz the user on next or to tailor exercises.
        limit: how many weak words to retrieve (1-10).
        """
        result = (
            supabase.table("user_progress")
            .select("word, times_seen, times_correct")
            .eq("phone", phone)
            .eq("language", language)
            .order("times_correct", desc=False)
            .limit(max(1, min(limit, 10)))
            .execute()
        )
        rows = result.data or []
        if not rows:
            return "No progress data yet — the user is just getting started."
        return "\n".join(
            f'"{r["word"]}" — seen {r["times_seen"]}x, correct {r["times_correct"]}x'
            for r in rows
        )

    @tool
    def generate_exercise(type: str, topic: str = "") -> str:
        """
        Generate a language exercise for the user.
        Use this when the user asks to be quizzed, wants practice,
        or when you decide a drill would help.
        type: one of 'translation', 'fill_in', or 'multiple_choice'.
        topic: optional topic focus e.g. 'food', 'travel', 'greetings'.
        """
        labels = {
            "translation": "a translation challenge (give an English phrase, ask for the translation)",
            "fill_in": "a fill-in-the-blank sentence",
            "multiple_choice": "a multiple-choice vocab question with 4 options (a/b/c/d)",
        }
        desc = labels.get(type, "a short vocabulary quiz")
        topic_hint = f" focused on the topic: {topic}" if topic else ""
        return f"Generate {desc} in {language}{topic_hint}. Keep it short and suitable for WhatsApp."

    return [save_progress, get_weak_words, generate_exercise]
