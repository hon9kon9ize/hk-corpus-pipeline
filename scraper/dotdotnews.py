from datetime import datetime as DateTime
from typing import TYPE_CHECKING
from scraper.utils import fetch_content
from bs4 import BeautifulSoup
import re
from scraper.html_scraper import HTMLScraper

if TYPE_CHECKING:
    from bs4.element import Tag, ResultSet  # for type hinting
    from scraper.scraper import ScraperOutput


class DotDotNewsScraper(HTMLScraper):
    def __init__(self, **kwargs: dict):
        super().__init__(
            index_url="https://www.dotdotnews.com/immed/more_1.html",
            category="news",
            content_type="text/html",
            index_item_selector=".columnList.item",
            item_id_selector="meta[property='og:url'][content]",
            item_title_selector="meta[property='og:title'][content]",
            item_content_selector=None,  # raw html content
            item_date_selector=None,  # <meta property="article:published_time" content="???">
            item_url_selector="meta[property='og:url'][content]",  # <meta property="og:url" content="???">
            item_author_selector="meta[name='publisher'][content]",
            **kwargs,
        )

    async def fetch_article(self, tag: "ResultSet[Tag]") -> "ResultSet[Tag]":
        href_tag = tag.select_one("h2 > a[href]")

        if href_tag is None:
            return None

        article_url = href_tag["href"]

        content = await fetch_content(
            article_url,
            headers={**self.headers, "Referer": self.index_url},
        )
        content_soup = BeautifulSoup(content, "html.parser")

        return content_soup

    def parse_article(self, tag: "ResultSet[Tag]") -> "ScraperOutput":
        article = super().parse_article(tag)

        # Extract date from the article content, "datePublished": "Wed Jun 25 19:29:33 HKT 2025"
        date_text = re.search(r'datePublished":\s*"([^"]+)"', str(tag))
        if date_text:
            date_str = date_text.group(1)
            try:
                # Remove timezone abbreviation (e.g., 'HKT') for compatibility
                date_str_clean = re.sub(r" [A-Z]{3} ", " ", date_str)
                date = DateTime.strptime(date_str_clean, "%a %b %d %H:%M:%S %Y")
                article.date = date
            except Exception:
                article.date = DateTime.now()
        else:
            article.date = DateTime.now()

        return article


if __name__ == "__main__":
    import asyncio

    scraper = DotDotNewsScraper(max_items=1)

    articles = asyncio.run(scraper.get_articles())

    print(articles)
