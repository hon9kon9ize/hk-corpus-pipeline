from typing import TYPE_CHECKING
from scraper.rss_scraper import RSSScraper
import re

if TYPE_CHECKING:
    from bs4.element import Tag, ResultSet  # for type hinting


class GovHKScraper(RSSScraper):
    def __init__(self, **kwargs: dict):
        super().__init__(
            index_url="https://www.news.gov.hk/tc/common/html/topstories.rss.xml",
            category="news",
            content_type="text/html",
            **kwargs,
        )


if __name__ == "__main__":
    import asyncio

    scraper = GovHKScraper(max_items=5)
    articles = asyncio.run(scraper.get_articles())
    print(f"Scraped {len(articles)} articles")
    for article in articles:
        print(article.content)
