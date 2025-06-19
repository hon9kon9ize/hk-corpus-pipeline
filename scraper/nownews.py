from datetime import datetime as DateTime
from scraper.utils import fetch_content
from scraper.api_scraper import APIScraper


class NowNewsScraper(APIScraper):
    def __init__(self, **kwargs):
        super().__init__(
            index_url="https://d3sli7vh0lsda4.cloudfront.net/api/getNewsList?category=119&pageNo=1&pageSize=20",
            category="news",
            content_type="text/html",
            index_item_selector=None,  # root level
            item_id_selector="newsId",
            item_title_selector="title",
            item_content_selector="content",  # html content
            item_date_selector="publishDate",  # 1750321286000
            item_url_selector=self.get_article_url,
            item_author_selector=None,
            **kwargs,
        )

    def get_article_url(self, item: dict) -> str:
        return f"https://news.now.com/home/local/player?newsId={item['newsId']}"

    def _parse_date(self, date):
        return DateTime.fromtimestamp(date / 1000) if date else DateTime.now()

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
    scraper = NowNewsScraper(
        num_proc=1,
    )

    articles = asyncio.run(scraper.get_articles())

    print(articles[0])
