from datetime import datetime as DateTime
from typing import TYPE_CHECKING
from scraper.utils import fetch_content
from bs4 import BeautifulSoup
from scraper.html_scraper import HTMLScraper

if TYPE_CHECKING:
    from bs4.element import Tag, ResultSet  # for type hinting


class HeadlineScraper(HTMLScraper):
    def __init__(self, **kwargs: dict):
        super().__init__(
            index_url="https://stheadline.com/realtimenews/即時",
            category="news",
            content_type="text/html",
            index_item_selector=".news-block",
            item_id_selector="meta[property='og:url'][content]",
            item_title_selector="meta[property='og:title'][content]",
            item_content_selector=None,  # raw html content
            item_date_selector="meta[property='article:published_time'][content]",  # <meta property="article:published_time" content="???">
            item_url_selector="meta[property='og:url'][content]",  # <meta property="og:url" content="???">
            item_author_selector="meta[name='publisher'][content]",
            **kwargs,
        )

    async def fetch_article(self, tag: "ResultSet[Tag]") -> "ResultSet[Tag]":
        # get html content in .tgme_widget_message_text
        href_tag = tag.select_one(".news-detail > a")

        if href_tag is None:
            return None

        article_url = href_tag["href"]

        if not article_url.startswith("http"):
            article_url = "https://stheadline.com" + article_url

        content = await fetch_content(article_url)
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

    scraper = HeadlineScraper(max_items=1)

    articles = asyncio.run(scraper.get_articles())

    print(articles)
