from datetime import datetime as DateTime
import asyncio
from scraper.telegram_scraper import TelegramScraper


class RTHKChineseTelegramScraper(TelegramScraper):
    def __init__(self, **kwargs: dict) -> None:
        super().__init__(
            index_url="https://t.me/s/rthk_new_c",
            category="news",
            content_type="text/html",
            **kwargs
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
