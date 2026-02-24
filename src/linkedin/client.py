"""LinkedIn Marketing API client."""

import httpx
from typing import Any


API_BASE = "https://api.linkedin.com/rest"
API_VERSION = "202402"


class LinkedInClient:
    """Thin wrapper around LinkedIn Marketing API."""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self._client = httpx.AsyncClient(
            base_url=API_BASE,
            headers={
                "Authorization": f"Bearer {access_token}",
                "LinkedIn-Version": API_VERSION,
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0",
            },
            timeout=30.0,
        )

    async def get(self, path: str, params: dict | None = None) -> dict[str, Any]:
        r = await self._client.get(path, params=params)
        r.raise_for_status()
        return r.json()

    async def post(self, path: str, json: dict) -> dict[str, Any]:
        r = await self._client.post(path, json=json)
        r.raise_for_status()
        return r.json()

    async def close(self):
        await self._client.aclose()

    # --- Ad Account ---

    async def get_ad_accounts(self) -> list[dict]:
        """List ad accounts the authenticated user has access to."""
        data = await self.get("/adAccounts", params={"q": "search"})
        return data.get("elements", [])

    async def get_ad_account_users(self, account_id: str) -> list[dict]:
        """List users and their roles on an ad account."""
        urn = f"urn:li:sponsoredAccount:{account_id}"
        data = await self.get("/adAccountUsers", params={"q": "accounts", "accounts": urn})
        return data.get("elements", [])

    # --- Campaign Group ---

    async def create_campaign_group(self, account_id: str, payload: dict) -> dict:
        payload["account"] = f"urn:li:sponsoredAccount:{account_id}"
        return await self.post("/adCampaignGroups", json=payload)

    # --- Campaign ---

    async def create_campaign(self, account_id: str, payload: dict) -> dict:
        payload["account"] = f"urn:li:sponsoredAccount:{account_id}"
        return await self.post("/adCampaigns", json=payload)

    # --- Creative ---

    async def create_creative(self, account_id: str, payload: dict) -> dict:
        payload["account"] = f"urn:li:sponsoredAccount:{account_id}"
        return await self.post("/adCreatives", json=payload)

    # --- Analytics ---

    async def get_analytics(self, params: dict) -> dict:
        return await self.get("/adAnalytics", params=params)
