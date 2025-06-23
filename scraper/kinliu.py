from datetime import datetime as DateTime
from typing import TYPE_CHECKING
from scraper.utils import fetch_content, fetch_json
from bs4 import BeautifulSoup
from scraper.html_scraper import HTMLScraper

if TYPE_CHECKING:
    from bs4.element import Tag, ResultSet  # for type hinting


class KinLiuScraper(HTMLScraper):
    def __init__(self, **kwargs: dict):
        super().__init__(
            index_url="https://n.kinliu.hk/wp-admin/admin-ajax.php?action=alm_query_posts&nonce=f408e7c304&query_type=standard&id=&post_id=924&slug=news&canonical_url=https%3A%2F%2Fn.kinliu.hk%2Fnews%2F&posts_per_page=10&page=1&offset=0&post_type%5B%5D=kinliuhknews&repeater=default&seo_start_page=1&preloaded=false&category=kinliuhknews&order=DESC&orderby=date&post__not_in=181275%2C181190",
            category="news",
            content_type="text/html",
            index_item_selector=".td-block-span6",
            item_id_selector="meta[property='og:url'][content]",
            item_title_selector="meta[property='og:title'][content]",
            item_content_selector=None,  # raw html content
            item_date_selector=".td-post-header .td-post-date time.entry-date",  # 2025年6月20日星期五
            item_url_selector=self.get_article_url,
            item_author_selector=None,
            **kwargs,
        )

    async def parse_index(self):
        """
        Asynchronously parses the index page and extracts a list of items.
        """
        try:
            item = await fetch_json(
                self.index_url,
                headers={"User-Agent": self.user_agent, "Referer": self.index_url},
            )
            index_soup = BeautifulSoup(item["html"], "html.parser")

            items = index_soup.select(self.index_item_selector)

            return items
        except Exception as e:
            print("Error", e)
            return []

    def get_article_url(self, item: "ResultSet[Tag]") -> str:
        href_tag = item.select_one(".entry-title > a")

        if href_tag is None:
            return None

        article_url = href_tag["href"]

        if not article_url.startswith("http"):
            if article_url.startswith(".."):
                article_url = "https://n.kinliu.hk" + article_url[2:]
            else:
                article_url = "https://n.kinliu.hk" + article_url

        return article_url

    async def fetch_article(self, tag: "ResultSet[Tag]") -> "ResultSet[Tag]":
        article_url = self.get_article_url(tag)

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

    scraper = KinLiuScraper(max_items=10)

    articles = asyncio.run(scraper.get_articles())

    print(articles)
