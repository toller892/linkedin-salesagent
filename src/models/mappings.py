"""AdCP ↔ LinkedIn data model mappings."""

from pydantic import BaseModel
from typing import Optional


# --- AdCP Models ---

class AdCPCreative(BaseModel):
    """AdCP creative format."""
    creative_id: str
    name: str
    image_url: str
    headline: str
    description: str
    landing_url: str


class AdCPMediaBuy(BaseModel):
    """AdCP create_media_buy request."""
    buyer_reference: str
    brand_name: str
    budget_amount: float
    budget_currency: str = "USD"
    daily_budget: Optional[float] = None
    start_date: str  # ISO 8601
    end_date: Optional[str] = None
    targeting: Optional[dict] = None
    creative_id: Optional[str] = None


class AdCPDeliveryReport(BaseModel):
    """AdCP delivery report."""
    media_buy_id: str
    impressions: int = 0
    clicks: int = 0
    spend: float = 0.0
    ctr: float = 0.0
    date_range: Optional[dict] = None


# --- Mapping helpers ---

def media_buy_to_campaign_group(buy: AdCPMediaBuy) -> dict:
    """Map AdCP media buy to LinkedIn Campaign Group payload."""
    payload = {
        "name": f"{buy.brand_name} - {buy.buyer_reference}",
        "status": "ACTIVE",
        "runSchedule": {"start": buy.start_date},
        "totalBudget": {
            "amount": str(buy.budget_amount),
            "currencyCode": buy.budget_currency,
        },
    }
    if buy.end_date:
        payload["runSchedule"]["end"] = buy.end_date
    return payload


def media_buy_to_campaign(buy: AdCPMediaBuy, campaign_group_urn: str) -> dict:
    """Map AdCP media buy to LinkedIn Campaign payload."""
    daily = buy.daily_budget or round(buy.budget_amount / 30, 2)
    payload = {
        "campaignGroup": campaign_group_urn,
        "name": f"{buy.brand_name} campaign",
        "type": "SPONSORED_UPDATES",
        "costType": "CPM",
        "dailyBudget": {
            "amount": str(daily),
            "currencyCode": buy.budget_currency,
        },
        "targetingCriteria": _build_targeting(buy.targeting),
        "status": "ACTIVE",
    }
    return payload


def _build_targeting(targeting: dict | None) -> dict:
    """Build LinkedIn targeting criteria from AdCP targeting dict."""
    if not targeting:
        # Default: US, English
        return {
            "include": {
                "and": [
                    {"or": {"geoTargetedLocations": ["urn:li:geo:103644278"]}},
                    {"or": {"interfaceLocales": [{"language": "en"}]}},
                ]
            }
        }

    criteria = {"include": {"and": []}}
    if "locations" in targeting:
        criteria["include"]["and"].append(
            {"or": {"geoTargetedLocations": targeting["locations"]}}
        )
    if "languages" in targeting:
        locales = [{"language": lang} for lang in targeting["languages"]]
        criteria["include"]["and"].append({"or": {"interfaceLocales": locales}})
    if "industries" in targeting:
        criteria["include"]["and"].append(
            {"or": {"industries": targeting["industries"]}}
        )

    # Fallback if empty
    if not criteria["include"]["and"]:
        return _build_targeting(None)

    return criteria


def creative_to_linkedin(creative: AdCPCreative, account_id: str) -> dict:
    """Map AdCP creative to LinkedIn creative payload."""
    return {
        "campaign": "",  # filled by caller
        "reference": creative.landing_url,
        "intendedStatus": "ACTIVE",
        "type": "SPONSORED_STATUS_UPDATE",
    }
