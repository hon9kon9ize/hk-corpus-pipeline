from datetime import datetime as DateTime
from typing import TYPE_CHECKING
from scraper.utils import fetch_content
from bs4 import BeautifulSoup
import re
from scraper.html_scraper import HTMLScraper

if TYPE_CHECKING:
    from bs4.element import Tag, ResultSet  # for type hinting
    from scraper.scraper import ScraperOutput


class MetroRadioScraper(HTMLScraper):
    def __init__(self, **kwargs: dict):
        super().__init__(
            index_url="https://www.metroradio.com.hk/news/",
            category="news",
            content_type="text/html",
            index_item_selector="#ContentPlaceHolder1_gvNews td > div",
            item_id_selector=self.get_article_url,
            item_title_selector="#ContentPlaceHolder1_IndividualNewsList_lblTitle_0",
            item_content_selector=None,  # raw html content
            item_date_selector="#ContentPlaceHolder1_IndividualNewsList_lblTime_0",  # 25/6/2025 16:43
            item_url_selector=self.get_article_url,
            item_author_selector=None,
            **kwargs,
        )

    def get_article_id(self, tag: "ResultSet[Tag]") -> str:
        # Extract the article ID from the article url
        article_url = self.get_article_url(tag)

        if article_url:
            match = re.search(r"NewsId=(\d+)", article_url)
            if match:
                return match.group(1)
        return None

    def get_article_url(self, tag: "ResultSet[Tag]") -> str:
        # Extract the article URL from the tag
        href_tag = tag.select_one("a[href]")
        if href_tag and "href" in href_tag.attrs:
            return "https://www.metroradio.com.hk/" + href_tag["href"]
        return None

    async def fetch_article(self, tag: "ResultSet[Tag]") -> "ResultSet[Tag]":
        # get html content in .tgme_widget_message_text
        href_tag = tag.select_one("a[href]")

        if href_tag is None:
            return None

        article_url = "https://www.metroradio.com.hk/" + href_tag["href"]

        content = await fetch_content(
            article_url,
            headers={"User-Agent": self.user_agent, "Referer": self.index_url},
        )
        content_soup = BeautifulSoup(content, "html.parser")

        return content_soup


if __name__ == "__main__":
    import asyncio

    scraper = MetroRadioScraper(max_items=2)

    articles = asyncio.run(scraper.get_articles())

    print(articles)
