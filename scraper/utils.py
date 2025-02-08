import aiohttp
from tenacity import retry, stop_after_attempt, wait_fixed
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from aiosocks import Socks5Addr


# @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def fetch_header_location(
    url: str, conn: Optional["Socks5Addr"] = None, timeout=10
) -> str:
    """
    Get the original url from shortened URL.

    Args:
      url (str): The URL to fetch.

    Returns:
      str: The header location of the URL.
    """
    async with aiohttp.ClientSession(connector=conn) as session:
        async with session.head(url, allow_redirects=True, timeout=timeout) as response:
            return response.url


# @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def fetch_content(
    url: str, conn: Optional["Socks5Addr"] = None, timeout=10
) -> str:
    """
    Get the content of the URL.

    Args:
      url (str): The URL to fetch.

    Returns:
      str: The content of the URL.
    """
    async with aiohttp.ClientSession(connector=conn) as session:
        async with session.get(url, timeout=timeout) as response:
            return await response.text()
