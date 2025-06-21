from datetime import datetime as DateTime
from typing import TYPE_CHECKING
from scraper.utils import fetch_content
from bs4 import BeautifulSoup
from scraper.html_scraper import HTMLScraper

if TYPE_CHECKING:
    from bs4.element import Tag, ResultSet  # for type hinting


class MingPaoScraper(HTMLScraper):
    def __init__(self, **kwargs: dict):
        super().__init__(
            index_url="https://news.mingpao.com/ins/%E5%8D%B3%E6%99%82%E6%96%B0%E8%81%9E/main",
            category="news",
            content_type="text/html",
            index_item_selector="#tabcontentnewslist2lat .contentwrapper",
            item_id_selector="meta[property='og:url'][content]",
            item_title_selector="meta[property='og:title'][content]",
            item_content_selector=None,  # raw html content
            item_date_selector=".date",  # 2025年6月20日星期五
            item_url_selector="meta[property='og:url'][content]",  # <meta property="og:url" content="???">
            item_author_selector="meta[property='article:author'][content]",
            **kwargs,
        )

    async def fetch_article(self, tag: "ResultSet[Tag]") -> "ResultSet[Tag]":
        # get html content in .tgme_widget_message_text
        href_tag = tag.select("h2 > a[href]")[1]

        if href_tag is None:
            return None

        article_url = href_tag["href"]

        if not article_url.startswith("http"):
            if article_url.startswith(".."):
                article_url = "https://news.mingpao.com" + article_url[2:]
            else:
                article_url = "https://news.mingpao.com" + article_url

        content = await fetch_content(
            article_url,
            headers={"User-Agent": self.user_agent, "Referer": self.index_url},
        )
        content_soup = BeautifulSoup(content, "html.parser")

        return content_soup

    def _parse_date(self, date: str) -> DateTime:
        # Handles date format like '2025年6月20日星期五'
        try:
            # Remove '星期' and the weekday for parsing
            import re

            date_clean = re.sub(r"星期.+$", "", date)
            date_obj = DateTime.strptime(date_clean.strip(), "%Y年%m月%d日")
        except Exception:
            date_obj = DateTime.now()

        return date_obj


if __name__ == "__main__":
    import asyncio

    scraper = MingPaoScraper()

    articles = asyncio.run(scraper.get_articles())

    print(articles)
