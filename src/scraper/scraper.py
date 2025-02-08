from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List, Any
from datetime import datetime as DateTime
from typing import Coroutine, List, Sequence
import asyncio


def _limit_concurrency(
    coroutines: Sequence[Coroutine], concurrency: int
) -> List[Coroutine]:
    """Decorate coroutines to limit concurrency.
    Enforces a limit on the number of coroutines that can run concurrently in higher
    level asyncio-compatible concurrency managers like asyncio.gather(coroutines) and
    asyncio.as_completed(coroutines).
    """
    semaphore = asyncio.Semaphore(concurrency)

    async def with_concurrency_limit(coroutine: Coroutine) -> Coroutine:
        async with semaphore:
            return await coroutine

    return [with_concurrency_limit(coroutine) for coroutine in coroutines]


@dataclass
class ScraperOutput:
    """
    Data class for storing the output of a scraper or a object representing an article.
    """

    id: str  # could be a URL or a unique identifier
    title: str
    content: str
    author: str | None
    date: DateTime | None
    url: str | None

    def __repr__(self):
        return f"{self.title} by {self.author} on {self.date}"


class Scraper(ABC):
    """
    Base class for a scraper.
    """

    def __init__(self, index_url: str, num_proc=1):
        self.index_url = index_url
        self.num_proc = num_proc

    def __repr__(self):
        return self.index_url

    @abstractmethod
    async def parse_index(self) -> List[Any]:
        """
        Asynchronously parses the index page and extracts a list of URLs.

        Returns:
          List[str]: A list of URLs extracted from the index page.

        Raises:
          NotImplementedError: This method should be implemented by subclasses.
        """
        raise NotImplementedError

    @abstractmethod
    def parse_article(self, index: Any) -> ScraperOutput:
        """
        Asynchronously retrieves an article based on the given index.

        Args:
          index (str): The index or identifier of the article to retrieve, it could be a URL or a unique identifier or a object representing an article.

        Returns:
          ScraperOutput: The output containing the article data.

        Raises:
          NotImplementedError: This method is not yet implemented.
        """
        raise NotImplementedError

    async def get_articles(self) -> List[ScraperOutput]:
        """
        Asynchronously retrieves articles by parsing indexes and fetching each article.

        Returns:
          List[ScraperOutput]: A list of ScraperOutput objects representing the articles.
        """
        article_indexes = await self.parse_index()

        # fetch the articles
        article_items = await asyncio.gather(
            *_limit_concurrency(
                [self.fetch_article(index) for index in article_indexes],
                concurrency=self.num_proc,
            )
        )

        # postprocess the article items
        articles = [self.parse_article(item) for item in article_items]

        return articles

    async def fetch_article(self, index: Any) -> Any:
        """
        Asynchronously fetches an article based on the given index.
        """
        return index

    def _parse_date(self, date: str) -> DateTime:
        """
        Parses a date string into a datetime object.

        Args:
          date (str): The date string to parse.

        Returns:
          datetime: The datetime object representing the date.
        """
        try:
            return DateTime.strptime(date, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return DateTime.now()

    def _parse_title(self, title: str) -> str:
        return title.strip()

    def _parse_content(self, text: str) -> str:
        return text.strip()

    def _parse_author(self, author: str) -> str:
        return author.strip()

    def _parse_url(self, url: str) -> str:
        return url.strip()

    def _parse_id(self, id: str) -> str:
        return id.strip()
