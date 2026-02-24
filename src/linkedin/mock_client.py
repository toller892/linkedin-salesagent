"""Mock LinkedIn client for testing without real credentials."""

from typing import Any

_MOCK_ACCOUNTS = [
    {
        "id": "500000001",
        "name": "Test Ad Account",
        "status": "ACTIVE",
        "currency": "USD",
    }
]

_MOCK_USERS = [
    {"user": "urn:li:person:mock123", "role": "CAMPAIGN_MANAGER"}
]

_counter = {"group": 900000, "campaign": 800000, "creative": 700000}


class MockLinkedInClient:
    """Drop-in replacement for LinkedInClient, returns fake data."""

    def __init__(self, access_token: str = "mock-token"):
        self.access_token = access_token

    async def get(self, path: str, params: dict | None = None) -> dict[str, Any]:
        if "/adAccounts" in path and "/adAccountUsers" not in path:
            return {"elements": _MOCK_ACCOUNTS}
        if "/adAccountUsers" in path:
            return {"elements": _MOCK_USERS}
        if "/adAnalytics" in path:
            return {"elements": [
                {
                    "impressions": 12450,
                    "clicks": 187,
                    "costInLocalCurrency": "23.45",
                    "dateRange": {"start": {"year": 2026, "month": 2, "day": 20}, "end": {"year": 2026, "month": 2, "day": 24}},
                }
            ]}
        return {"elements": []}

    async def post(self, path: str, json: dict) -> dict[str, Any]:
        if "/adCampaignGroups" in path:
            _counter["group"] += 1
            return {"id": str(_counter["group"])}
        if "/adCampaigns" in path:
            _counter["campaign"] += 1
            return {"id": str(_counter["campaign"])}
        if "/adCreatives" in path:
            _counter["creative"] += 1
            return {"id": str(_counter["creative"])}
        return {"id": "unknown"}

    async def get_ad_accounts(self) -> list[dict]:
        return _MOCK_ACCOUNTS

    async def get_ad_account_users(self, account_id: str) -> list[dict]:
        return _MOCK_USERS

    async def create_campaign_group(self, account_id: str, payload: dict) -> dict:
        return await self.post("/adCampaignGroups", payload)

    async def create_campaign(self, account_id: str, payload: dict) -> dict:
        return await self.post("/adCampaigns", payload)

    async def create_creative(self, account_id: str, payload: dict) -> dict:
        return await self.post("/adCreatives", payload)

    async def get_analytics(self, params: dict) -> dict:
        return await self.get("/adAnalytics", params)

    async def close(self):
        pass
