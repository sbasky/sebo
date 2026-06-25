"""
Brief generator — produces an HTML SEO brief from comparison data.
Uses claude-opus-4-8 with adaptive thinking.
"""

import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def _build_prompt(data: dict) -> str:
    current = data["current_period"]
    queries = data.get("queries", {})
    pages = data.get("pages", {})

    def top(lst, n=8):
        return json.dumps(lst[:n], indent=2)

    return f"""You are an expert SEO advisor writing a weekly brief for a SaaS founder.

Current week: {current["start"]} to {current["end"]}
Site: {data["site_url"]}
Baseline: average of the previous 4 weeks. delta_position > 0 means position dropped (worse).

## KEYWORDS LOSING POSITIONS:
{top(queries.get("losing", []))}

## KEYWORDS WINNING POSITIONS:
{top(queries.get("winning", []))}

## QUICK WIN KEYWORDS (positions 8-15, high impressions):
{top(queries.get("quick_wins", []))}

## PAGES LOSING POSITIONS:
{top(pages.get("losing", []))}

## QUICK WIN PAGES (positions 8-15):
{top(pages.get("quick_wins", []))}

Write a concise weekly SEO brief in HTML with exactly these four sections:

<h2>📉 Keywords Losing Positions</h2>
Top 5 keywords that dropped. Structure each <li> as three layers:
  Line 1: <strong>Keyword Name</strong> — position dropped from X to Y (<span style="color:#dc2626">▼ Z spots</span>)
  Line 2: <span style="color:#71717a">One sentence explaining why this matters.</span>
  Line 3: <span class="action">Action: Specific thing to do.</span>

<h2>⚡ Quick Wins This Week</h2>
Top 5 keywords at positions 8-15 with highest impressions. Structure each <li> as:
  Line 1: <strong>Keyword Name</strong> — position <span style="color:#1a5c47">X</span>, Y impressions
  Line 2: <span style="color:#71717a">One sentence on the opportunity.</span>
  Line 3: <span class="action">Action: Specific thing to push it to page one.</span>

<h2>✅ What's Working — Don't Touch</h2>
Top 5 keywords that improved or are stable. Structure each <li> as:
  Line 1: <strong>Keyword Name</strong> — position improved from X to Y (<span style="color:#1a5c47">▲ Z spots</span>)
  Line 2: <span style="color:#71717a">One sentence on what's working.</span>
  No action needed.

<h2>🎯 This Week's Main Recommendation</h2>
Structure as follows — no plain paragraphs:
  <p class="rec-title">One bold sentence: the main insight. Use <span style="color:#dc2626">▼ X spots</span> for drops and <span style="color:#1a5c47">▲ X spots</span> for gains inline when mentioning position changes.</p>
  <p class="rec-context">One sentence of context. Use <span style="color:#dc2626">red</span> for bad numbers (dropped positions) and <span style="color:#1a5c47">green</span> for good numbers (impressions up, positions improved) inline.</p>
  <div class="rec-step"><span class="rec-step-num">1.</span> First specific action — exact thing to do.</div>
  <div class="rec-step"><span class="rec-step-num">2.</span> Second specific action — exact thing to do.</div>
  <div class="rec-step"><span class="rec-step-num">3.</span> Third specific action — exact thing to do.</div>

Rules:
- Reference actual keywords and pages from the data above.
- No SEO jargon. Write for a smart founder, not a specialist.
- Total: 350-550 words.
- Use only: <h2>, <ul>, <li>, <p>, <strong>, <span>, <em>. No markdown.
- Do NOT include <html>, <head>, <body> tags.
- Capitalize the first letter of every keyword or page name in <strong> tags (e.g. <strong>Sebo</strong>, not <strong>sebo</strong>).
- Use inline style="color:#dc2626" for dropped positions (worse), style="color:#1a5c47" for improved positions (better)."""


def generate_brief(data: dict) -> str:
    """
    Generate an HTML SEO brief from fetch_comparison() output.
    Returns raw HTML content (no html/head/body wrapper).
    """
    prompt = _build_prompt(data)

    with client.messages.stream(
        model="claude-opus-4-8",
        max_tokens=2000,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        msg = stream.get_final_message()

    for block in msg.content:
        if block.type == "text":
            return block.text

    return "<p>Brief generation failed — no text block returned.</p>"


if __name__ == "__main__":
    from search_console import fetch_comparison

    site_url = os.getenv("SITE_URL", "")
    print(f"Fetching data for: {site_url}")
    data = fetch_comparison(site_url=site_url)
    print("Generating brief...")
    brief = generate_brief(data)
    print("\n--- BRIEF ---")
    print(brief)
