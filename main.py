"""
Sebo — weekly SEO brief pipeline.
Search Console → Snapshot → Brief → Email
"""

import os
from dotenv import load_dotenv

load_dotenv()

from search_console import fetch_comparison
from snapshot import save_snapshot
from brief_generator import generate_brief
from email_sender import send_brief

SITE_URL = os.getenv("SITE_URL", "")


def run():
    print(f"[1/4] Fetching Search Console data for: {SITE_URL}")
    data = fetch_comparison(site_url=SITE_URL)
    q = data["queries"]
    print(f"      losing: {len(q['losing'])}, winning: {len(q['winning'])}, "
          f"quick wins: {len(q['quick_wins'])}, new: {len(q['new'])}")

    print("[2/4] Saving snapshot to SQLite...")
    snapshot_id = save_snapshot(SITE_URL, data)
    print(f"      Snapshot #{snapshot_id} saved → sebo.db")

    print("[3/4] Generating brief (Anthropic API)...")
    brief_html = generate_brief(data)
    print(f"      Brief generated ({len(brief_html)} chars).")

    print("[4/4] Sending email (SendGrid)...")
    send_brief(brief_html, site_url=SITE_URL)
    print(f"      Sent to: {os.getenv('USER_EMAIL')}")
    print("\nDone.")


if __name__ == "__main__":
    run()
