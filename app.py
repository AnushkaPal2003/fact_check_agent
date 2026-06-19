
import os
from dotenv import load_dotenv

load_dotenv()

import streamlit as st

from pdf_extractor import extract_text_from_pdf, chunk_text_if_too_long
from pipeline import run_fact_check_pipeline


import os
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")



# Page Config

st.set_page_config(
    page_title="Fact-Check Agent",
    page_icon="🔎",
    layout="wide"
)


# Header

st.title("🔎 Fact-Check Agent")

st.caption(
    "Upload a PDF and automatically verify factual claims "
    "(statistics, dates, financial figures, and technical facts) "
    "against live web data."
)


# Sidebar

st.sidebar.header("API Configuration")

st.sidebar.markdown(
    """
Enter your OpenAI API key below.

The key is only used for this session and is not stored.
"""
)

openai_api_key = st.sidebar.text_input(
    "Enter your OpenAI API Key",
    type="password",
    placeholder="sk-..."
)

# Tavily key from .env 
tavily_api_key = os.getenv("TAVILY_API_KEY")

if not tavily_api_key:
    st.error("Missing TAVILY_API_KEY in .env")
    st.stop()


# Use secrets if available

tavily_api_key = st.sidebar.text_input(
    "Tavily API Key",
    value=os.getenv("TAVILY_API_KEY", ""),
    type="password"
)


# PDF Upload

uploaded_pdf = st.file_uploader(
    "Upload PDF",
    type=["pdf"]
)

run_button = st.button(
    "Run Fact-Check",
    type="primary",
    disabled=not (
    uploaded_pdf and
    openai_api_key

    )
)

if not uploaded_pdf:
    st.info("Upload a PDF to begin.")

elif not openai_api_key:
    st.info("Enter your OpenAI API key to continue.")


# Run Pipeline

if run_button:

    try:

        # Extract PDF text

        with st.spinner("Reading PDF..."):

            document_text = extract_text_from_pdf(uploaded_pdf)
            document_text = chunk_text_if_too_long(document_text)

        if not document_text.strip():
            st.error(
                "No readable text was found. "
                "This PDF may be image-only or scanned."
            )
            st.stop()

        
        # Progress Tracking

        progress_bar = st.progress(
            0,
            text="Extracting claims..."
        )

        status_placeholder = st.empty()

        def update_progress(current_index, total, claim_text):

            if total == 0:
                return

            fraction = current_index / total

            progress_bar.progress(
                min(fraction, 1.0),
                text=f"Checking claim {current_index + 1} of {total}"
            )

            status_placeholder.write(
                f"🔍 Verifying: *{claim_text}*"
            )

        
        # Run Fact Check

        report = run_fact_check_pipeline(
            document_text=document_text,
            openai_api_key=openai_api_key,
            tavily_api_key=tavily_api_key,
            progress_callback=update_progress
        )

        progress_bar.progress(
            1.0,
            text="Fact-check completed!"
        )

        status_placeholder.empty()

        
        # Empty Report

        if not report:
            st.warning(
                "No checkable factual claims were found "
                "in the uploaded document."
            )
            st.stop()

        
        # Summary Metrics

        verified_count = sum(
            1 for r in report
            if r.get("verdict") == "Verified"
        )

        inaccurate_count = sum(
            1 for r in report
            if r.get("verdict") == "Inaccurate"
        )

        false_count = sum(
            1 for r in report
            if r.get("verdict") == "False"
        )

        st.subheader("📊 Summary")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Claims",
            len(report)
        )

        col2.metric(
            "✅ Verified",
            verified_count
        )

        col3.metric(
            "⚠️ Inaccurate",
            inaccurate_count
        )

        col4.metric(
            "❌ False",
            false_count
        )

        # Detailed Report

        st.subheader("📋 Detailed Report")

        verdict_icons = {
    "Verified": "✅",
    "Inaccurate": "⚠️",
    "False": "❌",
    "Verification Error": "🔄",
}

        for item in report:

            verdict = item.get("verdict", "Unknown")
            icon = verdict_icons.get(verdict, "❓")

            claim_text = item.get(
                "claim_text",
                "Unknown Claim"
            )

            with st.expander(
                f"{icon} {verdict} — {claim_text}"
            ):

                st.write(
                    f"**Claim Type:** "
                    f"{item.get('claim_type', 'Unknown')}"
                )

                st.write(
                    f"**Reasoning:** "
                    f"{item.get('reasoning', 'No reasoning provided')}"
                )

                correct_fact = item.get("correct_fact")

                if verdict != "Verified" and correct_fact:
                    st.write(
                        f"**Correct Fact:** {correct_fact}"
                    )

                source_url = item.get("source_url")

                if source_url:
                    st.markdown(
                        f"**Source:** [{source_url}]({source_url})"
                    )

    except Exception as e:

        st.error(
            "An unexpected error occurred while "
            f"processing the document.\n\n{str(e)}"
        )

        st.exception(e)