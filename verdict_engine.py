
import json
from openai import OpenAI


VERDICT_SYSTEM_PROMPT = """You are a strict fact-checking judge.

You will receive:
1. A CLAIM made in a document.
2. EVIDENCE: snippets pulled from live web search results about that claim.

Decide ONE verdict for the claim:
- "Verified"   = the evidence confirms the claim is accurate and current.
- "Inaccurate" = the claim was true at some point, but evidence shows
                 it is outdated (numbers/dates have since changed).
- "False"      = the evidence contradicts the claim, or there is no
                 evidence anywhere supporting it.

Be skeptical. If the evidence is empty, weak, or unrelated, do NOT mark
the claim "Verified" -- mark it "False" and say no evidence was found.

Return ONLY valid JSON, in this exact structure, no markdown fences,
no extra text:

{
  "verdict": "Verified | Inaccurate | False",
  "correct_fact": "the accurate current fact, based on evidence (or 'No reliable data found' if none exists)",
  "reasoning": "one or two sentences explaining the verdict, referencing the evidence",
  "source_url": "the single most relevant URL from the evidence, or empty string if none"
}
"""


def judge_claim(claim_text: str, evidence: list[dict], openai_api_key: str) -> dict:
    """
    Sends a claim + its web evidence to Open AI's LLM and gets back a
    structured verdict.

    Args:
        claim_text: the claim being checked
        evidence: list of evidence dicts from web_verifier.py
        open_api_key: the user's Open API key

    Returns:
        dict like:
        {
            "verdict": "Inaccurate",
            "correct_fact": "...",
            "reasoning": "...",
            "source_url": "..."
        }
    """
    client = OpenAI(api_key=openai_api_key)

    # Turn the evidence list into readable text for the prompt
    if evidence:
        evidence_text = "\n\n".join(
            f"Source: {item['title']}\nURL: {item['url']}\nSnippet: {item['content']}"
            for item in evidence
        )
    else:
        evidence_text = "No web evidence was found for this claim."

    user_message = f"CLAIM:\n{claim_text}\n\nEVIDENCE:\n{evidence_text}"

    response = client.chat.completions.create(
    model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": VERDICT_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    raw_output = response.choices[0].message.content

    try:
        verdict_data = json.loads(raw_output)
    except json.JSONDecodeError:
        
        verdict_data = {
            "verdict": "False",
            "correct_fact": "Could not be determined (verification error).",
            "reasoning": "The verification step failed to produce a valid result.",
            "source_url": "",
        }

    return verdict_data