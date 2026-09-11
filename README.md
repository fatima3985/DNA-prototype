# DNA — Digital Narrative Anomaly Detection

DNA is a cybersecurity prototype designed to detect Business Email Compromise (BEC) and email impersonation by analyzing whether an email matches the usual writing style of the person it claims to be from.

## Features

- Sender-specific writing profiles
- Stylometric analysis
- Behavioral analysis
- Anomaly/deviation scoring
- Risk scoring
- Email evaluation
- Chrome extension interface
- Flask backend

## Project Structure

```text
DNA-prototype/
├── server.py
├── preprocessing.py
├── stylometry.py
├── behavior.py
├── deviation.py
├── scoring.py
├── evaluate.py
├── export_scores.py
├── run_demo.py
├── profiles.json
├── dataset.csv
├── results.csv
├── writing_scores.csv
├── manifest.json
├── content.js
├── popup.html
├── popup.css
└── popup.js


How It Works

DNA learns the normal writing patterns of a sender from historical emails. Incoming emails are then compared against that profile. If an email significantly deviates from the sender's usual writing and behavioral patterns, DNA assigns a higher risk score and flags it as potentially suspicious.

Running the Prototype

Install the required dependencies:

pip install -r requirements.txt

Start the Flask server:

python3 server.py

The Chrome extension can be loaded through:

Chrome → Extensions → Developer Mode → Load unpacked

Select the project folder.

The original Enron emails.csv dataset is not included in the repository because of its large file size.
