from datetime import datetime as DateTime
from scraper.utils import fetch_content
from scraper.api_scraper import APIScraper


class FortuneInsightScraper(APIScraper):
    def __init__(self, **kwargs):
        super().__init__(
            index_url="https://fortuneinsight.com/web/wp-json/wp/v2/instant-news-lists",
            category="news",
            content_type="text/html",
            index_item_selector="&",
            item_id_selector="id",
            item_title_selector="title.rendered",  # html title
            item_content_selector="content",  # html content
            item_date_selector="date",  # 2025-06-13 08:44:00
            item_url_selector="url",
            item_author_selector=None,
            **kwargs,
        )

    async def fetch_article(self, item: dict):
        article_url = item["url"]

        # NOTE: Replace the content with the full article content
        item["content"] = await fetch_content(
            article_url,
            headers={**self.headers, "Referer": self.index_url},
        )

        return item


if __name__ == "__main__":
    import asyncio

    # Example usage
    scraper = FortuneInsightScraper(
        num_proc=1,
    )

    articles = asyncio.run(scraper.get_articles())

    print(articles[0])
