import re
from typing import List, Tuple, Dict, Any

# Enhanced patterns from cybershield
SHORTLINKS = {"bit.ly","tinyurl.com","t.co","goo.gl","ow.ly","is.gd","buff.ly","cutt.ly","rb.gy","s.id","t.ly"}

PATTERNS = {
    "hate_speech": re.compile(r"\b(kill yourself|go back|subhuman|ape|monkey|dog|retard|retarded|faggot|slur|scum|racist|terrorist)\b", re.I),
    "cyberbullying": re.compile(r"\b(you are (so )?dumb|nobody likes you|loser|ugly|worthless|kill yourself|idiot|stupid|hate)\b", re.I),
    "misinformation": re.compile(r"\b(5g.*microchip|flat earth|chemtrails|plandemic|crisis actor|fake news|hoax|misleading)\b", re.I),
    "privacy_risk": re.compile(r"\b(share your otp|one time password|ssn|aadhaar|pan number|account number|privacy|expose(?:d)?|doxx?)\b", re.I),
    "hacking_exploit": re.compile(r"\b(cve-\d{4}-\d+|zero[- ]day|exploit|payload|rce|priv[- ]?esc|metasploit|hack(?:ed|ing)?|breach)\b", re.I),
    "scam_phishing": re.compile(r"\b(urgent|verify|kyc|win .* prize|gift card|limited time|act now|bank.*block|click.*link|verify your account|free|prize|win|otp|password|login)\b", re.I),
    "mental_health": re.compile(r"\b(hopeless|i hate myself|i want to die|self[- ]harm|cut myself|depress|suicid|lonely)\b", re.I),
}

# Legacy patterns for backward compatibility
CYBERBULLY = [r"\bidiot\b", r"\bstupid\b", r"\bkill yourself\b", r"\bhate\b"]
HATE_SPEECH = [r"\bracist\b", r"\bterrorist\b", r"\bgo back\b"]
MISINFO = [r"\bfake news\b", r"\bhoax\b", r"\bmisleading\b"]
MENTAL_HEALTH = [r"\bdepress\b", r"\bsuicid\b", r"\blonely\b", r"\bself harm\b"]
SCAM_PHISH = [r"\bverify your account\b", r"\bfree\b", r"\bprize\b", r"\bwin\b", r"\botp\b", r"\bpassword\b", r"\blogin\b"]
HACKING = [r"\bhack(?:ed|ing)?\b", r"\bbreach\b", r"\bexploit\b"]
PRIVACY = [r"\bprivacy\b", r"\bexpose(?:d)?\b", r"\bdoxx?\b"]

SUSPICIOUS_DOMAINS = ["bit.ly", "tinyurl.com", "t.co"]

CATEGORY_ORDER = [
    ("Scam/Phishing", SCAM_PHISH, "high"),
    ("Hacking/Exploit", HACKING, "high"),
    ("Hate Speech", HATE_SPEECH, "medium"),
    ("Cyberbullying", CYBERBULLY, "medium"),
    ("Misinformation", MISINFO, "medium"),
    ("Privacy Risk", PRIVACY, "medium"),
    ("Mental Health Risk", MENTAL_HEALTH, "medium"),
]

def _match_any(text: str, patterns: List[str]) -> bool:
    for p in patterns:
        if re.search(p, text, flags=re.IGNORECASE):
            return True
    return False

def classify(text: str, domains: List[str] = None) -> Tuple[str, str]:
    """
    Enhanced classification function that supports both legacy and new patterns.
    Returns (category, risk_level) tuple.
    """
    # Enhanced classification with risk scoring
    result = classify_enhanced(text, domains or [])
    return result["category"], result["risk_level"]

def classify_enhanced(text: str, domains: List[str] = None) -> Dict[str, Any]:
    """
    Enhanced classification function that returns detailed analysis.
    Returns dict with labels, risk_score, risk_level, category, and why.
    """
    t = text.lower() if text else ""
    matched = []
    why = []
    risk = 0

    # Check enhanced patterns
    for k, pat in PATTERNS.items():
        m = pat.search(t)
        if m:
            matched.append(k)
            why.append(f"{k}: '{m.group(0)}'")

    # Check for shortlinks
    for dom in SHORTLINKS:
        if dom in t:
            if "scam_phishing" not in matched:
                matched.append("scam_phishing")
                why.append(f"shortlink domain: {dom}")

    # Check domains
    if domains:
        for dom in domains:
            if dom in SHORTLINKS:
                if "scam_phishing" not in matched:
                    matched.append("scam_phishing")
                    why.append(f"suspicious domain: {dom}")

    # Risk scoring
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
        risk += weights.get(m, 1)

    # Determine category and risk level
    if not matched:
        category = "Neutral"
        level = "low"
    else:
        # Map enhanced labels to legacy categories
        category_mapping = {
            "scam_phishing": "Scam/Phishing",
            "hacking_exploit": "Hacking/Exploit", 
            "hate_speech": "Hate Speech",
            "cyberbullying": "Cyberbullying",
            "misinformation": "Misinformation",
            "privacy_risk": "Privacy Risk",
            "mental_health": "Mental Health Risk"
        }
        category = category_mapping.get(matched[0], "Other")
        level = "high" if risk >= 5 else "medium" if risk >= 3 else "low"

    return {
        "labels": matched,
        "risk_score": risk,
        "risk_level": level,
        "category": category,
        "why": "; ".join(why) or "—"
    }

# Legacy function for backward compatibility
def classify_legacy(text: str, domains: List[str]) -> Tuple[str, str]:
    # domain heuristic
    if any(d in SUSPICIOUS_DOMAINS for d in (domains or [])):
        return "Scam/Phishing", "high"
    for name, patterns, risk in CATEGORY_ORDER:
        if _match_any(text or "", patterns):
            return name, risk
    return "Neutral", "low"
