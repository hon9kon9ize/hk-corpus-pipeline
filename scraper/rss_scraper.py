from scraper.utils import fetch_content
from typing import Dict, Any
import feedparser
from scraper.scraper import Scraper, ScraperOutput


class RSSScraper(Scraper):
    """
    A scraper for HTML webpage.
    """

    def __init__(
        self,
        **kwargs,
    ):
        self.index_item_selector = None
        self.item_id_selector = "id"
        self.item_url_selector = "link"
        self.item_title_selector = "title"
        self.item_content_selector = "content"
        self.item_date_selector = "published"
        self.item_author_selector = None

        super().__init__(**kwargs)

    async def parse_index(self):
        """
        Asynchronously parses the index page and extracts a list of URLs.
        """
        try:
            d = feedparser.parse(
                self.index_url, agent=self.user_agent, referrer=self.index_url
            )
            return d.entries
        except Exception as e:
            print("Error", e)
            return []

    async def fetch_article(self, item: Dict[str, Any]):
        """
        Fetches the full article content from the given URL.

        Args:
            item (Dict[str, Any]): The index item to fetch.

        Returns:
            Dict[str, Any]: The index item with the full article content.
        """
        item["content"] = await fetch_content(
            item["link"],
            headers={**self.headers, "Referer": self.index_url},
        )

        return item

    def parse_article(self, item: Dict[str, Any]) -> ScraperOutput:
        """
        Parses an article from the given index item.

        Args:
            item (Dict[str, Any]): The index item to parse.

        Returns:
            ScraperOutput: An object containing the parsed article details including id, title, content, author, date, and url.
        """

        id_value = item.get(self.item_id_selector, "")
        title_value = item.get(self.item_title_selector, "")
        content_value = item.get(self.item_content_selector, "")
        date_value = item.get(self.item_date_selector, "")
        author_value = (
            item.get(self.item_author_selector, "")
            if self.item_author_selector
            else None
        )
        url_value = item.get(self.item_url_selector, "")

        if id_value is None or title_value is None or content_value is None:
            return None

        article_id = self._parse_id(id_value)
        title = self._parse_title(title_value)
        content = self._parse_content(content_value)
        date = self._parse_date(date_value)
        author = self._parse_author(author_value) if self.item_author_selector else None
        url = self._parse_url(url_value) if self.item_url_selector else None

        return ScraperOutput(
            article_id,
            title,
            category=self.category,
            content_type=self.content_type,
            content=content,
            author=author,
            date=date,
            url=url,
        )


if __name__ == "__main__":
    import asyncio

    scraper = RSSScraper(
        index_url="https://rthk9.rthk.hk/rthk/news/rss/e_expressnews_elocal.xml",
        category="news",
        num_proc=3,
    )
    articles = asyncio.run(scraper.get_articles())

    print(articles)
