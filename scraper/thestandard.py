from datetime import datetime as DateTime
import re
from scraper.utils import fetch_content
from scraper.api_scraper import APIScraper


class TheStandardScraper(APIScraper):
    def __init__(self, **kwargs):
        super().__init__(
            index_url="https://www.thestandard.com.hk/api/content?path=%2Fapi%2Fv1%2Fcat%2Fnews%2Farticle%3Fcursor%3D{cursor}",
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

    async def parse_index(self):
        raw_html = await fetch_content(
            "https://www.thestandard.com.hk/news",
            headers={"User-Agent": self.user_agent, "Referer": self.index_url},
        )
        # find the cursor from the raw HTML, example: cursor=eyJ2YWx1ZSI6MjAsImZ1bGxMaXN0SWQiOiI5OTRjZTkzN2RmNWMyMTBmZWFkMGYwNWJhNDVjNWU1YiJ9
        cursor_match = re.search(r'cursor=([^"]+)\\"', raw_html)
        if cursor_match:
            cursor = cursor_match.group(1)
            self.index_url = self.index_url.format(cursor=cursor)

        return await super().parse_index()

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
    scraper = TheStandardScraper()

    articles = asyncio.run(scraper.get_articles())

    print(articles[0])
