"""validate_account — verify OAuth token + Ad Account access."""

from src.linkedin.client import LinkedInClient


async def validate_account(client: LinkedInClient, account_id: str | None = None) -> dict:
    """
    Validate that the current OAuth token has advertising access.
    Returns account info and user role.
    """
    accounts = await client.get_ad_accounts()

    if not accounts:
        return {
            "valid": False,
            "error": "No ad accounts found for this user.",
            "accounts": [],
        }

    result_accounts = []
    for acct in accounts:
        acct_id = str(acct.get("id", ""))
        info = {
            "id": acct_id,
            "name": acct.get("name", ""),
            "status": acct.get("status", ""),
            "currency": acct.get("currency", ""),
        }
        result_accounts.append(info)

    # If specific account requested, check role
    target = account_id or (result_accounts[0]["id"] if result_accounts else None)
    role_info = None
    if target:
        try:
            users = await client.get_ad_account_users(target)
            role_info = [
                {"user": u.get("user", ""), "role": u.get("role", "")}
                for u in users
            ]
        except Exception as e:
            role_info = {"error": str(e)}

    return {
        "valid": True,
        "accounts": result_accounts,
        "selected_account": target,
        "account_users": role_info,
    }
