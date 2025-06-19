from datetime import datetime as DateTime
from scraper.utils import fetch_content
from scraper.api_scraper import APIScraper


class AM730Scraper(APIScraper):
    def __init__(self, **kwargs):
        super().__init__(
            index_url="https://www.am730.com.hk/%E5%8D%B3%E6%99%82%E6%96%B0%E8%81%9E",
            category="news",
            content_type="text/html",
            index_item_selector="data.data",
            item_id_selector="nid",
            item_title_selector="title",
            item_content_selector="content",  # html content
            item_date_selector="publishDate",
            item_url_selector=self.get_article_url,
            item_author_selector=None,
            fetch_index_method="POST",
            **kwargs,
        )

    def get_article_url(self, item: dict) -> str:
        return f"https://www.am730.com.hk/{item['url']}"

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
    scraper = AM730Scraper(
        num_proc=1,
    )

    articles = asyncio.run(scraper.get_articles())

    print(articles[0])
