def analyze_email(text):

    txt = text.lower()

    score = 0
    flags = []

    if "urgent" in txt or "24 hours" in txt:
        score += 25
        flags.append("Urgency tactics detected")

    if "password" in txt or "credentials" in txt:
        score += 30
        flags.append("Credential request detected")

    if "http://" in txt or "https://" in txt:
        score += 25
        flags.append("Suspicious link detected")

    if "verify account" in txt:
        score += 20
        flags.append("Account verification scam pattern")

    if score < 30:
        verdict = "Likely Safe"
    elif score < 60:
        verdict = "Suspicious"
    else:
        verdict = "Likely Phishing"

    return {
        "score": score,
        "verdict": verdict,
        "flags": flags
    }