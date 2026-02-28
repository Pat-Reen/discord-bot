# Kurt Vonnebot

A Reddit bot that replies to posts and comments with quotes from Kurt Vonnegut's books.

So it goes.

---

## How it works

Vonnebot monitors one or more subreddits for new posts and comments. When it
finds text that mentions Vonnegut, his books, or related keywords
(`slaughterhouse-five`, `billy pilgrim`, `tralfamadore`, `so it goes`, …), it
replies with a randomly selected Vonnegut quote, attributed to its source.

Example reply:

> *"Hello, babies. Welcome to Earth. It's hot in the summer and cold in the
> winter. It's round and wet and crowded. At the outside, babies, you've got
> about a hundred years here. There's only one rule that I know of, babies —
> God damn it, you've got to be kind."*
>
> — Kurt Vonnegut, **God Bless You, Mr. Rosewater**
>
> ---
> ^(I am Kurt Vonnebot. So it goes.)

---

## Setup

### 1. Create a Reddit app

1. Go to <https://www.reddit.com/prefs/apps> and click **create another app**.
2. Choose **script** as the app type.
3. Note your **client ID** (under the app name) and **client secret**.

### 2. Create a bot Reddit account

Register a separate Reddit account for the bot (e.g. `u/KurtVonnebot`).

### 3. Clone and install

```bash
git clone <repo-url>
cd reddit-bot
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

| Variable | Description |
|---|---|
| `REDDIT_CLIENT_ID` | App client ID from reddit.com/prefs/apps |
| `REDDIT_CLIENT_SECRET` | App client secret |
| `REDDIT_USERNAME` | Bot account username |
| `REDDIT_PASSWORD` | Bot account password |
| `SUBREDDITS` | Comma-separated list of subreddits to monitor |
| `FETCH_LIMIT` | Posts/comments fetched per cycle (default `25`) |
| `POLL_INTERVAL` | Seconds between cycles (default `60`) |
| `REPLY_TO_COMMENTS` | `true` to reply to comments too (default `true`) |
| `REPLIED_FILE` | Path to ID-tracking file (default `replied.txt`) |

### 5. Run

```bash
python bot.py
```

The bot logs activity to both the terminal and `vonnebot.log`.

---

## Project structure

```
reddit-bot/
├── bot.py          # Main bot loop and Reddit logic
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

To add new trigger keywords, append to the `VONNEGUT_KEYWORDS` list in the
same file.

---

## Notes

- Reddit's API rate-limits bots to roughly 60 requests per minute.  The
  default `POLL_INTERVAL=60` keeps the bot well within limits.
- Vonnebot never replies to its own comments, and it tracks replied IDs in
  `replied.txt` to avoid duplicate replies across restarts.
- Avoid adding the bot to very large, active subreddits without adjusting
  `FETCH_LIMIT` and `POLL_INTERVAL` accordingly.
