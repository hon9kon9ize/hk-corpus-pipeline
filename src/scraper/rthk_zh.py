from datetime import datetime as DateTime
import asyncio
from telegram_scraper import TelegramScraper


class RTHKChineseTelegramScraper(TelegramScraper):
    def __init__(self):
        super().__init__(
            "https://t.me/s/rthk_new_c",
        )

    def _parse_url(self, url: str) -> str:
        return None  # no url

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
    scraper = RTHKChineseTelegramScraper()

    articles = asyncio.run(scraper.get_articles())

    print(articles)
