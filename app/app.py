import os
from datetime import datetime
import pandas as pd
import streamlit as st

from classify import classify
from preprocess import clean_text, anonymize_id, extract_domains
from storage import init_db, insert_df
from report import render_html

st.set_page_config(page_title="HarmWatch — Social Harm Analyzer", layout="wide")

st.title("HarmWatch — Adverse Societal Impact of Social Media")
st.caption("Enhanced demo • Real-time monitoring • URL analysis • Privacy-aware (hashed IDs)")

# Navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Choose a page:",
    ["📊 Batch Analysis", "🔄 Live Dashboard", "ℹ️ About"]
)

if page == "🔄 Live Dashboard":
    st.info("Switch to the Live Dashboard page to access real-time monitoring features.")
    st.markdown("""
    **Live Dashboard Features:**
    - Real-time WebSocket streaming
    - Live data ingestion
    - URL analysis and text extraction
    - Enhanced classification with risk scoring
    - Real-time charts and monitoring
    """)
    if st.button("Go to Live Dashboard"):
        st.switch_page("pages/1_Live_Dashboard.py")
    st.stop()
elif page == "ℹ️ About":
    st.info("HarmWatch is an enhanced social media harm detection system.")
    st.markdown("""
    **Features:**
    - Batch CSV analysis
    - Real-time monitoring
    - URL content analysis
    - Enhanced classification patterns
    - Privacy-aware processing
    """)
    st.stop()

with st.expander("📘 How to use"):
    st.markdown("""
**Steps**
1. Prepare a CSV with at least a **text** column (use the sample in `data/sample_posts.csv`).
2. (Optional) Include **platform, date, author_id, url**.
3. Upload the file; HarmWatch will clean & classify. Explore charts and export.
    """)

uploaded = st.file_uploader("Upload CSV (min column: text)", type=["csv"])

if uploaded is not None:
    df = pd.read_csv(uploaded)
    if "text" not in df.columns:
        st.error("CSV must contain a 'text' column.")
        st.stop()

    for col in ["platform","date","author_id","url"]:
        if col not in df.columns:
            df[col] = ""

    # Processing
    df["clean_text"] = df["text"].apply(clean_text)
    df["author_hash"] = df["author_id"].apply(anonymize_id)
    df["domains"] = df["text"].apply(extract_domains)

    cats, risks = [], []
    for t, dlist in zip(df["clean_text"], df["domains"]):
        c, r = classify(t, dlist)
        cats.append(c); risks.append(r)
    df["category"], df["risk_level"] = cats, risks

    # Dates
    try:
        df["date_parsed"] = pd.to_datetime(df["date"], errors="coerce")
    except Exception:
        df["date_parsed"] = pd.NaT

    st.subheader("Preview")
    st.dataframe(df[["platform","date","author_hash","url","text","category","risk_level"]].head(30))

    st.subheader("Category distribution")
    st.bar_chart(df["category"].value_counts())

    if df["date_parsed"].notna().any():
        st.subheader("Trend over time (by category)")
        temp = df.dropna(subset=["date_parsed"]).copy()
        temp["day"] = temp["date_parsed"].dt.date
        pivot = temp.pivot_table(index="day", columns="category", values="text", aggfunc="count").fillna(0)
        st.line_chart(pivot)

    st.subheader("Flagged examples")
    flagged = df[df["category"]!="Neutral"]
    st.dataframe(flagged[["platform","date","author_hash","url","text","category","risk_level"]].head(50))

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💾 Export CSV"):
            os.makedirs("outputs", exist_ok=True)
            path = f"outputs/classified_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(path, index=False)
            st.success(f"Saved to {path}")
    with col2:
        if st.button("🗃️ Save to SQLite (optional)"):
            try:
                init_db()
                to_save = df[["platform","date","author_hash","url"]].copy()
                to_save["domain"] = df["domains"].apply(lambda x: x[0] if isinstance(x, list) and x else "")
                to_save["text"] = df["text"]
                to_save["clean_text"] = df["clean_text"]
                to_save["category"] = df["category"]
                to_save["risk_level"] = df["risk_level"]
                insert_df(to_save)
                st.success("Saved to data/harmwatch.db")
            except Exception as e:
                st.error(f"Failed to save: {e}")
    with col3:
        if st.button("📄 Generate HTML report"):
            os.makedirs("outputs", exist_ok=True)
            summary = df["category"].value_counts().to_dict()
            examples = flagged[["platform","date","author_hash","text","category","risk_level"]].head(10)
            html = render_html(summary, examples.to_html(index=False, escape=True))
            path = f"outputs/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(path,"w",encoding="utf-8") as f:
                f.write(html)
            st.success(f"Report saved to {path}")
else:
    st.info("Upload a CSV to begin. Try the sample at data/sample_posts.csv")

st.markdown("---")
st.caption("For research/education • Always respect platform policies & user privacy.")
