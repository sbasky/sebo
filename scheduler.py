"""
Sebo scheduler — runs the weekly SEO brief every Sunday at 08:00.

Local usage:  python scheduler.py
Hetzner cron: 0 8 * * 0 cd /opt/sebo-alpha && python main.py >> /var/log/sebo.log 2>&1
"""

import time
import logging
import schedule
from main import run

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M",
)
log = logging.getLogger(__name__)


def job():
    log.info("Running weekly brief...")
    try:
        run()
        log.info("Weekly brief sent.")
    except Exception as e:
        log.error(f"Error: {e}")


schedule.every().sunday.at("08:00").do(job)

log.info("Scheduler started. Next brief: Sunday 08:00.")

while True:
    schedule.run_pending()
    time.sleep(60)
