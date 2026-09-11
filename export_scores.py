"""
export_scores.py
Member 2 - Generates a CSV of writing_deviation scores across ALL
senders in the dataset, labelled genuine/impersonated. This is what
you hand to Member 3 so they can compute precision/recall/F1/FPR
without having to re-run your code themselves.

Usage:
    python3 export_scores.py

Output:
    writing_scores.csv
"""

import csv
import random
import pandas as pd
from deviation import build_sender_stats, compare_with_profile

DATASET_CSV = "dataset.csv"
OUTPUT_CSV = "writing_scores.csv"
HOLD_OUT = 50          # emails per sender reserved for genuine testing
IMPERSONATION_SAMPLES = 50  # emails borrowed from another sender per test

random.seed(42)  # reproducible -- same results every run


def main():
    df = pd.read_csv(DATASET_CSV)
    senders = df["sender"].unique().tolist()
    print(f"Found {len(senders)} senders in dataset.csv")

    rows = []

    for sender in senders:
        emails = df[df["sender"] == sender]["body"].tolist()
        if len(emails) <= HOLD_OUT:
            print(f"  Skipping {sender} (not enough emails)")
            continue

        train = emails[:-HOLD_OUT]
        test_genuine = emails[-HOLD_OUT:]
        sender_stats = build_sender_stats(train)

        # genuine
        for email in test_genuine:
            result = compare_with_profile(email, sender_stats)
            rows.append({
                "sender": sender,
                "label": "genuine",
                "writing_deviation": result["writing_deviation"],
                **{f"dev_{k}": v for k, v in result["feature_deviations"].items()},
            })

        # impersonated: pick a different random sender's real emails
        other_senders = [s for s in senders if s != sender]
        impersonator = random.choice(other_senders)
        impersonator_emails = df[df["sender"] == impersonator]["body"].tolist()
        sample = random.sample(impersonator_emails,
                                min(IMPERSONATION_SAMPLES, len(impersonator_emails)))
        for email in sample:
            result = compare_with_profile(email, sender_stats)
            rows.append({
                "sender": sender,
                "label": "forged",
                "impersonator": impersonator,
                "writing_deviation": result["writing_deviation"],
                **{f"dev_{k}": v for k, v in result["feature_deviations"].items()},
            })

        print(f"  Done: {sender} (vs {impersonator})")

    fieldnames = ["sender", "label", "impersonator", "writing_deviation",
                  "dev_email_length", "dev_sentence_length", "dev_vocabulary",
                  "dev_punctuation", "dev_greeting", "dev_signoff"]
    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, restval="")
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved {len(rows)} scored rows -> {OUTPUT_CSV}")
    print("Hand this file to Member 3 for precision/recall/F1/FPR evaluation.")


if __name__ == "__main__":
    main()
