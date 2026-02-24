"""get_media_buy_delivery — pull campaign analytics."""

from src.linkedin.client import LinkedInClient


async def get_media_buy_delivery(
    client: LinkedInClient,
    campaign_id: str,
    start_date: dict | None = None,
    end_date: dict | None = None,
) -> dict:
    """
    Get delivery metrics for a LinkedIn campaign.
    start_date/end_date: {"year": 2026, "month": 2, "day": 24}
    """
    if not start_date:
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)
        start_date = {"year": week_ago.year, "month": week_ago.month, "day": week_ago.day}
        end_date = {"year": now.year, "month": now.month, "day": now.day}

    params = {
        "q": "analytics",
        "pivot": "CAMPAIGN",
        "dateRange.start.year": start_date["year"],
        "dateRange.start.month": start_date["month"],
        "dateRange.start.day": start_date["day"],
        "timeGranularity": "DAILY",
        "campaigns": f"urn:li:sponsoredCampaign:{campaign_id}",
        "fields": "impressions,clicks,costInLocalCurrency,dateRange",
    }
    if end_date:
        params["dateRange.end.year"] = end_date["year"]
        params["dateRange.end.month"] = end_date["month"]
        params["dateRange.end.day"] = end_date["day"]

    data = await client.get_analytics(params)
    elements = data.get("elements", [])

    total_impressions = sum(e.get("impressions", 0) for e in elements)
    total_clicks = sum(e.get("clicks", 0) for e in elements)
    total_spend = sum(float(e.get("costInLocalCurrency", 0)) for e in elements)
    ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0.0

    return {
        "campaign_id": campaign_id,
        "impressions": total_impressions,
        "clicks": total_clicks,
        "spend": round(total_spend, 2),
        "ctr": round(ctr, 4),
        "daily_breakdown": elements,
    }
