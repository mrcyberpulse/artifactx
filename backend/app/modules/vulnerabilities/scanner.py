import httpx
import logging
from typing import Any

logger = logging.getLogger("artifactx.osv")

def fetch_osv_vulnerabilities(purl: str, version: str | None) -> list[dict[str, Any]]:
    """Queries Google's OSV API for a specific package."""
    if not purl or not version:
        return []

    url = "https://api.osv.dev/v1/query"
    payload = {
        "package": {"purl": purl},
        "version": version
    }

    try:
        # Using a short timeout so we don't block the server
        response = httpx.post(url, json=payload, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        return data.get("vulns", [])
    except Exception as e:
        logger.error(f"Failed to fetch OSV data for {purl}: {e}")
        return []
