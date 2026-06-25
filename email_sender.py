"""
Email sender for the weekly SEO brief via Resend.
Accepts HTML content directly from brief_generator.
"""

import os
import re
from datetime import date
import resend
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

USER_EMAIL = os.getenv("USER_EMAIL")
RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "Sebo <onboarding@resend.dev>")


def _sectionize(html: str) -> str:
    """Split on <h2 boundaries and wrap each block in a section div."""
    parts = re.split(r'(?=<h2)', html.strip())
    out = []
    for part in parts:
        part = part.strip()
        if part:
            out.append(
                f'<tr><td style="padding:28px 32px; border-bottom:1px solid #e4e4e7;">{part}</td></tr>'
            )
    return "\n".join(out) if out else f'<tr><td style="padding:28px 32px;">{html}</td></tr>'


def _wrap_html(content: str, site_url: str) -> str:
    domain = (
        site_url.replace("sc-domain:", "")
        .replace("https://", "")
        .replace("http://", "")
        .rstrip("/")
    )
    week = date.today().strftime("%d %b %Y")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  body {{
    margin: 0; padding: 0;
    background: #f7f7f5;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    color: #18181b;
    font-size: 15px;
    line-height: 1.7;
    -webkit-font-smoothing: antialiased;
  }}

  /* h2 pill */
  h2 {{
    display: inline-block;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #1a5c47;
    background: #e8f2ed;
    padding: 4px 11px;
    border-radius: 100px;
    margin: 0 0 20px 0;
    line-height: 1.5;
  }}

  /* Body text */
  p {{ font-size: 14px; line-height: 1.75; color: #18181b; margin: 0 0 10px 0; }}

  /* Lists */
  ul {{ list-style: none; padding: 0; margin: 0; }}
  li {{
    font-size: 14px; line-height: 1.7; color: #18181b;
    padding: 9px 0 9px 14px;
    border-left: 2px solid #e4e4e7;
    margin-bottom: 20px;
  }}
  li:last-child {{ margin-bottom: 0; }}

  /* Action callout */
  .action {{
    display: block;
    background: #e8f2ed;
    border-left: 3px solid #1a5c47;
    padding: 10px 14px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 13px;
    color: #1a5c47;
    margin-top: 8px;
    line-height: 1.5;
  }}

  /* Recommendation section */
  .rec-title {{
    font-size: 15px; font-weight: 700; color: #18181b;
    margin: 0 0 12px 0; line-height: 1.5;
  }}
  .rec-context {{
    font-size: 14px; color: #71717a;
    margin: 0 0 16px 0; line-height: 1.7;
  }}
  .rec-step {{
    display: block;
    background: #e8f2ed;
    border-left: 3px solid #1a5c47;
    padding: 10px 14px;
    border-radius: 6px;
    font-size: 13px;
    color: #1a5c47;
    line-height: 1.5;
    margin-bottom: 8px;
  }}
  .rec-step:last-child {{ margin-bottom: 0; }}
  .rec-step-num {{ font-weight: 700; margin-right: 6px; }}

  strong {{ font-weight: 600; color: #18181b; }}
  em {{ color: #71717a; font-style: normal; }}
  a, a:link, a:visited, a:hover {{
    color: #1a5c47 !important;
    text-decoration: none !important;
  }}
</style>
</head>
<body style="margin:0; padding:0; background:#f7f7f5;">

<!-- Outer centering table -->
<table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#f7f7f5">
<tr>
  <td align="center" style="padding:28px 16px 40px;">

  <!-- Card -->
  <table width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px; width:100%; background:#ffffff; border:1px solid #e4e4e7; border-radius:16px; overflow:hidden;">

    <!-- Nav -->
    <tr>
      <td style="padding:16px 28px; border-bottom:1px solid #e4e4e7;">
        <table width="100%" cellpadding="0" cellspacing="0" border="0">
          <tr>
            <td width="70%" style="vertical-align:middle;">
              <img src="https://get-sebo.com/icon-32.png" width="32" height="32" alt="S" style="display:inline-block;vertical-align:middle;border-radius:50%;">
              <span style="display:inline-block; font-size:17px; font-weight:700; letter-spacing:-0.02em; color:#18181b; vertical-align:middle; margin-left:9px;">Sebo</span>
            </td>
            <td width="30%" align="right" style="vertical-align:middle; font-size:12px; color:#71717a; white-space:nowrap;">{week}</td>
          </tr>
        </table>
      </td>
    </tr>

    <!-- Hero -->
    <tr>
      <td align="center" style="padding:28px 28px 24px; border-bottom:1px solid #e4e4e7; background-color:#f7f7f5; text-align:center;">
        <span style="display:inline-block; background:#e8f2ed; border:1px solid rgba(26,92,71,0.2); color:#1a5c47; font-size:11px; font-weight:600; letter-spacing:0.05em; text-transform:uppercase; padding:4px 12px; border-radius:100px;">Weekly SEO Brief</span>
        <a href="https://{domain}" style="display:block; font-size:22px; font-weight:700; letter-spacing:-0.02em; color:#18181b !important; text-decoration:none !important; margin-top:12px; line-height:1.2;">{domain}</a>
        <div style="font-size:13px; color:#71717a; margin-top:6px;">Rankings &amp; actions for this week</div>
      </td>
    </tr>

    <!-- Brief sections -->
    {_sectionize(content)}

    <!-- Footer -->
    <tr>
      <td style="padding:18px 28px; border-top:1px solid #e4e4e7; background:#ffffff;">
        <table width="100%" cellpadding="0" cellspacing="0" border="0">
          <tr>
            <td width="50%" style="font-size:14px; font-weight:700; color:#18181b; vertical-align:middle;">Sebo</td>
            <td width="50%" align="right" style="vertical-align:middle;"><a href="https://get-sebo.com" style="font-size:12px; color:#71717a !important; text-decoration:none !important;">get-sebo.com</a></td>
          </tr>
        </table>
      </td>
    </tr>

  </table>
  <!-- /Card -->

  </td>
</tr>
</table>
<!-- /Outer -->

</body>
</html>"""


def _strip_html(html: str) -> str:
    return re.sub(r"<[^>]+>", "", html).strip()


def send_brief(html_content: str, site_url: str = None) -> bool:
    """Send the weekly SEO brief via Resend. Returns True on success."""
    if not resend.api_key:
        raise ValueError("RESEND_API_KEY not set in .env")
    if not USER_EMAIL:
        raise ValueError("USER_EMAIL not set in .env")

    site_url = site_url or os.getenv("SITE_URL", "")
    domain = site_url.replace("sc-domain:", "").rstrip("/")
    week = date.today().strftime("%d %b %Y")
    subject = f"Sebo SEO Brief — {domain} — {week}"

    resend.Emails.send({
        "from": RESEND_FROM_EMAIL,
        "to": USER_EMAIL,
        "subject": subject,
        "text": _strip_html(html_content),
        "html": _wrap_html(html_content, site_url),
    })

    return True
