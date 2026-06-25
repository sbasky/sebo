# Sebo

A small, self-hosted SEO agent. Once a week it pulls your Google Search Console data, works out what changed compared to the last month, asks Claude to turn that into a plain-English brief, and emails it to you.

No dashboard to check, no subscription. It runs on your own machine (or a cheap server) and the data never leaves it.

## Why

Most SEO tools bury you in dashboards and charts you have to interpret yourself. I wanted the opposite: open my inbox on Sunday, read five minutes, know exactly what to do that week. That's all Sebo does.

## How it works

```
Search Console  →  week-over-week diff  →  SQLite snapshot  →  Claude brief  →  email
```

Each step is one file:

| File | What it does |
|------|--------------|
| `search_console.py` | Pulls the last 7 days from GSC and compares them against the average of the previous 4 weeks. Sorts keywords into losing / winning / quick wins / new. |
| `snapshot.py` | Saves every run to a local SQLite file (`sebo.db`) so you keep a history. |
| `brief_generator.py` | Sends the diff to Claude and gets back a short HTML brief with concrete actions. |
| `email_sender.py` | Wraps the brief in an email template and sends it through Resend. |
| `scheduler.py` | Fires the whole thing every Sunday at 08:00. |
| `main.py` | Runs the four steps in order. This is the entry point. |

## Setup

You'll need a Google account with Search Console access to your site, an [Anthropic API key](https://console.anthropic.com), and a [Resend](https://resend.com) account for sending mail. All three have free tiers that are plenty to start.

### 1. Install

```bash
git clone https://github.com/sbasky/sebo.git
cd sebo
pip install -r requirements.txt
```

### 2. Configure

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

```env
SITE_URL=sc-domain:yourdomain.com
USER_EMAIL=you@example.com
ANTHROPIC_API_KEY=sk-ant-...
RESEND_API_KEY=re_...
RESEND_FROM_EMAIL=Sebo <onboarding@resend.dev>
```

A couple of notes:

- `SITE_URL` uses the `sc-domain:` prefix for a domain property in Search Console, or the full `https://` URL for a URL-prefix property. Match exactly how it's registered.
- Leave `RESEND_FROM_EMAIL` as the sandbox sender until you verify your own domain in Resend. The sandbox will only deliver to the email on your Resend account, which is fine for testing.

### 3. Connect Google Search Console

This is the only fiddly part, and you only do it once.

1. Open the [Google Cloud Console](https://console.cloud.google.com) and create a project.
2. Enable the **Google Search Console API** for it.
3. Create an **OAuth 2.0 client ID** of type *Desktop app* and download the JSON.
4. Save that file as `client_secret.json` in the project root.
5. Add `http://localhost:8080/` to the client's authorized redirect URIs.

Then authenticate:

```bash
python auth.py
```

A browser window opens — sign in with the Google account that has access to your site. This writes a `token.json` that refreshes itself from then on. If you ever get an `invalid_grant` error, delete `token.json` and run it again.

## Running it

One-off run, sends the email immediately:

```bash
python main.py
```

Want to see what the email looks like first, without spending anything? This uses sample data, no API calls:

```bash
python preview_email.py
```

For the real weekly schedule, you can leave `scheduler.py` running, but on a server a cron job is simpler and survives reboots:

```cron
0 8 * * 0 cd /opt/sebo && python main.py >> /var/log/sebo.log 2>&1
```

## A few things worth knowing

- **New sites won't have much to say.** GSC needs a few weeks of data before the week-over-week comparison means anything. Give it 4–5 weeks before judging the briefs.
- **Your data stays local.** The SQLite file lives on your machine. The only things that leave are the GSC numbers Claude needs to write the brief, and the email itself.
- **Three files never get committed:** `.env`, `client_secret.json`, and `token.json`. They're in `.gitignore` already — keep them that way.

## License

[AGPL-3.0](LICENSE). If you run a modified version as a network service, you have to make your source available to its users. Do what you like with it otherwise.
