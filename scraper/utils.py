import aiohttp
from tenacity import retry, stop_after_attempt, wait_fixed
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from aiosocks import Socks5Addr


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def fetch_header_location(
    url: str, conn: Optional["Socks5Addr"] = None, timeout=10, headers=None
) -> str:
    """
    Get the original url from shortened URL.

    Args:
      url (str): The URL to fetch.

    Returns:
      str: The header location of the URL.
    """
    async with aiohttp.ClientSession(connector=conn) as session:
        async with session.head(
            url, allow_redirects=True, timeout=timeout, headers=headers
        ) as response:
            return response.url


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def fetch_content(
    url: str, conn: Optional["Socks5Addr"] = None, timeout=10, headers=None
) -> str:
    """
    Get the content of the URL.

    Args:
      url (str): The URL to fetch.

    Returns:
      str: The content of the URL.
    """
    async with aiohttp.ClientSession(connector=conn) as session:
        async with session.get(url, timeout=timeout, headers=headers) as response:
            return await response.text()


# @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def fetch_json(
    url: str,
    conn: Optional["Socks5Addr"] = None,
    timeout=10,
    method="GET",
    headers=None,
    body=None,
) -> dict:
    """
    Get the JSON content of the URL.

    Args:
      url (str): The URL to fetch.

    Returns:
      dict: The JSON content of the URL.
    """
    async with aiohttp.ClientSession(connector=conn) as session:
        headers = headers or {}
        headers.setdefault("Content-Type", "application/json")
        headers.setdefault("Accept", "application/json")
        headers.setdefault("x-requested-with", "XMLHttpRequest")

        async with session.request(
            method, url, timeout=timeout, headers=headers, data=body
        ) as response:
            return await response.json()


def text_processing(text: str) -> str:
    """
    Process text by removing extra spaces and newlines.

    Args:
      text (str): The text to process.

    Returns:
      str: The processed text.
    """
    return text.strip().replace("\u3000", "")
