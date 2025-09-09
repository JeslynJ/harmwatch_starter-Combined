
import re
from typing import Dict, Any

SHORTLINKS = {"bit.ly","tinyurl.com","t.co","goo.gl","ow.ly","is.gd","buff.ly","cutt.ly","rb.gy","s.id","t.ly"}

PATTERNS = {
    "hate_speech": re.compile(r"\b(kill yourself|go back|subhuman|ape|monkey|dog|retard|retarded|faggot|slur|scum)\b", re.I),
    "cyberbullying": re.compile(r"\b(you are (so )?dumb|nobody likes you|loser|ugly|worthless|kill yourself)\b", re.I),
    "misinformation": re.compile(r"\b(5g.*microchip|flat earth|chemtrails|plandemic|crisis actor|fake news)\b", re.I),
    "privacy_risk": re.compile(r"\b(share your otp|one time password|ssn|aadhaar|pan number|account number)\b", re.I),
    "hacking_exploit": re.compile(r"\b(cve-\d{4}-\d+|zero[- ]day|exploit|payload|rce|priv[- ]?esc|metasploit)\b", re.I),
    "scam_phishing": re.compile(r"\b(urgent|verify|kyc|win .* prize|gift card|limited time|act now|bank.*block|click.*link)\b", re.I),
    "mental_health": re.compile(r"\b(hopeless|i hate myself|i want to die|self[- ]harm|cut myself)\b", re.I),
}

def classify(text: str) -> Dict[str, Any]:
    t = text.lower()
    matched = []
    why = []
    risk = 0

    for k, pat in PATTERNS.items():
        m = pat.search(t)
        if m:
            matched.append(k)
            why.append(f"{k}: '{m.group(0)}'")

    for dom in SHORTLINKS:
        if dom in t:
            if "scam_phishing" not in matched:
                matched.append("scam_phishing")
                why.append(f"shortlink domain: {dom}")

    weights = {
        "scam_phishing": 3,
        "hacking_exploit": 3,
        "privacy_risk": 3,
        "hate_speech": 2,
        "cyberbullying": 2,
        "misinformation": 2,
        "mental_health": 2,
    }
    for m in matched:
        risk += weights.get(m,1)

    if not matched:
        matched = ["neutral"]
    level = "low"
    if risk >= 5: level = "high"
    elif risk >= 3: level = "medium"

    return {"labels": matched, "risk_score": risk, "risk_level": level, "why": "; ".join(why) or "—"}
