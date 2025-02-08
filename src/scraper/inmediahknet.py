from datetime import datetime as DateTime
import requests
from bs4 import BeautifulSoup
from telegram_scraper import TelegramScraper
from typing import TYPE_CHECKING
from utils import fetch_content, fetch_header_location

if TYPE_CHECKING:
    from bs4.element import Tag, ResultSet  # for type hinting


class InMediaHKNetTelegramScraper(TelegramScraper):
    def __init__(self):
        super().__init__(
            "https://t.me/s/inmediahknet",
        )

    def fetch_article(self, index: "ResultSet[Tag]") -> "ResultSet[Tag]":
        # get content in .text-content
        content = index.select_one(".text-content").text  # bit.ly url
        article_url = content.split("\n")[-1].strip()

    def _parse_url(self, url: str) -> str:
        return None

    def _parse_author(self, author: str) -> str:
        return None  # no author

    def _parse_date(self, date: str) -> DateTime:
        date = date.split("\n")[-1].strip()

        try:
            date = DateTime.strptime(date, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            date = DateTime.now()

    def _parse_title(self, title: str) -> str:
        title = title.split("\n")[0].strip()

        return title


if __name__ == "__main__":
    scraper = InMediaHKNetTelegramScraper()

    articles = asyncio.run(scraper.get_articles())

    print(articles)
