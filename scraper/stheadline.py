from datetime import datetime as DateTime
from typing import TYPE_CHECKING
from scraper.utils import fetch_content
from bs4 import BeautifulSoup
from scraper.html_scraper import HTMLScraper

if TYPE_CHECKING:
    from bs4.element import Tag, ResultSet  # for type hinting


class HeadlineScraper(HTMLScraper):
    def __init__(self, item_detail_selector: str, **kwargs: dict):
        super().__init__(
            index_item_selector="#article-list .news-block",
            item_id_selector="meta[property='og:url'][content]",
            item_title_selector="meta[property='og:title'][content]",
            item_content_selector=None,  # raw html content
            item_date_selector="meta[property='article:published_time'][content]",  # <meta property="article:published_time" content="???">
            item_url_selector="meta[property='og:url'][content]",  # <meta property="og:url" content="???">
            item_author_selector="meta[name='publisher'][content]",
            **kwargs,
        )
        self.item_detail_selector = item_detail_selector

    async def fetch_article(self, tag: "ResultSet[Tag]") -> "ResultSet[Tag]":
        href_tag = tag.select_one(f"{self.item_detail_selector} > a")

        if href_tag is None:
            return None

        article_url = href_tag["href"]

        if not article_url.startswith("http"):
            article_url = "https://stheadline.com" + article_url

        content = await fetch_content(
            article_url,
            headers={**self.headers, "Referer": self.index_url},
        )
        content_soup = BeautifulSoup(content, "html.parser")

        return content_soup

    def _parse_date(self, date: str) -> DateTime:
        try:
            date = DateTime.strptime(date, "%Y-%m-%dT%H:%M:%S%z")
        except ValueError:
            date = DateTime.now()

        return date


class HeadlineNewsScraper(HeadlineScraper):
    def __init__(self, **kwargs: dict):
        super().__init__(
            item_detail_selector=".news-detail",
            index_url="https://stheadline.com/realtimenews/新聞",
            category="news",
            content_type="text/html",
            **kwargs,
        )


class HeadlineColumnsScraper(HeadlineScraper):
    def __init__(self, **kwargs: dict):
        super().__init__(
            item_detail_selector=".column-info",
            index_url="https://www.stheadline.com/columnists/latest/%E6%9C%80%E6%96%B0",
            category="columns",
            content_type="text/html",
            **kwargs,
        )


if __name__ == "__main__":
    import asyncio

    scraper = HeadlineColumnsScraper(max_items=10)
    articles = asyncio.run(scraper.get_articles())

    print(articles)
