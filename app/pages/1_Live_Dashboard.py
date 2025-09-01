import asyncio
import json
import os
from datetime import datetime
import pandas as pd
import streamlit as st
import websockets
import requests
from bs4 import BeautifulSoup

from classify import classify_enhanced
from url_analyzer import fetch_text_from_url, analyze_url

WS_URL = os.getenv("HARMWATCH_WS", "ws://localhost:8000/stream")

st.set_page_config(page_title="HarmWatch Live", page_icon="🔄", layout="wide")
st.title("🔄 HarmWatch Live — Real-Time Social Media Harm Analyzer")
st.caption("Enhanced real-time monitoring with URL analysis and comprehensive classification")

colA, colB = st.columns([2,1])
status = colA.empty()
controls = colB.container()

log_holder = st.empty()
chart_holder = st.empty()

data = []

def to_df():
    if not data:
        return pd.DataFrame(columns=["time","source","author","text","labels","risk_level","risk_score","why","platform","url"])
    return pd.DataFrame(data)

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
                platform = payload.get("platform", "unknown")
                url = payload.get("url", "")

                # Enhanced classification
                result = classify_enhanced(text)
                row = {
                    "time": timestamp,
                    "source": source,
                    "author": author,
                    "text": text,
                    "labels": ", ".join(result["labels"]),
                    "risk_level": result["risk_level"],
                    "risk_score": result["risk_score"],
                    "why": result["why"],
                    "platform": platform,
                    "url": url
                }
                data.append(row)

                # Update live dashboard
                df = to_df().tail(200)
                with log_holder.container():
                    st.subheader("Live Feed")
                    st.dataframe(df, use_container_width=True, height=320)
                
                with chart_holder.container():
                    st.subheader("Risk Overview")
                    if len(df):
                        # Risk level distribution
                        by_risk = df["risk_level"].value_counts().rename_axis("risk").reset_index(name="count")
                        st.bar_chart(by_risk.set_index("risk"))
                        
                        # Category distribution
                        by_category = df["labels"].str.get_dummies(sep=", ").sum().sort_values(ascending=False)
                        if len(by_category):
                            st.bar_chart(by_category)
                        
                        # Platform distribution
                        if df["platform"].notna().any():
                            by_platform = df["platform"].value_counts()
                            st.bar_chart(by_platform)
    except Exception as e:
        status.error(f"Connection failed: {e}")

with controls:
    st.markdown("**Controls**")
    ws_url = st.text_input("WebSocket URL", WS_URL)
    if ws_url != WS_URL:
        os.environ["HARMWATCH_WS"] = ws_url
        st.experimental_rerun()

    st.markdown("**Analyze a single URL**")
    url_input = st.text_input("Enter post URL (YouTube / X / Instagram / public pages)")
    if url_input:
        with st.spinner("Fetching URL and analyzing..."):
            fetched = fetch_text_from_url(url_input)
            st.markdown("**Extracted Text (preview):**")
            st.write(fetched)
            
            # Analyze the extracted text
            result = classify_enhanced(fetched)
            st.markdown("**Analysis Result:**")
            st.write({
                "labels": result["labels"],
                "risk_level": result["risk_level"],
                "risk_score": result["risk_score"],
                "why": result["why"]
            })
            
            # Show URL metadata
            url_analysis = analyze_url(url_input)
            if url_analysis["success"]:
                st.markdown("**URL Analysis:**")
                st.write({
                    "domains": url_analysis["domains"],
                    "is_social_media": url_analysis["is_social_media"]
                })

    if st.button("Start Listening", use_container_width=True):
        asyncio.run(listen_and_classify())

    if st.button("Export CSV", use_container_width=True):
        df = to_df()
        if not df.empty:
            ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
            out = f"harmwatch_live_export_{ts}.csv"
            df.to_csv(out, index=False)
            st.success(f"Exported {out}")
        else:
            st.warning("No data to export")

    if st.button("Clear Data", use_container_width=True):
        data.clear()
        st.success("Data cleared")

# Display current data if available
if data:
    st.subheader("Current Data Summary")
    df = to_df()
    st.write(f"Total records: {len(df)}")
    if len(df) > 0:
        st.write(f"Risk levels: {df['risk_level'].value_counts().to_dict()}")
        st.write(f"Categories: {df['labels'].value_counts().head(5).to_dict()}")

st.markdown("---")
st.caption("Real-time monitoring • Enhanced classification • URL analysis • Privacy-aware")
