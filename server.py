from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

from deviation import build_sender_stats, compare_with_profile
from scoring import compute_risk


app = Flask(__name__)

# Allow the Chrome extension to communicate with Python
CORS(app)


DATASET_CSV = "dataset.csv"
TARGET_SENDER = "carol.clair@enron.com"
TRAINING_EMAILS = 120


def load_sender_emails():

    df = pd.read_csv(DATASET_CSV)

    emails = (
        df[
            df["sender"]
            .astype(str)
            .str.lower()
            == TARGET_SENDER.lower()
        ]["body"]
        .fillna("")
        .astype(str)
        .tolist()
    )

    return [
        email.strip()
        for email in emails
        if email.strip()
    ]


# Build Carol's normal writing profile
emails = load_sender_emails()

if len(emails) < TRAINING_EMAILS:

    raise ValueError(
        f"Not enough emails for {TARGET_SENDER}. "
        f"Found {len(emails)}, need at least "
        f"{TRAINING_EMAILS}."
    )


training_emails = emails[:TRAINING_EMAILS]

sender_stats = build_sender_stats(training_emails)


@app.route("/analyze", methods=["POST"])
def analyze_email():

    data = request.get_json()

    if not data:

        return jsonify({
            "error": "No email data received"
        }), 400


    sender = data.get(
        "sender",
        "Unknown sender"
    )

    subject = data.get(
        "subject",
        ""
    )

    body = data.get(
        "body",
        ""
    )


    if not body:

        return jsonify({
            "error": "Email body is empty"
        }), 400


    # Writing-style analysis
    writing_result = compare_with_profile(
        body,
        sender_stats
    )

    writing_deviation = (
        writing_result["writing_deviation"]
    )


    # Behavior + final risk
    risk_result = compute_risk(
        writing_deviation,
        body
    )


    return jsonify({

        "sender": sender,

        "subject": subject,

        "risk_score": round(
            risk_result["risk_score"],
            2
        ),

        "risk_label": (
            risk_result["risk_label"]
        ),

        "writing_deviation": round(
            writing_deviation,
            2
        ),

        "behavior_score": round(
            risk_result["behavior_score"],
            2
        ),

        "category_scores": (
            risk_result["category_scores"]
        ),

        "reasons": (
            risk_result["reasons"]
        ),

        "feature_deviations": (
            writing_result[
                "feature_deviations"
            ]
        )
    })


@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "message":
            "BEC Email Analyzer API is running"
    })


if __name__ == "__main__":

    print("=" * 60)
    print("BEC EMAIL ANALYZER SERVER")
    print("=" * 60)

    print(
        "Server running at "
        "http://127.0.0.1:5000"
    )

    print(
        "Waiting for emails from "
        "Chrome extension..."
    )

    print("=" * 60)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )