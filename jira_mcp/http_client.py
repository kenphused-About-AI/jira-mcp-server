import base64
import aiohttp
from .config import JIRA_USERNAME, JIRA_API_TOKEN

_session: aiohttp.ClientSession | None = None

async def get_session() -> aiohttp.ClientSession:
    global _session
    if _session and not _session.closed:
        return _session

    auth = base64.b64encode(
        f"{JIRA_USERNAME}:{JIRA_API_TOKEN}".encode()
    ).decode()

    _session = aiohttp.ClientSession(
        headers={
            "Authorization": f"Basic {auth}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        timeout=aiohttp.ClientTimeout(total=30),
        raise_for_status=False,
    )
    return _session

async def close_session():
    global _session
    if _session:
        await _session.close()
        _session = None
