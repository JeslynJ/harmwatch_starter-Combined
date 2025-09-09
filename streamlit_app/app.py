
import asyncio, json, os
from datetime import datetime
import pandas as pd
import streamlit as st
import websockets
import requests
from bs4 import BeautifulSoup

from classify import classify

WS_URL = os.getenv("CYBERSHIELD_WS", "ws://localhost:8000/stream")

st.set_page_config(page_title="CyberShield Live", page_icon="🛡️", layout="wide")
st.title("🛡️ CyberShield Live — Real-Time Social Media Harm Analyzer")

colA, colB = st.columns([2,1])
status = colA.empty()
controls = colB.container()

log_holder = st.empty()
chart_holder = st.empty()

data = []

def to_df():
    if not data:
        return pd.DataFrame(columns=["time","source","author","text","labels","risk_level","risk_score","why"])
    return pd.DataFrame(data)

def fetch_text_from_url(url: str, max_chars=3000) -> str:
    try:
        headers = {"User-Agent":"Mozilla/5.0 (compatible; CyberShield/1.0; +https://example.com)"}
        resp = requests.get(url, headers=headers, timeout=8)
        if resp.status_code != 200:
            return f"[Error fetching URL: status {resp.status_code}]"
        soup = BeautifulSoup(resp.text, "html.parser")
        parts = []
        title = soup.title.string.strip() if soup.title and soup.title.string else None
        if title:
            parts.append(title)
        og = soup.find("meta", property="og:description")
        if og and og.get("content"):
            parts.append(og.get("content").strip())
        m = soup.find("meta", attrs={"name":"description"})
        if m and m.get("content"):
            parts.append(m.get("content").strip())
        texts = []
        for tag in soup.find_all(["p","li","span","strong"]):
            t = tag.get_text(separator=" ", strip=True)
            if t and len(t) > 20:
                texts.append(t)
        if texts:
            parts.append(" ".join(texts[:8]))
        combined = "\n\n".join(parts)
        if not combined.strip():
            combined = soup.get_text(separator=" ", strip=True)[:max_chars]
        return combined[:max_chars]
    except Exception as e:
        return f"[Error fetching URL: {e}]"

async def listen_and_classify():
    try:
        async with websockets.connect(WS_URL) as ws:
            status.success(f"Connected to {WS_URL}")
            await ws.send("ready")
            while True:
                msg = await ws.recv()
                try:
                    payload = json.loads(msg) if isinstance(msg, str) else msg
                except Exception:
                    continue
                text = payload.get("text", "")
                source = payload.get("source", "unknown")
                author = payload.get("author") or "anon"
                timestamp = payload.get("timestamp") or datetime.utcnow().isoformat()+"Z"

                result = classify(text)
                row = {
                    "time": timestamp,
                    "source": source,
                    "author": author,
                    "text": text,
                    "labels": ", ".join(result["labels"]),
                    "risk_level": result["risk_level"],
                    "risk_score": result["risk_score"],
                    "why": result["why"]
                }
                data.append(row)

                df = to_df().tail(200)
                with log_holder.container():
                    st.subheader("Live Feed")
                    st.dataframe(df, use_container_width=True, height=320)
                with chart_holder.container():
                    st.subheader("Risk Overview")
                    if len(df):
                        by_label = df["risk_level"].value_counts().rename_axis("risk").reset_index(name="count")
                        st.bar_chart(by_label.set_index("risk"))
                        by_type = df["labels"].str.get_dummies(sep=", ").sum().sort_values(ascending=False)
                        if len(by_type):
                            st.bar_chart(by_type)
    except Exception as e:
        status.error(f"Connection failed: {e}")

with controls:
    st.markdown("**Controls**")
    ws_url = st.text_input("WebSocket URL", WS_URL)
    if ws_url != WS_URL:
        os.environ["CYBERSHIELD_WS"] = ws_url
        st.experimental_rerun()

    st.markdown("**Analyze a single URL (YouTube / X / Instagram / public pages)**")
    url_input = st.text_input("Enter post URL (optional)")
    if url_input:
        with st.spinner("Fetching URL and analyzing..."):
            fetched = fetch_text_from_url(url_input)
            st.markdown("**Extracted Text (preview):**")
            st.write(fetched)
            result = classify(fetched)
            st.markdown("**Analysis Result:**")
            st.write({
                "labels": result["labels"],
                "risk_level": result["risk_level"],
                "risk_score": result["risk_score"],
                "why": result["why"]
            })

    if st.button("Start Listening", use_container_width=True):
        asyncio.run(listen_and_classify())

    if st.button("Export CSV", use_container_width=True):
        df = to_df()
        ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        out = f"cybershield_export_{ts}.csv"
        df.to_csv(out, index=False)
        st.success(f"Exported {out}")
