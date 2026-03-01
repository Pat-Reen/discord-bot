# Kurt Vonnebot

A Discord bot that replies with Kurt Vonnegut quotes whenever someone mentions
him, his books, or related keywords. Also exposes a `/quote` slash command.

So it goes.

---

## How it works

Vonnebot listens to messages in your server. When it spots a Vonnegut-related
keyword (`slaughterhouse-five`, `billy pilgrim`, `tralfamadore`, `so it goes`, …),
it replies with a randomly selected quote as a Discord embed.

You can also summon a quote at any time with the `/quote` slash command.

Example reply:

> *"Hello, babies. Welcome to Earth. It's hot in the summer and cold in the
> winter. It's round and wet and crowded. At the outside, babies, you've got
> about a hundred years here. There's only one rule that I know of, babies —
> God damn it, you've got to be kind."*
>
> — Kurt Vonnegut, God Bless You, Mr. Rosewater  |  So it goes.

---

## Setup

### 1. Create a Discord application and bot

1. Go to <https://discord.com/developers/applications> and click **New Application**.
2. Give it a name (e.g. "KurtVonnebot"), then open the **Bot** tab.
3. Click **Add Bot** and confirm.
4. Under **Token**, click **Reset Token** and copy it — you'll need it in step 4.
5. Under **Privileged Gateway Intents**, enable **Message Content Intent**.

### 2. Invite the bot to your server

1. In your application, open the **OAuth2 → URL Generator** tab.
2. Under **Scopes**, check `bot` and `applications.commands`.
3. Under **Bot Permissions**, check at minimum:
   - `Read Messages / View Channels`
   - `Send Messages`
   - `Read Message History`
4. Copy the generated URL, open it in your browser, and add the bot to your server.

### 3. Clone and install

```bash
git clone <repo-url>
cd discord-bot
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your values:

| Variable | Description |
|---|---|
| `DISCORD_TOKEN` | Bot token from the Developer Portal |
| `WATCH_CHANNELS` | Comma-separated channel IDs to watch (blank = all channels) |

### 5. Run

```bash
python bot.py
```

The bot logs activity to both the terminal and `vonnebot.log`.

On first start it syncs the `/quote` slash command globally. Discord can take up
to an hour to propagate new slash commands across all servers — this is normal.

---

## Project structure

```
discord-bot/
├── bot.py          # Main bot logic (events + slash command)
├── quotes.py       # Vonnegut quotes and trigger keywords
├── requirements.txt
├── .env.example    # Template for credentials (never commit .env)
└── README.md
```

---

## Adding quotes

Open `quotes.py` and append a dict to the `QUOTES` list:

```python
{
    "text": "Your quote here.",
    "source": "Book Title",
},
```

To add new trigger keywords, append to `VONNEGUT_KEYWORDS` in the same file.
