import os

from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
from dotenv import load_dotenv
from services.analyzer import analyze_email
from datetime import datetime

load_dotenv()

app = Flask(__name__)

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

    email = data.get("email", "").lower()

    if "credentials" in email or "password" in email:

        return jsonify({
            "question": "An email asks you to enter your password to prevent account suspension. What is the safest action?",
            "options": [
                "Provide the password immediately",
                "Verify through the official website or application",
                "Send your password by reply email",
                "Forward the email to colleagues"
            ],
            "correct_index": 1,
            "explanation": "Passwords should never be submitted through links in unexpected emails."
        })

    elif "urgent" in email or "24 hours" in email:

        return jsonify({
            "question": "What is a common sign of phishing in this email?",
            "options": [
                "Professional formatting",
                "Use of company branding",
                "Urgency designed to pressure quick action",
                "A greeting with your name"
            ],
            "correct_index": 2,
            "explanation": "Urgency is commonly used by attackers to rush people into making mistakes."
        })

    else:

        return jsonify({
            "question": "What should you do if you are unsure whether an email is legitimate?",
            "options": [
                "Click every link to test them",
                "Ignore all company emails",
                "Verify through official channels before acting",
                "Reply with personal information"
            ],
            "correct_index": 2,
            "explanation": "If unsure, verify through an official source before taking action."
        })


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