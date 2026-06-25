"""
Local email preview — generates email.html and opens it in the browser.
No API calls, no costs.
"""

import os
import webbrowser
from email_sender import _wrap_html, _sectionize

SAMPLE_CONTENT = """
<h2>📉 Keywords Losing Positions</h2>
<ul>
  <li>
    <strong>Sebo</strong> — position dropped from 43.9 to 48.4 (<span style="color:#dc2626">▼ 4.5 spots</span>)
    <span style="color:#71717a;display:block;margin-top:4px;">You're ranking on page five for your own brand name — this is the biggest leak in your funnel.</span>
    <span class="action">Action: Update your homepage title tag to "Sebo — AI SEO agent for SaaS founders" and add a clear one-line description above the fold.</span>
  </li>
  <li>
    <strong>SEO agent</strong> — position dropped from 31.2 to 36.8 (<span style="color:#dc2626">▼ 5.6 spots</span>)
    <span style="color:#71717a;display:block;margin-top:4px;">This is a high-intent keyword — people searching it are looking for a tool, not a blog post.</span>
    <span class="action">Action: Create a dedicated landing page targeting "AI SEO agent for founders" with a clear headline and a waitlist CTA.</span>
  </li>
</ul>

<h2>⚡ Quick Wins This Week</h2>
<ul>
  <li>
    <strong>Google Search Console guide</strong> — position <span style="color:#1a5c47">12.4</span>, 89 impressions
    <span style="color:#71717a;display:block;margin-top:4px;">You're close to page one on a high-volume informational keyword that drives relevant traffic.</span>
    <span class="action">Action: Strengthen the H1 to exactly match the query and add 3 internal links from other blog posts pointing to this page.</span>
  </li>
  <li>
    <strong>SEO for SaaS startups</strong> — position <span style="color:#1a5c47">14.1</span>, 54 impressions
    <span style="color:#71717a;display:block;margin-top:4px;">Bottom of page one is within reach — this keyword has clear buying intent from your target audience.</span>
    <span class="action">Action: Expand the intro paragraph with a concrete definition and add a comparison table showing Sebo vs manual SEO work.</span>
  </li>
</ul>

<h2>✅ What's Working — Don't Touch</h2>
<ul>
  <li>
    <strong>Keyword gap analysis</strong> — position improved from 9.1 to 8.2 (<span style="color:#1a5c47">▲ 0.9 spots</span>)
    <span style="color:#71717a;display:block;margin-top:4px;">Holding steady in the top 10 with 120 impressions — whatever you did on this page last month is paying off.</span>
  </li>
  <li>
    <strong>Semrush alternative</strong> — position improved from 10.3 to 9.6 (<span style="color:#1a5c47">▲ 0.7 spots</span>)
    <span style="color:#71717a;display:block;margin-top:4px;">Slowly climbing with 77 impressions. Leave this page alone and let it continue gaining authority.</span>
  </li>
</ul>

<h2>🎯 This Week's Main Recommendation</h2>
<p class="rec-title">Your homepage fell <span style="color:#dc2626">▼ 8.7 spots</span> while impressions jumped <span style="color:#1a5c47">▲ 41</span> — Google is showing you more but ranking you lower.</p>
<p class="rec-context">Position dropped from <span style="color:#1a5c47">34.9</span> to <span style="color:#dc2626">43.6</span> as impressions went from 11 to <span style="color:#1a5c47">52</span> — a sign Google is unsure what your site is about.</p>
<div class="rec-step"><span class="rec-step-num">1.</span> Update your homepage title tag to "Sebo — AI SEO agent for SaaS founders" so Google knows exactly what this page is about.</div>
<div class="rec-step"><span class="rec-step-num">2.</span> Add a one-sentence description in the hero — above the fold — that uses the word "Sebo" naturally and explains what it does.</div>
<div class="rec-step"><span class="rec-step-num">3.</span> Add a 150-word FAQ block near the bottom of the homepage answering "What is Sebo?", "Who is it for?", and "How does Sebo work?" — this reinforces brand relevance for Google.</div>
"""

OUTPUT_FILE = "email_preview.html"
SITE_URL = os.getenv("SITE_URL", "sc-domain:your-url.com")

html = _wrap_html(SAMPLE_CONTENT, SITE_URL)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Preview saved to {OUTPUT_FILE}")
webbrowser.open(f"file://{os.path.abspath(OUTPUT_FILE)}")
