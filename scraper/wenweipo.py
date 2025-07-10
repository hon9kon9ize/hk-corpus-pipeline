from datetime import datetime as DateTime
from typing import TYPE_CHECKING
from scraper.utils import fetch_content
from bs4 import BeautifulSoup
from scraper.html_scraper import HTMLScraper

if TYPE_CHECKING:
    from bs4.element import Tag, ResultSet  # for type hinting


class WenWeiPoScraper(HTMLScraper):
    def __init__(self, **kwargs: dict):
        super().__init__(
            index_url="https://www.wenweipo.com/todaywenwei/whnews/more_1.html",
            category="news",
            content_type="text/html",
            index_item_selector=".content-story-list .story-item",
            item_id_selector="meta[property='og:url'][content]",
            item_title_selector="meta[property='og:title'][content]",
            item_content_selector=None,  # raw html content
            item_date_selector="time.publish-date",  # 2025-07-04 04:30:53
            item_url_selector="meta[property='og:url'][content]",
            item_author_selector="meta[property='article:author'][content]",
            **kwargs,
        )

    async def fetch_article(self, tag: "ResultSet[Tag]") -> "ResultSet[Tag]":
        href_tag = tag.select_one(".story-item-text > a")

        if href_tag is None:
            return None

        article_url = href_tag["href"]

        content = await fetch_content(
            article_url,
            headers={**self.headers, "Referer": self.index_url},
        )
        content_soup = BeautifulSoup(content, "html.parser")

        return content_soup

    def _parse_date(self, date: str) -> DateTime:
        try:
            date = DateTime.strptime(date, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            date = DateTime.now()

        return date


if __name__ == "__main__":
    import asyncio

    scraper = WenWeiPoScraper(max_items=1)

    articles = asyncio.run(scraper.get_articles())

    print(articles)
