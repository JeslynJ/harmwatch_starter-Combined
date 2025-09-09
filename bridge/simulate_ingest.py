
import time, requests

URL = "http://localhost:8000/ingest"
SAMPLES = [
    {"text": "You are so dumb, nobody wants you here.", "source": "twitter", "author": "user123"},
    {"text": "Limited time KYC update: click bit.ly/abc now or your bank will block your account!", "source": "instagram", "author": "promo1"},
    {"text": "Breaking: vaccine causes 5G microchips!!!", "source": "reddit", "author": "misinfo_bot"},
]

for s in SAMPLES:
    r = requests.post(URL, json=s, timeout=5)
    print("Sent:", s["text"][:60], "->", r.status_code)
    time.sleep(2)
