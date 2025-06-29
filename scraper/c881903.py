from datetime import datetime as DateTime
from scraper.utils import fetch_content
from scraper.api_scraper import APIScraper


class C881903Scraper(APIScraper):
    def __init__(self, **kwargs):
        super().__init__(
            index_url="https://www.881903.com/api/news/section/morelist?limit=11",
            category="news",
            content_type="text/html",
            index_item_selector="response.content",
            item_id_selector="item_id",
            item_title_selector="title",
            item_content_selector="content",  # html content
            item_date_selector="display_date",  # 2025-06-18
            item_url_selector=self.get_article_url,
            item_author_selector=None,
            **kwargs,
        )

    def get_article_url(self, item: dict) -> str:
        return f"https://www.881903.com/news/{item['article_column']['uri_code']}/{item['item_id']}"

    def _parse_date(self, date):
        return DateTime.strptime(date, "%Y-%m-%d") if date else DateTime.now()

    async def fetch_article(self, item: dict):
        article_url = self.get_article_url(item)

        # NOTE: Replace the content with the full article content
        item["content"] = await fetch_content(
            article_url,
            headers={"User-Agent": self.user_agent, "Referer": self.index_url},
        )

        return item


if __name__ == "__main__":
    import asyncio

    # Example usage
    scraper = C881903Scraper(
        num_proc=1,
        max_items=1,  # Limit to 1 item for testing
    )

    articles = asyncio.run(scraper.get_articles())

    print(articles[0])
