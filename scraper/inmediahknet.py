from datetime import datetime as DateTime
from typing import TYPE_CHECKING
from scraper.utils import fetch_content
from scraper.telegram_scraper import TelegramScraper
from bs4 import BeautifulSoup

if TYPE_CHECKING:
    from bs4.element import Tag, ResultSet  # for type hinting


class InMediaHKNetTelegramScraper(TelegramScraper):
    def __init__(self, **kwargs: dict):
        super().__init__(
            index_url="https://t.me/s/inmediahknet",
            category="news",
            content_type="text/html",
            item_id_selector="meta[property='og:url'][content]",
            item_title_selector=".article-detail .title",
            item_content_selector=None,  # html content
            item_date_selector="meta[property='article:published_time'][content]",  # <meta property="article:published_time" content="???">
            item_url_selector="meta[property='og:url'][content]",  # <meta property="og:url" content="???">
            item_author_selector="a.author",
            **kwargs,
        )

    async def fetch_article(self, tag: "ResultSet[Tag]") -> "ResultSet[Tag]":
        # get html content in .tgme_widget_message_text
        href_tag = tag.select_one(
            ".tgme_widget_message_text > a[href^='https://bit.ly']"
        )

        if href_tag is None:
            return None

        article_url = href_tag["href"]
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

    scraper = InMediaHKNetTelegramScraper()

    articles = asyncio.run(scraper.get_articles())

    print(articles)
