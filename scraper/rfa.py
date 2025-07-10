from datetime import datetime as DateTime
from typing import TYPE_CHECKING
from scraper.utils import fetch_content
from scraper.telegram_scraper import TelegramScraper
from bs4 import BeautifulSoup

if TYPE_CHECKING:
    from bs4.element import Tag, ResultSet  # for type hinting


class RFACantoneseScraper(TelegramScraper):
    def __init__(self, **kwargs: dict):
        super().__init__(
            index_url="https://t.me/s/rfacantonese_news",
            category="news",
            content_type="text/html",
            item_id_selector="meta[property='og:url'][content]",
            item_title_selector="meta[property='og:title'][content]",
            item_content_selector=None,  # html content
            item_date_selector=".c-date.b-date[datetime]",  # 2025-06-18T10:53:48.095Z
            item_url_selector="meta[property='og:url'][content]",  # <meta property="og:url" content="???">
            item_author_selector=None,
            **kwargs,
        )

    def _parse_date(self, date: str) -> DateTime:
        try:
            date = DateTime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            date = DateTime.now()

        return date

    async def fetch_article(self, tag: "ResultSet[Tag]") -> "ResultSet[Tag]":
        href_tag = tag.select_one(
            ".tgme_widget_message_text > a[href^='https://ca.rfa.org']"
        )

        if href_tag is None:
            return None

        article_url = href_tag["href"]
        content = await fetch_content(article_url)
        content_soup = BeautifulSoup(content, "html.parser")

        return content_soup


if __name__ == "__main__":
    import asyncio

    scraper = RFACantoneseScraper()

    articles = asyncio.run(scraper.get_articles())

    print(articles)
