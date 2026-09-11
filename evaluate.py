import random
import csv
import pandas as pd
from deviation import build_sender_stats, compare_with_profile
from behavior import compute_behavior_score

DATASET_CSV = "dataset.csv"
OUTPUT_CSV = "results.csv"
HOLD_OUT = 50
IMPERSONATION_SAMPLES = 50
THRESHOLD = 30  

random.seed(42)  


SYNTHETIC_BEC_TEMPLATES = [
    "URGENT - need this done today.\n\nTransfer {amount} to the account below immediately, this is confidential so don't discuss it with anyone else on the team.\n\n{name}",
    "Hi,\n\nI'm in a meeting and can't talk. I need you to process a wire transfer of {amount} ASAP, before end of day. Please keep this between us for now.\n\n{name}",
    "Quick favor - I need the login and verification code for the finance portal, it's urgent and I don't have time to explain right now.\n\n{name}",
    "As discussed with the CEO, please action this payment request immediately. This is time-sensitive and should not be discussed with anyone outside this thread.\n\n{name}",
]


def generate_synthetic_bec_emails(name):
    amounts = ["AED 48,000", "USD 12,500", "AED 90,000"]
    return [t.format(amount=random.choice(amounts), name=name.split("@")[0])
            for t in SYNTHETIC_BEC_TEMPLATES]


def run_pipeline(weights):
    df = pd.read_csv(DATASET_CSV)
    senders = df["sender"].unique().tolist()

    rows = []
    for sender in senders:
        emails = df[df["sender"] == sender]["body"].tolist()
        if len(emails) <= HOLD_OUT:
            continue

        train = emails[:-HOLD_OUT]
        test_genuine = emails[-HOLD_OUT:]
        sender_stats = build_sender_stats(train)

        for email in test_genuine:
            wd = compare_with_profile(email, sender_stats)["writing_deviation"]
            bh = compute_behavior_score(email)["behavior_score"]
            risk = round(weights["writing"] * wd + weights["behavior"] * bh, 1)
            rows.append({"sender": sender, "label": "genuine",
                         "writing_deviation": wd, "behavior_score": bh,
                         "risk_score": risk})

        other_senders = [s for s in senders if s != sender]
        impersonator = random.choice(other_senders)
        impersonator_emails = df[df["sender"] == impersonator]["body"].tolist()
        sample = random.sample(impersonator_emails,
                                min(IMPERSONATION_SAMPLES, len(impersonator_emails)))
        for email in sample:
            wd = compare_with_profile(email, sender_stats)["writing_deviation"]
            bh = compute_behavior_score(email)["behavior_score"]
            risk = round(weights["writing"] * wd + weights["behavior"] * bh, 1)
            rows.append({"sender": sender, "label": "forged",
                         "impersonator": impersonator,
                         "writing_deviation": wd, "behavior_score": bh,
                         "risk_score": risk})

        # synthetic BEC attacks impersonating this sender - see note above
        for email in generate_synthetic_bec_emails(sender):
            wd = compare_with_profile(email, sender_stats)["writing_deviation"]
            bh = compute_behavior_score(email)["behavior_score"]
            risk = round(weights["writing"] * wd + weights["behavior"] * bh, 1)
            rows.append({"sender": sender, "label": "forged",
                         "impersonator": "synthetic_bec",
                         "writing_deviation": wd, "behavior_score": bh,
                         "risk_score": risk})

    return rows


def compute_metrics(rows, threshold):
    tp = fp = tn = fn = 0
    for r in rows:
        predicted_forged = r["risk_score"] >= threshold
        actual_forged = r["label"] == "forged"
        if predicted_forged and actual_forged:
            tp += 1
        elif predicted_forged and not actual_forged:
            fp += 1
        elif not predicted_forged and not actual_forged:
            tn += 1
        else:
            fn += 1

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)
          if (precision + recall) else 0.0)
    fpr = fp / (fp + tn) if (fp + tn) else 0.0

    return {"TP": tp, "FP": fp, "TN": tn, "FN": fn,
            "precision": round(precision, 3), "recall": round(recall, 3),
            "f1": round(f1, 3), "fpr": round(fpr, 3)}


def main():
    weight_options = {
        "writing-heavy (0.55W / 0.45B)": {"writing": 0.55, "behavior": 0.45},
        "behavior-heavy (0.45W / 0.55B)": {"writing": 0.45, "behavior": 0.55},
    }

    best_name, best_rows, best_metrics = None, None, None
    for name, weights in weight_options.items():
        rows = run_pipeline(weights)
        metrics = compute_metrics(rows, THRESHOLD)
        print(f"\n--- {name} ---")
        print(metrics)
        if best_metrics is None or metrics["f1"] > best_metrics["f1"]:
            best_name, best_rows, best_metrics = name, rows, metrics

    print(f"\nBest weighting by F1: {best_name}")
    print(best_metrics)

    fieldnames = ["sender", "label", "impersonator", "writing_deviation",
                  "behavior_score", "risk_score"]
    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, restval="")
        writer.writeheader()
        writer.writerows(best_rows)
    print(f"\nSaved {len(best_rows)} scored rows -> {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
