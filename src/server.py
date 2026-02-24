"""LinkedIn AdCP Sales Agent — MCP Server."""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastmcp import FastMCP

from src.auth.oauth import get_authorization_url, exchange_code
from src.linkedin.client import LinkedInClient
from src.tasks.validate_account import validate_account
from src.tasks.list_creative_formats import list_creative_formats
from src.tasks.create_media_buy import create_media_buy as _create_media_buy
from src.tasks.sync_creatives import sync_creatives as _sync_creatives
from src.tasks.get_delivery import get_media_buy_delivery as _get_delivery
from src.models.mappings import AdCPMediaBuy

load_dotenv()

mcp = FastMCP(
    "LinkedIn AdCP Sales Agent",
    description="AdCP Sales Agent for LinkedIn Advertising — translates AdCP tasks to LinkedIn Marketing API.",
)


def _get_client() -> LinkedInClient:
    token = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
    if not token:
        raise ValueError("LINKEDIN_ACCESS_TOKEN not set. Run /auth/login first.")
    return LinkedInClient(token)


def _get_account_id() -> str:
    acct = os.getenv("LINKEDIN_AD_ACCOUNT_ID", "")
    if not acct:
        raise ValueError("LINKEDIN_AD_ACCOUNT_ID not set.")
    return acct


# --- AdCP Tasks as MCP Tools ---


@mcp.tool()
async def validate_ad_account(account_id: str | None = None) -> dict:
    """Validate LinkedIn OAuth token and Ad Account access. Returns available accounts and user roles."""
    client = _get_client()
    try:
        return await validate_account(client, account_id or _get_account_id())
    finally:
        await client.close()


@mcp.tool()
async def list_formats() -> dict:
    """List supported LinkedIn ad creative formats."""
    return await list_creative_formats()


@mcp.tool()
async def create_media_buy(
    buyer_reference: str,
    brand_name: str,
    budget_amount: float,
    start_date: str,
    budget_currency: str = "USD",
    daily_budget: float | None = None,
    end_date: str | None = None,
    targeting: dict | None = None,
) -> dict:
    """Create a LinkedIn ad campaign (Campaign Group + Campaign) from an AdCP media buy."""
    client = _get_client()
    buy = AdCPMediaBuy(
        buyer_reference=buyer_reference,
        brand_name=brand_name,
        budget_amount=budget_amount,
        budget_currency=budget_currency,
        daily_budget=daily_budget,
        start_date=start_date,
        end_date=end_date,
        targeting=targeting,
    )
    try:
        return await _create_media_buy(client, _get_account_id(), buy)
    finally:
        await client.close()


@mcp.tool()
async def sync_creatives(campaign_id: str, creatives: list[dict]) -> dict:
    """Sync ad creatives to a LinkedIn campaign. Each creative needs: creative_id, name, image_url, headline, description, landing_url."""
    client = _get_client()
    try:
        return await _sync_creatives(client, _get_account_id(), campaign_id, creatives)
    finally:
        await client.close()


@mcp.tool()
async def get_media_buy_delivery(
    campaign_id: str,
    start_date: dict | None = None,
    end_date: dict | None = None,
) -> dict:
    """Get delivery metrics (impressions, clicks, spend, CTR) for a LinkedIn campaign."""
    client = _get_client()
    try:
        return await _get_delivery(client, campaign_id, start_date, end_date)
    finally:
        await client.close()


# --- OAuth helper endpoints ---


@mcp.tool()
async def get_auth_url() -> dict:
    """Get the LinkedIn OAuth2 authorization URL. User must visit this URL to grant access."""
    client_id = os.getenv("LINKEDIN_CLIENT_ID", "")
    redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI", "")
    if not client_id:
        return {"error": "LINKEDIN_CLIENT_ID not set in .env"}
    url = get_authorization_url(client_id, redirect_uri)
    return {"authorization_url": url, "instructions": "Visit this URL, authorize, then use exchange_auth_code with the code from the redirect."}


@mcp.tool()
async def exchange_auth_code(code: str) -> dict:
    """Exchange an OAuth2 authorization code for an access token."""
    client_id = os.getenv("LINKEDIN_CLIENT_ID", "")
    client_secret = os.getenv("LINKEDIN_CLIENT_SECRET", "")
    redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI", "")
    result = await exchange_code(code, client_id, client_secret, redirect_uri)
    return {"access_token": result.get("access_token", ""), "expires_in": result.get("expires_in", 0)}


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
