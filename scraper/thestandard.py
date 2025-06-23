from datetime import datetime as DateTime
from scraper.utils import fetch_content
from scraper.api_scraper import APIScraper


class TheStandardScraper(APIScraper):
    def __init__(self, **kwargs):
        super().__init__(
            index_url="https://www.thestandard.com.hk/api/content?path=%2Fapi%2Fv1%2Fcat%2Fnews%2Farticle%3Fcursor%3DeyJ2YWx1ZSI6NDAsImZ1bGxMaXN0SWQiOiI3MDQzNmNhZmIyMDM1ZWFlZGNkZjZiZTg1ZTcyMjIyMiJ9",
            category="news",
            content_type="text/html",
            index_item_selector="data",
            item_id_selector="article_id",
            item_title_selector="title",
            item_content_selector="content",  # html content
            item_date_selector="publish_at",  # 1750663140
            item_url_selector=self.get_article_url,
            item_author_selector=None,
            **kwargs,
        )

    def get_article_url(self, item: dict) -> str:
        return f"https://www.thestandard.com.hk/{item['url']}"

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
    scraper = TheStandardScraper(
        num_proc=1,
    )

    articles = asyncio.run(scraper.get_articles())

    print(articles[0])
