from datetime import datetime as DateTime
from typing import Union
from scraper.api_scraper import APIScraper


class HK01Scraper(APIScraper):
    def __init__(self, **kwargs):
        super().__init__(
            index_url="https://web-data.api.hk01.com/v2/feed/category/0?bucketId=00000",
            category="news",
            index_item_selector="items",
            item_id_selector="data.articleId",
            item_title_selector="data.title",
            item_content_selector="data.description",
            item_date_selector="data.publishTime",
            item_url_selector="data.canonicalUrl",
            item_author_selector="data.authors.0.publishName",
            **kwargs,
        )

    def _parse_date(self, date: int) -> DateTime:
        return DateTime.fromtimestamp(date)

    def parse_article(self, item: dict) -> dict:
        # filter out non-article items
        if item["data"]["type"] != "article":
            return None

        return super().parse_article(item)


if __name__ == "__main__":
    import asyncio

    # Example usage
    scraper = HK01Scraper(
        num_proc=1,
    )

    articles = asyncio.run(scraper.get_articles())

    print(articles)
