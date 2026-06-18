"""

claim_extractor.py

Extracts factual, verifiable claims from PDF text using Groq.

The goal is high recall:
- Statistics
- Dates
- Financial figures
- Technical metrics
- Company facts
- Historical facts
- User counts
- Market claims

Output:
[
    {
        "claim_text": "...",
        "claim_type": "statistic"
    }
]
"""

import json
from openai import OpenAI

#client = OpenAI(api_key=OPENAI_API_KEY)

MAX_INPUT_CHARS = 25000


EXTRACTION_SYSTEM_PROMPT = """
You are a precise claim extraction engine.

You will receive raw text extracted from a PDF.

Your task is to identify ALL factual claims that can be verified using
public sources.

A factual claim is ANY statement that can be checked against a reliable
external source.

Extract claims from categories including:

- Statistics and percentages
- Dates and years
- Financial figures
- Technical metrics
- User counts
- Market share claims
- Company facts
- Historical facts
- Scientific facts
- Geography and location facts
- Organization facts
- Product facts

Examples:

- OpenAI was founded in 2015.
- Tesla is headquartered in Austin, Texas.
- Google was founded in 1998.
- The capital of Australia is Canberra.
- The Eiffel Tower is located in Paris.
- The United Nations was established in 1945.
- Python was first released in 1991.
- Revenue increased by 240%.
- Used by over 10,000 businesses.

DO NOT extract:

- Opinions
- Marketing slogans
- Subjective statements
- Generic praise

Examples to ignore:

- Industry-leading platform
- Best solution available
- World-class service
- Revolutionary product

Return ONLY valid JSON.

Format:

{
  "claims": [
    {
      "claim_text": "Google was founded in 1998",
      "claim_type": "historical"
    }
  ]
}

If no claims exist:

{
  "claims": []
}
"""


def extract_claims(document_text: str, openai_api_key: str) -> list[dict]:
    """
    Extract factual claims from a document.

    Args:
        document_text: extracted PDF text
        groq_api_key: Groq API key

    Returns:
        List[dict]
    """

    if not document_text:
        return []

    # Prevent context window issues
    document_text = document_text[:MAX_INPUT_CHARS]

    
    client = OpenAI(api_key=openai_api_key)

    response = client.chat.completions.create(
    model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": EXTRACTION_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": document_text,
            },
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    raw_output = response.choices[0].message.content

    try:
        parsed = json.loads(raw_output)
        claims = parsed.get("claims", [])

    except Exception:
        return []

    # Deduplicate claims
    unique_claims = []
    seen = set()

    for claim in claims:

        claim_text = (
            claim.get("claim_text", "")
            .strip()
        )

        claim_type = (
            claim.get("claim_type", "unknown")
            .strip()
            .lower()
        )

        if not claim_text:
            continue

        normalized = claim_text.lower()

        if normalized in seen:
            continue

        seen.add(normalized)

        unique_claims.append(
            {
                "claim_text": claim_text,
                "claim_type": claim_type,
            }
        )

    return unique_claims