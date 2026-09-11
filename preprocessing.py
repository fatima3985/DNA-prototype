"""
preprocessing.py
=================
Member 1 deliverable: Dataset + Sender Profiles

Pipeline:
1. Load raw Enron emails (Kaggle emails.csv format: columns ['file','message'])
2. Parse headers + body from each raw message
3. Clean body: strip quoted replies, signatures, HTML, forwarded blocks
4. Group cleaned emails by sender
5. Pick top N senders by email volume
6. Compute a stylometric profile per sender
7. Save dataset.csv (cleaned emails) and profiles.json (per-sender profiles)

Usage:
    python preprocessing.py

Requirements:
    pip install pandas beautifulsoup4
"""

import re
import json
import email
import string
from email import policy
from collections import Counter, defaultdict

import pandas as pd
from bs4 import BeautifulSoup

# --------------------------------------------------------------------------
# CONFIG — tweak these
# --------------------------------------------------------------------------
INPUT_CSV = "emails.csv"        # the Kaggle file
OUTPUT_DATASET_CSV = "dataset.csv"
OUTPUT_PROFILES_JSON = "profiles.json"

NUM_SENDERS = 15                # how many senders to keep (10-20 recommended)
MIN_EMAILS_PER_SENDER = 40      # ignore senders with too few emails for a reliable profile
MAX_EMAILS_PER_SENDER = 300     # cap so profile-building doesn't take forever
EXCLUDED_SENDERS = {"enron.announcements@enron.com", "no.address@enron.com","pete.davis@enron.com","outlook.team@enron.com"}

GREETING_PATTERNS = {
    "Hi": r"^\s*hi\b",
    "Hello": r"^\s*hello\b",
    "Dear": r"^\s*dear\b",
    "Hey": r"^\s*hey\b",
    "Good morning": r"^\s*good morning\b",
    "Good afternoon": r"^\s*good afternoon\b",
}

SIGNOFF_PATTERNS = {
    "Regards": r"regards\W*$",
    "Best": r"best\W*$",
    "Best regards": r"best regards\W*$",
    "Thanks": r"thanks\W*$",
    "Thank you": r"thank you\W*$",
    "Sincerely": r"sincerely\W*$",
    "Cheers": r"cheers\W*$",
}

# --------------------------------------------------------------------------
# STEP 1: PARSE RAW EMAIL -> (sender, subject, date, body)
# --------------------------------------------------------------------------

def parse_raw_email(raw_message: str):
    """Parse a raw RFC822-style email string into structured fields."""
    try:
        msg = email.message_from_string(raw_message, policy=policy.default)
    except Exception:
        return None

    sender = msg.get("From", "")
    subject = msg.get("Subject", "")
    date = msg.get("Date", "")

    # Extract plain text body (Enron corpus is almost entirely plain text,
    # but we handle multipart / html just in case)
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype == "text/plain":
                try:
                    body = part.get_content()
                except Exception:
                    pass
                break
        if not body:
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    try:
                        body = part.get_content()
                    except Exception:
                        pass
                    break
    else:
        try:
            body = msg.get_content()
        except Exception:
            body = raw_message

    # Normalize sender to a clean email address like "sarah@company.com"
    sender_match = re.search(r"[\w\.\-\+]+@[\w\.\-]+", sender)
    sender_clean = sender_match.group(0).lower() if sender_match else sender.strip().lower()

    return {
        "sender": sender_clean,
        "subject": subject.strip(),
        "date": date.strip(),
        "raw_body": body,
    }


# --------------------------------------------------------------------------
# STEP 2: CLEAN BODY — remove headers-in-body, quoted replies, signatures, HTML
# --------------------------------------------------------------------------

QUOTE_MARKERS = [
    r"^\s*-{2,}\s*Original Message\s*-{2,}",
    r"^\s*-{2,}\s*Forwarded by",
    r"^From:\s.*",
    r"^Sent:\s.*",
    r"^To:\s.*",
    r"^Cc:\s.*",
    r"^Subject:\s.*",
    r"^On .* wrote:\s*$",
]
QUOTE_MARKER_RE = re.compile("|".join(QUOTE_MARKERS), re.IGNORECASE)

SIGNATURE_MARKERS_RE = re.compile(
    r"^\s*(--+|Regards,|Best regards,|Sincerely,|Thanks,|Thank you,|Best,|Cheers,)\s*$",
    re.IGNORECASE,
)


def strip_html(text: str) -> str:
    if "<html" in text.lower() or "<div" in text.lower() or "<p>" in text.lower():
        return BeautifulSoup(text, "html.parser").get_text()
    return text


def clean_body(raw_body: str) -> str:
    text = strip_html(raw_body)

    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()

        # Stop entirely once we hit a quoted-reply block (everything after is old thread)
        if QUOTE_MARKER_RE.match(stripped):
            break

        # Lines that are clearly quoted (start with '>')
        if stripped.startswith(">"):
            continue

        # Keep the signoff line itself (e.g. "Thanks,") so it's still detectable,
        # but drop everything after it (name, phone, disclaimers, etc.)
        if SIGNATURE_MARKERS_RE.match(stripped):
            cleaned_lines.append(line)
            break

        cleaned_lines.append(line)

    cleaned = "\n".join(cleaned_lines).strip()

    # Collapse excessive blank lines / whitespace
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)

    return cleaned.strip()


# --------------------------------------------------------------------------
# STEP 3: LOAD + CLEAN ALL EMAILS
# --------------------------------------------------------------------------

