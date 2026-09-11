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

```
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
```

## How It Works

DNA learns the normal writing patterns of a sender from historical emails. Incoming emails are then compared against that profile. If an email significantly deviates from the sender's usual writing and behavioral patterns, DNA assigns a higher risk score and flags it as potentially suspicious.

## Quick Start (using the pre-built data — recommended)

This repo already includes a pre-built `profiles.json` (15 sender profiles) and `dataset.csv`, so you can run the full demo **without** downloading the original Enron dataset or rebuilding anything from scratch.

1. **Install dependencies:**
   ```
   pip install flask pandas beautifulsoup4
   ```
   (If you hit a `ModuleNotFoundError` for anything else when running `server.py`, install that package the same way — this project doesn't ship a `requirements.txt` yet.)

2. **Start the Flask backend:**
   ```
   python3 server.py
   ```
   By default this runs on `http://127.0.0.1:5000`. Leave this terminal window running.

3. **Load the Chrome extension:**
   - Go to `chrome://extensions`
   - Enable **Developer Mode** (top-right toggle)
   - Click **Load unpacked**
   - Select the `DNA-prototype` project folder

4. **Try it out:**
   - Open Gmail in Chrome
   - Open any email (works best on emails from one of the 15 profiled senders — see `profiles.json` for the full list, e.g. `kay.mann@enron.com`, `jeff.dasovich@enron.com`)
   - Click the DNA extension icon in your toolbar
   - Click **Analyze** — the popup will display the sender, risk score, writing deviation, behavioral score, and the reasons the email was flagged

The backend must be running (step 2) for the extension to return real results.

## Rebuilding the Dataset From Scratch (optional)

Only needed if you want to regenerate `dataset.csv` / `profiles.json` yourself, e.g. with a different sender selection.

1. Download the Enron email dataset (`emails.csv`) from Kaggle: https://www.kaggle.com/datasets/wcukierski/enron-email-dataset — not included in this repo due to file size (~1.4GB).
2. Place `emails.csv` in the project root.
3. Run:
   ```
   python3 preprocessing.py
   ```
   This regenerates `dataset.csv` and `profiles.json`.

## Notes

- Tested locally with the Flask backend running on `127.0.0.1:5000` — the extension expects this exact address.
- If the extension shows no result, check the terminal running `server.py` for errors first.
- 
