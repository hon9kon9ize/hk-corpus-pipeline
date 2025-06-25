import re
from typing import TYPE_CHECKING
from datetime import datetime
from scraper.rss_scraper import RSSScraper

if TYPE_CHECKING:
    from scraper.scraper import ScraperOutput


class OrientalSundayScraper(RSSScraper):
    def __init__(self, **kwargs):
        super().__init__(
            index_url="https://www.orientalsunday.hk/feed/",
            category="news",
            content_type="text/html",
            **kwargs
        )


if __name__ == "__main__":
    import asyncio

    scraper = OrientalSundayScraper(num_proc=3)
    articles = asyncio.run(scraper.get_articles())

    print(articles)