def load_and_clean(input_csv: str) -> pd.DataFrame:
    print(f"Loading {input_csv} ...")
    df = pd.read_csv(input_csv)

    records = []
    for i, row in enumerate(df.itertuples(index=False)):
        parsed = parse_raw_email(row.message)
        if parsed is None or not parsed["sender"]:
            continue
        clean = clean_body(parsed["raw_body"])
        if len(clean.split()) < 5:
            continue  # skip near-empty emails
        records.append({
            "sender": parsed["sender"],
            "subject": parsed["subject"],
            "date": parsed["date"],
            "body": clean,
        })
        if i % 20000 == 0:
            print(f"  processed {i} raw rows...")

    out = pd.DataFrame(records)
    print(f"Parsed {len(out)} usable cleaned emails from {len(df)} raw rows.")
    return out


# --------------------------------------------------------------------------
# STEP 4: PICK TOP SENDERS
# --------------------------------------------------------------------------

def select_top_senders(df: pd.DataFrame, num_senders: int, min_emails: int) -> list:
    counts = df["sender"].value_counts()
    counts = counts.drop(labels=[s for s in EXCLUDED_SENDERS if s in counts.index])
    eligible = counts[counts >= min_emails]
    top = eligible.head(num_senders).index.tolist()
    print(f"Selected {len(top)} senders (of {len(eligible)} eligible with >= {min_emails} emails).")
    for s in top:
        print(f"   {s}: {counts[s]} emails")
    return top


# --------------------------------------------------------------------------
# STEP 5: STYLOMETRIC FEATURES + PROFILE BUILDING
# --------------------------------------------------------------------------

SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
WORD_RE = re.compile(r"[A-Za-z']+")


def split_sentences(text: str):
    sentences = SENTENCE_SPLIT_RE.split(text)
    return [s.strip() for s in sentences if s.strip()]


def get_words(text: str):
    return WORD_RE.findall(text.lower())


def extract_email_stats(body: str) -> dict:
    """Per-email stylometric stats used to build the aggregate sender profile."""
    words = get_words(body)
    sentences = split_sentences(body)
    n_words = len(words)
    n_sentences = max(len(sentences), 1)

    avg_sentence_length = n_words / n_sentences
    vocab_richness = (len(set(words)) / n_words) if n_words > 0 else 0

    comma_count = body.count(",")
    comma_rate = comma_count / n_words if n_words > 0 else 0

    lines = [l.strip() for l in body.splitlines() if l.strip()]
    first_line = lines[0] if lines else ""
    last_lines = " ".join(lines[-2:]) if lines else ""

    greeting = None
    for name, pattern in GREETING_PATTERNS.items():
        if re.search(pattern, first_line, re.IGNORECASE):
            greeting = name
            break

    signoff = None
    for name, pattern in SIGNOFF_PATTERNS.items():
        if re.search(pattern, last_lines, re.IGNORECASE):
            signoff = name
            break

    return {
        "n_words": n_words,
        "avg_sentence_length": avg_sentence_length,
        "vocab_richness": vocab_richness,
        "comma_rate": comma_rate,
        "greeting": greeting,
        "signoff": signoff,
    }


def build_sender_profile(sender: str, bodies: list) -> dict:
    stats_list = [extract_email_stats(b) for b in bodies]

    avg_words = sum(s["n_words"] for s in stats_list) / len(stats_list)
    avg_sentence_length = sum(s["avg_sentence_length"] for s in stats_list) / len(stats_list)
    vocab_richness = sum(s["vocab_richness"] for s in stats_list) / len(stats_list)
    comma_rate = sum(s["comma_rate"] for s in stats_list) / len(stats_list)

    greeting_counter = Counter(s["greeting"] for s in stats_list if s["greeting"])
    signoff_counter = Counter(s["signoff"] for s in stats_list if s["signoff"])

    n = len(stats_list)
    greeting_dist = {k: round(v / n, 2) for k, v in greeting_counter.most_common(3)}
    signoff_dist = {k: round(v / n, 2) for k, v in signoff_counter.most_common(3)}

    return {
        "sender": sender,
        "num_emails_used": n,
        "avg_words": round(avg_words, 1),
        "avg_sentence_length": round(avg_sentence_length, 1),
        "vocab_richness": round(vocab_richness, 3),
        "comma_rate": round(comma_rate, 3),
        "greeting": greeting_dist,
        "signoff": signoff_dist,
    }


# --------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------

def main():
    df = load_and_clean(INPUT_CSV)
    before = len(df)
    df = df.drop_duplicates(subset=["sender", "body"]).reset_index(drop=True)
    print(f"Dropped {before - len(df)} duplicate emails (same sender + same body).")

    top_senders = select_top_senders(df, NUM_SENDERS, MIN_EMAILS_PER_SENDER)
    df_top = df[df["sender"].isin(top_senders)].copy()

    # Cap number of emails per sender to keep things fast
    df_top = (
        df_top.groupby("sender", group_keys=False)
        .apply(lambda g: g.head(MAX_EMAILS_PER_SENDER))
        .reset_index(drop=True)
    )

    # Save cleaned dataset (this is what Members 2 & 3 will also use)
    df_top.to_csv(OUTPUT_DATASET_CSV, index=False)
    print(f"Saved cleaned dataset -> {OUTPUT_DATASET_CSV} ({len(df_top)} rows)")

    # Build profiles
    profiles = []
    for sender in top_senders:
        bodies = df_top[df_top["sender"] == sender]["body"].tolist()
        profile = build_sender_profile(sender, bodies)
        profiles.append(profile)

    with open(OUTPUT_PROFILES_JSON, "w") as f:
        json.dump(profiles, f, indent=2)
    print(f"Saved sender profiles -> {OUTPUT_PROFILES_JSON} ({len(profiles)} senders)")


if __name__ == "__main__":
    main()
