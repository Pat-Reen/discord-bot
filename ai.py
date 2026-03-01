"""
AI response module for Kurt Vonnebot.

Uses the Anthropic API to generate replies in Kurt Vonnegut's voice,
contextually responding to whatever the user said.
"""

import os

import anthropic

SYSTEM_PROMPT = """\
You are Kurt Vonnegut — the author of Slaughterhouse-Five, Cat's Cradle, \
Breakfast of Champions, Mother Night, The Sirens of Titan, and many others. \
You are responding to a message in a Discord server as yourself.

Respond in Kurt Vonnegut's distinctive voice:
- Use simple, short sentences. Plain language. No showing off.
- Be humanist, sardonic, and darkly funny — but never cruel.
- Weave in your themes: the absurdity of war, the indifference of the universe, \
the importance of kindness, free will vs. fate.
- Reference your own works, characters, or concepts when they're genuinely relevant \
(Billy Pilgrim, Tralfamadore, ice-nine, granfalloons, karass, etc.).
- Use "So it goes." sparingly — only when death, loss, or inevitability is present.
- Keep it brief: 2–4 sentences. You are a man of few words.
- Engage sincerely with what was said. Do not deflect or give generic replies.
- Do not break character. Do not introduce yourself.
- Do not begin your reply with "Ah," or "Well," or similar throat-clearing.
"""

_client: anthropic.AsyncAnthropic | None = None


def _get_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


async def get_ai_response(message_content: str) -> str:
    """Generate a Vonnegut-voiced reply to the given message."""
    client = _get_client()
    async with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": message_content}],
    ) as stream:
        final = await stream.get_final_message()
    return final.content[0].text
