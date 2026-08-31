import os
import json

from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
from dotenv import load_dotenv
from services.analyzer import analyze_email
from groq import Groq
from datetime import datetime

load_dotenv()

app = Flask(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_SENDER", "")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD", "")

mail = Mail(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():

    data = request.get_json()

    email_text = data.get("email", "")

    result = analyze_email(email_text)

    return jsonify(result)


@app.route("/coach", methods=["POST"])
def awareness_coach():

    data = request.get_json()

    email = data.get("email", "")

    if groq_client is None:
        return jsonify({
            "error": "Awareness coach is not configured. Set the GROQ_API_KEY environment variable."
        }), 500

    prompt = f"""
You are a cybersecurity awareness coach helping an employee decide how to
handle an email they are unsure about, so they do not fall for phishing.

Based on the email below, create ONE multiple-choice quiz question that
teaches the employee the SAFEST action to take.

The email is:
---
{email}
---

Requirements:
- Write exactly one question as a short, clear sentence.
- Provide exactly 4 answer options.
- Exactly ONE option must be the correct, safest action.
- The other three options must be plausible but WRONG (unsafe or poor choices).
- Return only valid JSON with this exact structure (no extra text):
{{
  "question": "the question text",
  "options": ["opt1", "opt2", "opt3", "opt4"],
  "correct_index": 0,
  "explanation": "a short explanation of the correct answer"
}}
Make sure "correct_index" is the integer index (0-3) of the correct option in
the "options" array.
"""

    try:

        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": "You generate concise, safe cybersecurity coaching questions and always reply with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=400,
        )

        raw = completion.choices[0].message.content.strip()

        # Strip any surrounding markdown fences if the model adds them
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.startswith("json"):
                raw = raw[4:]

        coach = json.loads(raw)

        # Validate structure and correct_index bounds
        if "question" not in coach or "options" not in coach \
           or "correct_index" not in coach or "explanation" not in coach:
            return jsonify({
                "error": "The AI returned an unexpected response format."
            }), 500

        if not (0 <= coach["correct_index"] < len(coach["options"])):
            coach["correct_index"] = 0

        return jsonify(coach)

    except Exception as exc:

        return jsonify({
            "error": f"Failed to generate coaching question: {exc}"
        }), 500


@app.route("/report", methods=["POST"])
def report_email():

    data = request.get_json()

    email = data.get("email", "")

    recipient = os.getenv("MAIL_RECIPIENT", "")
    sender = os.getenv("MAIL_SENDER", "")

    if not recipient or not sender or not app.config["MAIL_PASSWORD"]:
        return jsonify({
            "status": "error",
            "message": "Reporting is not configured. Set the MAIL_* variables in the .env file."
        }), 500

    subject = f"[PhishGuard] Incident Report - {datetime.now():%Y-%m-%d %H:%M:%S}"

    body = f"""INCIDENT REPORT
============================================================
Date: {datetime.now()}

Reported email content:
------------------------------------------------------------
{email}
------------------------------------------------------------

This email was flagged as a potential phishing threat by an
employee and reported to IT Security via PhishGuard-AI.
"""

    try:

        msg = Message(
            subject=subject,
            sender=sender,
            recipients=[recipient]
        )
        msg.body = body
        mail.send(msg)

        return jsonify({
            "status": "success",
            "message": "Email successfully reported to IT Security."
        })

    except Exception as exc:

        return jsonify({
            "status": "error",
            "message": f"Failed to send report: {exc}"
        }), 500


if __name__ == "__main__":
    app.run(debug=True)