"""
stylometry.py
Member 2 - Feature extraction for BEC writing-style detection.

extract_features(email_text) turns one raw email string into a dict
of stylometric features. No external dependencies.
"""

import re
from collections import Counter

# Common English function words (closed-class words that don't change
# much between topics -- good stylometric signal because people use
# them unconsciously in a consistent way).
FUNCTION_WORDS = [
    "the", "and", "of", "to", "in", "is", "that", "it", "for", "on",
    "with", "as", "was", "at", "by", "an", "be", "this", "which",
    "or", "from", "but", "not", "are", "we", "you", "your", "i",
    "have", "will", "can", "if", "so", "please", "would", "just"
]

GREETING_PATTERNS = ["hi", "hello", "hey", "dear", "good morning",
                      "good afternoon", "good evening", "greetings"]

SIGNOFF_PATTERNS = ["regards", "best regards", "best", "thanks",
                     "thank you", "sincerely", "cheers", "kind regards",
                     "warm regards", "yours truly", "respectfully"]


def _split_sentences(text):
    # Simple sentence splitter on . ! ? followed by space/newline/end
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s for s in sentences if s.strip()]


def _split_words(text):
    return re.findall(r"[A-Za-z']+", text.lower())


def _detect_greeting(first_line):
    first_line = first_line.strip().lower()
    for pattern in GREETING_PATTERNS:
        if first_line.startswith(pattern):
            return pattern.title()
    return None


def _detect_signoff(lines):
    # Look at the last few non-empty lines for a sign-off phrase
    non_empty = [l.strip() for l in lines if l.strip()]
    for line in non_empty[-3:]:
        low = line.lower().strip(",.! ")
        for pattern in SIGNOFF_PATTERNS:
            if low == pattern or low.startswith(pattern):
                return pattern.title()
    return None


def extract_features(email_text: str) -> dict:
    """
    Extract stylometric features from a single raw email string.
    Returns a dict matching the spec in the project brief.
    """
    lines = email_text.split("\n")
    words = _split_words(email_text)
    sentences = _split_sentences(email_text)

    word_count = len(words)
    sentence_count = max(len(sentences), 1)  # avoid div/0
    unique_words = set(words)

    avg_sentence_length = word_count / sentence_count
    vocab_richness = len(unique_words) / word_count if word_count else 0
    avg_word_length = (sum(len(w) for w in words) / word_count
                        if word_count else 0)

    comma_count = email_text.count(",")
    period_count = email_text.count(".")
    question_count = email_text.count("?")
    exclaim_count = email_text.count("!")

    # Rates are per-word so they're comparable across emails of
    # different lengths.
    comma_frequency = comma_count / word_count if word_count else 0
    period_frequency = period_count / word_count if word_count else 0
    question_frequency = question_count / word_count if word_count else 0
    exclamation_frequency = exclaim_count / word_count if word_count else 0

    # Function word frequency: what fraction of all words are
    # function words, PLUS the individual breakdown (useful for
    # more detailed comparison later if you have time).
    word_counter = Counter(words)
    function_word_hits = sum(word_counter.get(w, 0) for w in FUNCTION_WORDS)
    function_word_frequency = (function_word_hits / word_count
                                if word_count else 0)
    function_word_breakdown = {
        w: word_counter.get(w, 0) / word_count if word_count else 0
        for w in FUNCTION_WORDS
    }

    greeting = _detect_greeting(lines[0]) if lines else None
    signoff = _detect_signoff(lines)

    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "average_sentence_length": round(avg_sentence_length, 3),
        "vocabulary_richness": round(vocab_richness, 3),
        "average_word_length": round(avg_word_length, 3),
        "comma_frequency": round(comma_frequency, 4),
        "period_frequency": round(period_frequency, 4),
        "question_frequency": round(question_frequency, 4),
        "exclamation_frequency": round(exclaim_count / word_count, 4)
            if word_count else 0,
        "greeting": greeting,
        "signoff": signoff,
        "function_word_frequency": round(function_word_frequency, 4),
        "function_word_breakdown": function_word_breakdown,
    }


if __name__ == "__main__":
    # Quick manual test -- run `python3 stylometry.py` to sanity check
    sample = """Hi John,

I hope you're doing well. I wanted to follow up on the invoice we
discussed last week. Could you please confirm the payment schedule
by Friday? Let me know if you have any questions.

Regards,
Sarah
"""
    import json
    print(json.dumps(extract_features(sample), indent=2))
