"""create_media_buy — create a LinkedIn campaign from AdCP media buy."""

from src.linkedin.client import LinkedInClient
from src.models.mappings import AdCPMediaBuy, media_buy_to_campaign_group, media_buy_to_campaign


async def create_media_buy(client: LinkedInClient, account_id: str, buy: AdCPMediaBuy) -> dict:
    """
    Create a LinkedIn Campaign Group + Campaign from an AdCP media buy.
    Returns the created resource IDs.
    """
    # 1. Create Campaign Group
    group_payload = media_buy_to_campaign_group(buy)
    group_result = await client.create_campaign_group(account_id, group_payload)
    group_id = group_result.get("id", "")
    group_urn = f"urn:li:sponsoredCampaignGroup:{group_id}"

    # 2. Create Campaign under the group
    campaign_payload = media_buy_to_campaign(buy, group_urn)
    campaign_result = await client.create_campaign(account_id, campaign_payload)
    campaign_id = campaign_result.get("id", "")

    return {
        "media_buy_id": buy.buyer_reference,
        "linkedin_campaign_group_id": group_id,
        "linkedin_campaign_id": campaign_id,
        "status": "CREATED",
        "budget": {
            "total": buy.budget_amount,
            "daily": buy.daily_budget or round(buy.budget_amount / 30, 2),
            "currency": buy.budget_currency,
        },
    }
