"""
run_demo.py
 End-to-end demo using REAL dataset.csv
(15 Enron senders x 300 emails each).

Usage:
    python3 run_demo.py
"""

import json
import statistics
import pandas as pd
from deviation import build_sender_stats, compare_with_profile

DATASET_CSV = "dataset.csv"


def load_sender_emails(dataset_csv: str, sender: str) -> list:
    """Load all raw email bodies."""
    df = pd.read_csv(dataset_csv)
    return df[df["sender"] == sender]["body"].tolist()


def main():
    target_sender = "kay.mann@enron.com"     # the person being impersonated
    impersonator = "jeff.dasovich@enron.com"  # a stylistically different sender

    print(f"Building writing profile for: {target_sender}")
    all_emails = load_sender_emails(DATASET_CSV, target_sender)

    # Train the profile on the first 250 emails, test on the other 50 --
    # this way "genuine" test emails were never seen while building the baseline, which is a fair test.
 
    train, test_genuine = all_emails[:250], all_emails[250:]
    sender_stats = build_sender_stats(train)
    print(f"  Baseline built from {len(train)} emails, "
          f"testing against {len(test_genuine)} held-out genuine emails.\n")

    # ---- Score every held-out GENUINE email ----
    genuine_scores = [compare_with_profile(e, sender_stats)["writing_deviation"]
                       for e in test_genuine]

    # ---- Score real emails from a DIFFERENT sender, relabelled as if
    #      they came from the target -- this is the brief's recommended
    #      "forged-message set" approach ----
    impersonator_emails = load_sender_emails(DATASET_CSV, impersonator)[:50]
    forged_scores = [compare_with_profile(e, sender_stats)["writing_deviation"]
                      for e in impersonator_emails]

    print(f"GENUINE emails from {target_sender} (n={len(genuine_scores)}):")
    print(f"  mean deviation:   {statistics.mean(genuine_scores):.1f}")
    print(f"  median deviation: {statistics.median(genuine_scores):.1f}")
    print(f"  min / max:        {min(genuine_scores):.1f} / {max(genuine_scores):.1f}\n")

    print(f"IMPERSONATED: {impersonator}'s real emails relabelled as "
          f"{target_sender} (n={len(forged_scores)}):")
    print(f"  mean deviation:   {statistics.mean(forged_scores):.1f}")
    print(f"  median deviation: {statistics.median(forged_scores):.1f}")
    print(f"  min / max:        {min(forged_scores):.1f} / {max(forged_scores):.1f}\n")

  
    print("--- Example GENUINE breakdown ---")
    print(json.dumps(compare_with_profile(test_genuine[0], sender_stats), indent=2))

    print("\n--- Example IMPERSONATED breakdown ---")
    print(json.dumps(compare_with_profile(impersonator_emails[0], sender_stats), indent=2))


if __name__ == "__main__":
    main()
