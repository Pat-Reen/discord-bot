"""
Kurt Vonnebot — A Reddit bot that replies to posts with Kurt Vonnegut quotes.

The bot monitors configured subreddits and replies when a post or comment
mentions Vonnegut, his books, or known trigger keywords.  It tracks which
items it has already replied to so it never double-posts.
"""

import logging
import os
import random
import time
from pathlib import Path

import praw
from dotenv import load_dotenv

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
REDDIT_CLIENT_ID = os.environ["REDDIT_CLIENT_ID"]
REDDIT_CLIENT_SECRET = os.environ["REDDIT_CLIENT_SECRET"]
REDDIT_USERNAME = os.environ["REDDIT_USERNAME"]
REDDIT_PASSWORD = os.environ["REDDIT_PASSWORD"]
REDDIT_USER_AGENT = os.environ.get(
    "REDDIT_USER_AGENT",
    f"script:KurtVonnebot:v1.0 (by u/{os.environ.get('REDDIT_USERNAME', 'vonnebot')})",
)

# Comma-separated list of subreddits to monitor, e.g. "books,literature,scifi"
SUBREDDITS = os.environ.get("SUBREDDITS", "books,literature,scifi,AskReddit").split(",")
SUBREDDITS = [s.strip() for s in SUBREDDITS]

# How many posts/comments to fetch per poll cycle
FETCH_LIMIT = int(os.environ.get("FETCH_LIMIT", "25"))

# Seconds to wait between poll cycles (Reddit rate-limit friendly default)
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", "60"))

# Reply to comments as well as posts?
REPLY_TO_COMMENTS = os.environ.get("REPLY_TO_COMMENTS", "true").lower() == "true"

# Path to the file that stores IDs of already-replied items
REPLIED_FILE = Path(os.environ.get("REPLIED_FILE", "replied.txt"))

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_replied_ids() -> set:
    """Load the set of Reddit IDs we have already replied to."""
    if not REPLIED_FILE.exists():
        return set()
    return set(REPLIED_FILE.read_text().splitlines())


def save_replied_id(item_id: str, replied_ids: set) -> None:
    """Persist a new ID to the replied file and add it to the in-memory set."""
    replied_ids.add(item_id)
    with REPLIED_FILE.open("a") as fh:
        fh.write(item_id + "\n")


def contains_keyword(text: str) -> bool:
    """Return True if *text* contains any Vonnegut-related keyword."""
    lowered = text.lower()
    return any(kw in lowered for kw in VONNEGUT_KEYWORDS)


def random_quote() -> dict:
    """Return a random quote dict with 'text' and 'source' keys."""
    return random.choice(QUOTES)


def format_reply(quote: dict) -> str:
    """Format a quote into a Reddit-friendly markdown reply."""
    return (
        f'> *"{quote["text"]}"*\n\n'
        f"— Kurt Vonnegut, **{quote['source']}**\n\n"
        "---\n"
        "^(I am Kurt Vonnebot. So it goes.)"
    )


def build_reddit() -> praw.Reddit:
    """Initialise and return an authenticated PRAW Reddit instance."""
    return praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        username=REDDIT_USERNAME,
        password=REDDIT_PASSWORD,
        user_agent=REDDIT_USER_AGENT,
    )


# ---------------------------------------------------------------------------
# Core bot logic
# ---------------------------------------------------------------------------

def process_submission(submission, replied_ids: set, reddit: praw.Reddit) -> None:
    """Reply to a submission (post) if it matches and hasn't been replied to."""
    if submission.id in replied_ids:
        return

    text = f"{submission.title} {submission.selftext}"
    if not contains_keyword(text):
        return

    quote = random_quote()
    reply_text = format_reply(quote)

    try:
        submission.reply(reply_text)
        save_replied_id(submission.id, replied_ids)
        log.info("Replied to submission %s: '%s'", submission.id, submission.title[:60])
    except praw.exceptions.APIException as exc:
        log.warning("API error replying to submission %s: %s", submission.id, exc)
    except Exception as exc:
        log.error("Unexpected error replying to submission %s: %s", submission.id, exc)


def process_comment(comment, replied_ids: set) -> None:
    """Reply to a comment if it matches and hasn't been replied to."""
    if comment.id in replied_ids:
        return

    # Don't reply to ourselves
    if comment.author and comment.author.name.lower() == REDDIT_USERNAME.lower():
        return

    if not contains_keyword(comment.body):
        return

    quote = random_quote()
    reply_text = format_reply(quote)

    try:
        comment.reply(reply_text)
        save_replied_id(comment.id, replied_ids)
        log.info("Replied to comment %s by u/%s", comment.id, comment.author)
    except praw.exceptions.APIException as exc:
        log.warning("API error replying to comment %s: %s", comment.id, exc)
    except Exception as exc:
        log.error("Unexpected error replying to comment %s: %s", comment.id, exc)


def run() -> None:
    """Main bot loop."""
    log.info("Starting Kurt Vonnebot…")
    log.info("Monitoring subreddits: %s", ", ".join(SUBREDDITS))

    reddit = build_reddit()
    replied_ids = load_replied_ids()
    subreddit = reddit.subreddit("+".join(SUBREDDITS))

    log.info("Logged in as u/%s", reddit.user.me())

    while True:
        try:
            # --- New submissions ---
            for submission in subreddit.new(limit=FETCH_LIMIT):
                process_submission(submission, replied_ids, reddit)

            # --- New comments (optional) ---
            if REPLY_TO_COMMENTS:
                for comment in subreddit.comments(limit=FETCH_LIMIT):
                    process_comment(comment, replied_ids)

        except praw.exceptions.PRAWException as exc:
            log.error("PRAW exception during poll: %s", exc)
        except Exception as exc:
            log.error("Unexpected exception during poll: %s", exc)

        log.debug("Sleeping %d seconds…", POLL_INTERVAL)
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    run()
