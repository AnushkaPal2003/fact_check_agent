"""
web_verifier.py

Job of this module: take ONE claim and search the live web for evidence
about whether it's true, outdated, or false. Uses Tavily, which is a
search API built specifically for feeding clean results to LLMs (no
messy HTML scraping needed).

This module does NOT decide if the claim is true -- it only fetches
evidence. The decision happens in verdict_engine.py. Keeping "fetch
evidence" and "judge evidence" as separate steps makes each one easier
to test and debug on its own.
"""

from tavily import TavilyClient


def search_evidence_for_claim(
    claim_text: str,
    tavily_api_key: str,
    max_results: int = 5,
):
    """
    Search the live web for evidence related to a claim.

    Returns:
        [
            {
                "title": "...",
                "url": "...",
                "content": "..."
            }
        ]
    """

    client = TavilyClient(api_key=tavily_api_key)

    evidence = []
    seen_urls = set()

    search_queries = [
        claim_text,
        f"fact check {claim_text}",
    ]

    for query in search_queries:

        try:

            response = client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_answer=True,
            )

            # Add synthesized answer if available
            answer = response.get("answer")

            if answer:
                evidence.append(
                    {
                        "title": "Tavily Summary",
                        "url": "",
                        "content": answer,
                    }
                )

            for result in response.get("results", []):

                url = result.get("url", "")

                if url in seen_urls:
                    continue

                seen_urls.add(url)

                evidence.append(
                    {
                        "title": result.get("title", ""),
                        "url": url,
                        "content": result.get("content", ""),
                    }
                )

        except Exception:
            continue

    return evidence