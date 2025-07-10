from datetime import datetime as DateTime
import asyncio
from zoneinfo import ZoneInfo
import dateparser
from pydantic.dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List, Any, Optional, Literal, Coroutine, Sequence
from scraper.utils import text_processing

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
}


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
    content_type: Literal["text/html", "text/plain"]
    category: Literal[
        "news", "columns", "blog", "encyclopedia", "forum", "social_media", "new_media"
    ]
    author: Optional[str]
    date: Optional[DateTime]
    url: Optional[str]

    def __repr__(self):
        return f"{self.title} by {self.author} on {self.date}"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "content_type": self.content_type,
            "content": self.content,
            "author": self.author,
            "date": self.date,
            "url": self.url,
        }


class Scraper(ABC):
    """
    Base class for a scraper.
    """

    content_type: Literal["text/html", "text/plain"] = "text/html"

    def __init__(
        self,
        index_url: str,
        category: str,
        content_type="text/html",
        num_proc=1,
        max_items: Optional[int] = None,
        headers=DEFAULT_HEADERS,
    ):
        self.index_url = index_url
        self.category = category
        self.num_proc = num_proc
        self.max_items = max_items
        self.content_type = content_type
        self.headers = headers

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
        article_indexes = (
            article_indexes[: self.max_items]
            if self.max_items is not None
            else article_indexes
        )

        # fetch the articles
        article_items = await asyncio.gather(
            *_limit_concurrency(
                [self.fetch_article(index) for index in article_indexes],
                concurrency=self.num_proc,
            )
        )

        # postprocess the article items
        articles = []

        for item in article_items:
            if item is not None:
                try:
                    article = self.parse_article(item)
                    articles.append(article)
                except Exception as e:
                    print(f"Error parsing article: {e}")

        return articles

    async def fetch_article(self, item: Any) -> Any:
        """
        Asynchronously fetches an article based on the given item.
        """
        return item

    def _parse_date(self, date: str) -> DateTime:
        """
        Parses a date string into a datetime object.

        Args:
          date (str): The date string to parse.

        Returns:
          datetime: The datetime object representing the date.
        """
        try:
            return dateparser.parse(date, settings={"TIMEZONE": "Asia/Hong_Kong"})
        except:
            return DateTime.now(tz=ZoneInfo("Asia/Hong_Kong"))

    def _parse_title(self, title: str) -> str:
        return text_processing(title)

    def _parse_content(self, text: str) -> str:
        return text.strip()

    def _parse_author(self, author: str) -> str:
        return text_processing(author)

    def _parse_url(self, url: str) -> str:
        return url.strip()

    def _parse_id(self, id: str) -> str:
        return id.strip()
