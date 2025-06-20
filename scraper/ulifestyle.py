from datetime import datetime as DateTime
from typing import TYPE_CHECKING
from scraper.utils import fetch_content
from bs4 import BeautifulSoup
from scraper.html_scraper import HTMLScraper

if TYPE_CHECKING:
    from bs4.element import Tag, ResultSet  # for type hinting


class ULifestyleScraper(HTMLScraper):
    def __init__(self, **kwargs: dict):
        super().__init__(
            index_url="https://www.ulifestyle.com.hk/category/ul-personalise-list",
            category="new_media",
            content_type="text/html",
            index_item_selector="section#article .list__item",
            item_id_selector="meta[property='og:url'][content]",
            item_title_selector="meta[property='og:title'][content]",
            item_content_selector=None,  # raw html content
            item_date_selector="meta[property='article:published_time'][content]",  # 2025-06-17T13:50:00+0800
            item_url_selector="meta[property='og:url'][content]",
            item_author_selector="meta[property='article:author'][content]",
            **kwargs,
        )

    async def fetch_article(self, tag: "ResultSet[Tag]") -> "ResultSet[Tag]":
        # get html content in .tgme_widget_message_text
        href_tag = tag.select_one(".card > .card-body .card-title > a")

        if href_tag is None:
            return None

        article_url = href_tag["href"]

        content = await fetch_content(
            article_url,
            headers={"User-Agent": self.user_agent, "Referer": self.index_url},
        )
        content_soup = BeautifulSoup(content, "html.parser")

        return content_soup

    def _parse_date(self, date: str) -> DateTime:
        try:
            date = DateTime.strptime(date, "%Y-%m-%dT%H:%M:%S%z")
        except ValueError:
            date = DateTime.now()

        return date


if __name__ == "__main__":
    import asyncio

    scraper = ULifestyleScraper(max_items=2)

    articles = asyncio.run(scraper.get_articles())

    print(articles)
