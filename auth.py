"""
Google OAuth2 authentication for Search Console API.
Handles token generation, storage, and refresh.
"""

from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
CLIENT_SECRET_FILE = "client_secret.json"
TOKEN_FILE = "token.json"


def get_credentials() -> Credentials:
    """Get valid credentials, refreshing or re-authenticating as needed."""
    creds = None

    if Path(TOKEN_FILE).exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            print("Token refreshed.")
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=8080)
            print("Authentication successful.")

        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    return creds


def get_search_console_service():
    """Return an authenticated Search Console API service."""
    creds = get_credentials()
    return build("webmasters", "v3", credentials=creds)


if __name__ == "__main__":
    print("Testing Google OAuth authentication...")
    service = get_search_console_service()

    sites = service.sites().list().execute()
    print("\nSites you have access to:")
    for site in sites.get("siteEntry", []):
        print(f"  - {site['siteUrl']} ({site['permissionLevel']})")
