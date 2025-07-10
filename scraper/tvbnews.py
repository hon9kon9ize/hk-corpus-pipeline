from datetime import datetime as DateTime
from scraper.utils import fetch_content
from scraper.api_scraper import APIScraper


class TVBNewsScraper(APIScraper):
    def __init__(self, **kwargs):
        super().__init__(
            index_url="https://inews-api.tvb.com/news/entry/category?id=instant&mpmLimit=0&lang=tc&page=5&limit=10&frt=1750325085172&country=HK",
            category="news",
            content_type="text/html",
            index_item_selector="content",
            item_id_selector="id",
            item_title_selector="title",
            item_content_selector="content",  # html content
            item_date_selector="publish_datetime",  # 2025-06-17T11:30:30.000Z
            item_url_selector=self.get_article_url,
            item_author_selector=None,
            **kwargs,
        )

    def get_article_url(self, item: dict) -> str:
        return f"https://news.tvb.com/tc/{item['category'][0]['id']}/{item['id']}"

    def _parse_date(self, date):
        return (
            DateTime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ") if date else DateTime.now()
        )

    async def fetch_article(self, item: dict):
        article_url = self.get_article_url(item)

        # NOTE: Replace the content with the full article content
        item["content"] = await fetch_content(
            article_url,
            headers={**self.headers, "Referer": self.index_url},
        )

        return item


if __name__ == "__main__":
    import asyncio

    # Example usage
    scraper = TVBNewsScraper(
        num_proc=1,
    )

    articles = asyncio.run(scraper.get_articles())

    print(articles[0])
