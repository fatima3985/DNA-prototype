"""
deviation.py
Member 2 - Compares a new email's features against a sender's
historical writing profile and produces a 0-100 writing deviation
score (plus a breakdown per feature), matching the project brief's
output format.
"""

import statistics
from collections import Counter
from stylometry import extract_features

# Which numeric features feed into the z-score comparison, and how
# they map onto the brief's "feature_deviations" categories.
NUMERIC_FEATURE_GROUPS = {
    "email_length": ["word_count"],
    "sentence_length": ["average_sentence_length"],
    "vocabulary": ["vocabulary_richness", "average_word_length"],
    "punctuation": ["comma_frequency", "period_frequency",
                     "question_frequency", "exclamation_frequency"],
}

# Final weighted combination -> overall writing_deviation score.
# These are a starting point -- tune them during evaluation and note
# in your report why you landed on them (that's literally graded
# under "technical depth").
DEFAULT_WEIGHTS = {
    "email_length": 0.20,
    "sentence_length": 0.20,
    "vocabulary": 0.15,
    "punctuation": 0.15,
    "greeting": 0.15,
    "signoff": 0.15,
}


def build_sender_stats(past_emails: list[str]) -> dict:
    """
    Takes a list of a sender's PAST raw email texts and returns the
    mean + stdev for every numeric feature, plus the most common
    greeting/signoff. This is what Member 1's profiles.json should
    eventually store -- but you can compute it yourself right now
    from raw emails so you're not blocked waiting on them.
    """
    all_features = [extract_features(email) for email in past_emails]

    stats = {}
    numeric_keys = [
        "word_count", "average_sentence_length", "vocabulary_richness",
        "average_word_length", "comma_frequency", "period_frequency",
        "question_frequency", "exclamation_frequency",
        "function_word_frequency",
    ]
    for key in numeric_keys:
        values = [f[key] for f in all_features]
        mean = statistics.mean(values)
        # stdev needs >= 2 data points; guard against small samples
        stdev = statistics.stdev(values) if len(values) > 1 else 0.0
        stats[key] = {"mean": mean, "stdev": stdev}

    # Full frequency distributions (including "None" for no greeting/
    # signoff at all) -- much more realistic than a single "most common"
    # value, since real people don't greet the same way every time.
    n = len(all_features)
    greeting_counts = Counter(f["greeting"] for f in all_features)
    signoff_counts = Counter(f["signoff"] for f in all_features)
    stats["greeting_distribution"] = {k: v / n for k, v in greeting_counts.items()}
    stats["signoff_distribution"] = {k: v / n for k, v in signoff_counts.items()}
    # keep these for convenience/debugging/reporting
    stats["common_greeting"] = greeting_counts.most_common(1)[0][0] if greeting_counts else None
    stats["common_signoff"] = signoff_counts.most_common(1)[0][0] if signoff_counts else None
    return stats


def _zscore_to_100(x, mean, stdev):
    """Turn a raw z-score into a 0-100 'how unusual is this' scale."""
    if stdev == 0:
        return 0.0 if x == mean else 100.0
    z = abs((x - mean) / stdev)
    # z=0 -> 0, z=2 -> ~100 (2 standard deviations is already very
    # unusual for most writing features). Cap at 100.
    return min(100.0, (z / 2.0) * 100.0)


def _categorical_deviation(new_value, distribution: dict):
    """
    Greeting/signoff deviation based on how often the sender actually
    used this exact value (including None, for 'no greeting/signoff')
    in their history -- not just whether it matches their single most
    common choice. A sender who says "Hi" 40% of the time and nothing
    50% of the time shouldn't get penalised hard for either.
    """
    if not distribution:
        return 0.0  # no baseline at all -- can't judge
    freq = distribution.get(new_value, 0.0)
    return round(100.0 * (1.0 - freq), 1)


def compare_with_profile(email_text: str, sender_stats: dict,
                          weights: dict = None) -> dict:
    """
    Main entry point for Member 2's job: given a new email and the
    sender's historical stats (from build_sender_stats), return the
    writing_deviation score + feature_deviations breakdown.
    """
    weights = weights or DEFAULT_WEIGHTS
    new_features = extract_features(email_text)

    # Score each individual numeric feature vs its baseline
    per_feature_scores = {}
    for key, base in sender_stats.items():
        if key in ("common_greeting", "common_signoff"):
            continue
        if key in new_features:
            per_feature_scores[key] = _zscore_to_100(
                new_features[key], base["mean"], base["stdev"]
            )

    # Roll individual features up into the brief's grouped categories
    feature_deviations = {}
    for group, keys in NUMERIC_FEATURE_GROUPS.items():
        relevant = [per_feature_scores[k] for k in keys
                    if k in per_feature_scores]
        feature_deviations[group] = (round(statistics.mean(relevant), 1)
                                      if relevant else 0.0)

    feature_deviations["greeting"] = _categorical_deviation(
        new_features["greeting"], sender_stats.get("greeting_distribution", {})
    )
    feature_deviations["signoff"] = _categorical_deviation(
        new_features["signoff"], sender_stats.get("signoff_distribution", {})
    )

    # Weighted combination -> single writing_deviation score
    writing_deviation = sum(
        feature_deviations[k] * weights[k] for k in weights
    )

    return {
        "writing_deviation": round(writing_deviation, 1),
        "feature_deviations": feature_deviations,
    }


if __name__ == "__main__":
    import json

    # ---- Fake "past emails" for Sarah, just to test end-to-end ----
    sarah_past_emails = [
        """Hi John,

I hope you're doing well. I wanted to follow up on the invoice we
discussed last week. Could you please confirm the payment schedule
by Friday? Let me know if you have any questions.

Regards,
Sarah
""",
        """Hi Team,

Quick update on the Q3 budget review. I've attached the latest
figures for your reference. Please review before our meeting on
Thursday and let me know if anything looks off.

Regards,
Sarah
""",
        """Hi John,

Thanks for sending that over. I've reviewed the contract and it
looks good overall, though I'd like to discuss clause 4 briefly
before we sign anything.

Regards,
Sarah
""",
        """Hi John,

Following up again on this -- have you had a chance to look at the
numbers I sent through? Would appreciate an update when you get a
moment.

Regards,
Sarah
""",
        """Hi Team,

Just a reminder that the deadline for expense reports is this
Friday. Please make sure everything is submitted through the usual
portal.

Regards,
Sarah
""",
    ]

    # ---- A suspicious "new" email pretending to be Sarah ----
    suspicious_email = """URGENT - need this done today.

Transfer 48,000 AED to the account below immediately, this is
confidential so don't discuss it with anyone else on the team.

Sarah"""

    stats = build_sender_stats(sarah_past_emails)
    result = compare_with_profile(suspicious_email, stats)
    print(json.dumps(result, indent=2))
