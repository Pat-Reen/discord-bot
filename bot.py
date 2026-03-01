"""
Kurt Vonnebot — A Discord bot that replies with Kurt Vonnegut quotes and AI responses.

The bot monitors messages for Vonnegut-related keywords and replies with either a
randomly selected quote or an AI-generated response in Vonnegut's voice. It also
exposes a /quote slash command for on-demand use.
"""

import logging
import os
import random

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from ai import get_ai_response
from quotes import QUOTES, VONNEGUT_KEYWORDS

load_dotenv()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("vonnebot.log"),
    ],
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config — read from environment variables (see .env.example)
# ---------------------------------------------------------------------------
DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]

# Optional: comma-separated channel IDs to watch for keyword triggers.
# Leave blank (or unset) to monitor every channel in every server.
_watch_raw = os.environ.get("WATCH_CHANNELS", "").strip()
WATCH_CHANNELS: set[int] = (
    {int(c.strip()) for c in _watch_raw.split(",") if c.strip()}
    if _watch_raw
    else set()
)

# ---------------------------------------------------------------------------
# Bot setup
# ---------------------------------------------------------------------------
intents = discord.Intents.default()
intents.message_content = True  # required to read message text

bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def contains_keyword(text: str) -> bool:
    """Return True if text contains any Vonnegut-related keyword."""
    lowered = text.lower()
    return any(kw in lowered for kw in VONNEGUT_KEYWORDS)


def random_quote() -> dict:
    """Return a random quote dict with 'text' and 'source' keys."""
    return random.choice(QUOTES)


def build_embed(quote: dict) -> discord.Embed:
    """Format a quote as a Discord embed."""
    embed = discord.Embed(
        description=f'*"{quote["text"]}"*',
        color=discord.Color.dark_gold(),
    )
    embed.set_footer(text=f'— Kurt Vonnegut, {quote["source"]}  |  So it goes.')
    return embed


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

@bot.event
async def on_ready():
    log.info("Logged in as %s (ID: %s)", bot.user, bot.user.id)
    try:
        synced = await bot.tree.sync()
        log.info("Synced %d slash command(s)", len(synced))
    except Exception as exc:
        log.error("Failed to sync slash commands: %s", exc)


@bot.event
async def on_message(message: discord.Message):
    # Never reply to ourselves
    if message.author == bot.user:
        return

    # If WATCH_CHANNELS is configured, ignore other channels
    if WATCH_CHANNELS and message.channel.id not in WATCH_CHANNELS:
        await bot.process_commands(message)
        return

    if contains_keyword(message.content):
        if random.random() < 0.5:
            # Return a quote
            quote = random_quote()
            await message.reply(embed=build_embed(quote), mention_author=False)
            log.info(
                "Quote reply to %s in #%s: %.60s",
                message.author,
                message.channel,
                message.content,
            )
        else:
            # Generate an AI response in Vonnegut's voice
            async with message.channel.typing():
                try:
                    response = await get_ai_response(message.content)
                    await message.reply(response, mention_author=False)
                    log.info(
                        "AI reply to %s in #%s: %.60s",
                        message.author,
                        message.channel,
                        message.content,
                    )
                except Exception as exc:
                    log.error("AI response failed, falling back to quote: %s", exc)
                    quote = random_quote()
                    await message.reply(embed=build_embed(quote), mention_author=False)

    # Allow prefix commands to still work
    await bot.process_commands(message)


# ---------------------------------------------------------------------------
# Slash commands
# ---------------------------------------------------------------------------

@bot.tree.command(name="quote", description="Get a random Kurt Vonnegut quote")
async def quote_command(interaction: discord.Interaction):
    quote = random_quote()
    await interaction.response.send_message(embed=build_embed(quote))
    log.info("/quote used by %s in #%s", interaction.user, interaction.channel)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    log.info("Starting Kurt Vonnebot…")
    bot.run(DISCORD_TOKEN, log_handler=None)
