import json
from .config import JIRA_URL
from .http_client import get_session
from .sanitization import sanitize_endpoint

async def jira_request(
    endpoint: str,
    *,
    method: str = "GET",
    params: dict | None = None,
    json_body: dict | None = None,
):
    endpoint = sanitize_endpoint(endpoint)
    url = f"{JIRA_URL}/rest/api/3/{endpoint}"

    session = await get_session()
    async with session.request(
        method,
        url,
        params=params,
        json=json_body,
    ) as resp:
        text = await resp.text()
        if resp.status >= 400:
            raise RuntimeError(f"Jira {resp.status}: {text}")
        return json.loads(text) if text else {}
