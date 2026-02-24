"""list_creative_formats — return supported ad formats."""


SUPPORTED_FORMATS = [
    {
        "format_id": "single_image",
        "name": "Single Image Ad",
        "description": "Sponsored Content with a single image in the LinkedIn feed.",
        "specs": {
            "image": {"min_width": 1200, "min_height": 627, "formats": ["jpg", "png"]},
            "headline": {"max_length": 70},
            "description": {"max_length": 200},
            "cta_options": [
                "APPLY", "DOWNLOAD", "GET_QUOTE", "LEARN_MORE",
                "SIGN_UP", "SUBSCRIBE", "REGISTER", "JOIN", "ATTEND",
            ],
        },
        "supported": True,
    },
    {
        "format_id": "carousel",
        "name": "Carousel Ad",
        "description": "Multi-card swipeable ad in the LinkedIn feed.",
        "specs": {"cards": {"min": 2, "max": 10}},
        "supported": False,  # MVP: not yet
    },
    {
        "format_id": "video",
        "name": "Video Ad",
        "description": "Sponsored Content with video.",
        "specs": {"max_duration_seconds": 600},
        "supported": False,
    },
]


async def list_creative_formats() -> dict:
    """Return available LinkedIn ad creative formats."""
    return {
        "platform": "linkedin",
        "formats": SUPPORTED_FORMATS,
        "mvp_supported": [f for f in SUPPORTED_FORMATS if f["supported"]],
    }
