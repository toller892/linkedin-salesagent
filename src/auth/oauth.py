"""LinkedIn OAuth2 flow."""

import httpx
from urllib.parse import urlencode


AUTHORIZE_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

SCOPES = ["rw_ads", "r_ads_reporting", "r_organization_admin"]


def get_authorization_url(client_id: str, redirect_uri: str, state: str = "random123") -> str:
    """Build the OAuth2 authorization URL."""
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "state": state,
        "scope": " ".join(SCOPES),
    }
    return f"{AUTHORIZE_URL}?{urlencode(params)}"


async def exchange_code(
    code: str, client_id: str, client_secret: str, redirect_uri: str
) -> dict:
    """Exchange authorization code for access token."""
    async with httpx.AsyncClient() as client:
        r = await client.post(
            TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
            },
        )
        r.raise_for_status()
        return r.json()
