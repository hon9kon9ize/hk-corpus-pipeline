from datetime import datetime as DateTime
from scraper.telegram_scraper import TelegramScraper
from scraper.scraper import ScraperOutput
from scraper.utils import fetch_content
from bs4 import BeautifulSoup


class SCMPScraper(TelegramScraper):
    """
    A scraper for South China Morning Post Telegram channel.
    """

    def __init__(self, **kwargs):
        super().__init__(
            index_url="https://t.me/s/scmpfeed",
            category="news",
            item_id_selector="meta[name='cXenseParse:articleid'][content]",
            item_title_selector="h1",
            item_content_selector=None,  # html content
            item_date_selector="meta[property='article:published_time'][content]",  # <meta property="article:published_time" content="???">
            item_url_selector="meta[property='og:url'][content]",  # <meta property="og:url" content="???">
            item_author_selector="meta[name='cXenseParse:author'][content]",
            **kwargs,
        )

    async def fetch_article(self, tag: "ResultSet[Tag]") -> "ResultSet[Tag]":
        # get html content in .tgme_widget_message_text
        href_tag = tag.select_one(".tgme_widget_message_text > a")

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

    scraper = SCMPScraper()

    articles = asyncio.run(scraper.get_articles())

    print(articles)
