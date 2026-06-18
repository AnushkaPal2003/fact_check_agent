"""
pipeline.py

Orchestrates the complete fact-checking workflow:

PDF Text
    ↓
Claim Extraction
    ↓
Web Verification
    ↓
Verdict Generation
    ↓
Final Report

This module contains no UI code and no PDF parsing logic.
"""

from claim_extractor import extract_claims
from web_verifier import search_evidence_for_claim
from verdict_engine import judge_claim

# Prevent extremely large reports and excessive API usage
MAX_CLAIMS = 20


def run_fact_check_pipeline(
    document_text: str,
    openai_api_key: str,
    tavily_api_key: str,
    progress_callback=None,
) -> list[dict]:
    """
    Run the full fact-checking pipeline.

    Args:
        document_text: text extracted from uploaded PDF
        groq_api_key: Groq API key
        tavily_api_key: Tavily API key
        progress_callback: optional callback for UI progress updates

    Returns:
        [
            {
                "claim_text": "...",
                "claim_type": "...",
                "verdict": "...",
                "correct_fact": "...",
                "reasoning": "...",
                "source_url": "..."
            }
        ]
    """

    # --------------------------------------------------
    # Step 1: Extract claims
    # --------------------------------------------------

    claims = extract_claims(
        document_text=document_text,
        openai_api_key=openai_api_key,
    )

    if not claims:
        return []

    # Limit API costs and processing time
    claims = claims[:MAX_CLAIMS]

    report = []

    total_claims = len(claims)

    # --------------------------------------------------
    # Step 2 + 3:
    # Search evidence and judge verdict
    # --------------------------------------------------

    for index, claim in enumerate(claims):

        claim_text = claim.get("claim_text", "").strip()
        claim_type = claim.get("claim_type", "unknown")

        if not claim_text:
            continue

        # Update UI progress if callback exists
        if progress_callback:
            progress_callback(
                index,
                total_claims,
                claim_text,
            )

        try:

            # ------------------------------------------
            # Search web evidence
            # ------------------------------------------

            evidence = search_evidence_for_claim(
                claim_text=claim_text,
                tavily_api_key=tavily_api_key,
            )

            # ------------------------------------------
            # Generate verdict
            # ------------------------------------------

            verdict_data = judge_claim(
                claim_text=claim_text,
                evidence=evidence,
                openai_api_key=openai_api_key,
            )

        except Exception as e:

            verdict_data = {
        "verdict": "Verification Error",
        "correct_fact": "Verification could not be completed.",
        "reasoning": f"API or verification error: {str(e)}",
        "source_url": "",
    }

        report.append(
            {
                "claim_text": claim_text,
                "claim_type": claim_type,
                "verdict": verdict_data.get("verdict", "False"),
                "correct_fact": verdict_data.get(
                    "correct_fact",
                    "No reliable information found.",
                ),
                "reasoning": verdict_data.get(
                    "reasoning",
                    "No reasoning available.",
                ),
                "source_url": verdict_data.get(
                    "source_url",
                    "",
                ),
            }
        )

    return report