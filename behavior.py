import re

URGENCY_WORDS = ["urgent", "immediately", "asap", "as soon as possible",
                  "today", "right now", "quickly", "time-sensitive",
                  "time sensitive", "hurry", "before end of day", "eod"]

FINANCIAL_WORDS = ["payment", "transfer", "bank", "account", "invoice",
                    "funds", "wire", "wire transfer", "iban", "swift",
                    "routing number", "deposit", "reimburse"]

SECRECY_WORDS = ["confidential", "keep this private", "don't tell anyone",
                  "do not tell anyone", "do not discuss", "dont discuss",
                  "between us", "just between", "don't mention",
                  "do not mention", "no one else"]

CREDENTIAL_WORDS = ["password", "login", "log in", "verification code",
                     "verification", "otp", "credentials", "username",
                     "2fa", "two-factor", "security code"]

AUTHORITY_WORDS = ["ceo", "cfo", "coo", "director", "executive", "boss",
                    "chairman", "president", "vp", "vice president",
                    "manager approved", "on behalf of"]

CATEGORIES = {
    "urgency": URGENCY_WORDS,
    "financial": FINANCIAL_WORDS,
    "secrecy": SECRECY_WORDS,
    "credential": CREDENTIAL_WORDS,
    "authority": AUTHORITY_WORDS,
}

SATURATION = 3  # this many keyword hits = fully maxed out at 100 for that category


def _score_category(text_lower: str, keywords: list) -> float:
    hits = 0
    for kw in keywords:
        hits += len(re.findall(re.escape(kw), text_lower))
    if hits == 0:
        return 0.0
    return round(min(100.0, (hits / SATURATION) * 100.0), 1)


def extract_behavior_scores(email_text: str) -> dict:
    text_lower = email_text.lower()
    return {cat: _score_category(text_lower, words)
            for cat, words in CATEGORIES.items()}


DEFAULT_CATEGORY_WEIGHTS = {
    "urgency": 0.20,
    "financial": 0.30,
    "secrecy": 0.20,
    "credential": 0.10,
    "authority": 0.20,
}


def compute_behavior_score(email_text: str, weights: dict = None) -> dict:
    weights = weights or DEFAULT_CATEGORY_WEIGHTS
    category_scores = extract_behavior_scores(email_text)
    behavior_score = sum(category_scores[c] * weights[c] for c in weights)
    return {
        "behavior_score": round(behavior_score, 1),
        "category_scores": category_scores,
    }

