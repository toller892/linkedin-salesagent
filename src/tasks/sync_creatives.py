"""sync_creatives — upload/associate creatives with a campaign."""

from src.linkedin.client import LinkedInClient
from src.models.mappings import AdCPCreative


async def sync_creatives(
    client: LinkedInClient,
    account_id: str,
    campaign_id: str,
    creatives: list[dict],
) -> dict:
    """
    Sync creatives to a LinkedIn campaign.
    MVP: Single Image Ad only — takes image URL + copy, creates LinkedIn creative.
    """
    results = []
    for c in creatives:
        creative = AdCPCreative(**c)

        # LinkedIn creative payload for Sponsored Content (Single Image)
        payload = {
            "campaign": f"urn:li:sponsoredCampaign:{campaign_id}",
            "intendedStatus": "ACTIVE",
            "content": {
                "singleImage": {
                    "imageUrl": creative.image_url,
                    "headline": creative.headline,
                    "description": creative.description,
                    "landingPageUrl": creative.landing_url,
                }
            },
        }

        try:
            result = await client.create_creative(account_id, payload)
            results.append({
                "creative_id": creative.creative_id,
                "linkedin_creative_id": result.get("id", ""),
                "status": "SYNCED",
            })
        except Exception as e:
            results.append({
                "creative_id": creative.creative_id,
                "status": "FAILED",
                "error": str(e),
            })

    return {
        "campaign_id": campaign_id,
        "synced": len([r for r in results if r["status"] == "SYNCED"]),
        "failed": len([r for r in results if r["status"] == "FAILED"]),
        "details": results,
    }
