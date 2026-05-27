"""
URL Shortener Utility
---------------------
Wraps any shortener that supports the standard API format:
  GET https://{site}/api?api={key}&url={long_url}  → { "shortenedUrl": "..." }

Popular compatible sites: mdisklink.com, gplinks.in, shrinkme.io, shorte.st
"""
import aiohttp
import logging
from config import Config

logger = logging.getLogger(__name__)

async def shorten_url(long_url: str) -> str:
    """
    Returns shortened URL if shortener is configured, otherwise returns original URL.
    Never raises — falls back to original on any error.
    """
    if not Config.USE_SHORTENER or not Config.SHORTENER_API or not Config.SHORTENER_SITE:
        return long_url

    try:
        api_url = f"https://{Config.SHORTENER_SITE}/api"
        params  = {"api": Config.SHORTENER_API, "url": long_url}

        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                data = await resp.json()
                # Most shorteners return "shortenedUrl" or "short_url"
                return (
                    data.get("shortenedUrl") or
                    data.get("short_url")    or
                    data.get("shortlink")    or
                    long_url
                )
    except Exception as e:
        logger.warning(f"Shortener failed: {e} — using original URL")
        return long_url
