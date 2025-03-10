from datetime import datetime as DateTime
from scraper.utils import fetch_content
import json
from scraper.api_scraper import APIScraper


class ONCCScraper(APIScraper):
    base_url = "https://hk.on.cc"

    def __init__(self, **kwargs):
        date = DateTime.now().strftime("%Y%m%d")  # 20250310
        index_url = "https://hk.on.cc/hk/bkn/js/{}/news_dailyList.js".format(date)
        super().__init__(
            index_url=index_url,
            category="news",
            content_type="text/html",
            index_item_selector="items",
            item_id_selector="articleId",
            item_title_selector="title",
            item_content_selector="description",  # html content
            item_date_selector="pubDate",
            item_url_selector="link",
            item_author_selector="authorname",
            **kwargs,
        )

    async def parse_index(self):
        """
        Asynchronously parses the index page and extracts a list of URLs.
        """
        try:
            api_res_text = await fetch_content(self.index_url)
            # parse json
            api_res_json = json.loads(api_res_text.encode("utf-8").decode("utf-8-sig"))

            return api_res_json
        except Exception as e:
            print("Error", e)
            return []

    async def fetch_article(self, item: dict):
        # NOTE: Replace the content with the full article content
        item["description"] = await fetch_content(self.base_url + item["link"])

        return item

    def parse_article(self, item: dict) -> dict:
        # filter out non-article items
        if item["feedtype"] != "static":
            return None

        return super().parse_article(item)

    def _parse_url(self, url: str) -> str:
        return self.base_url + url


if __name__ == "__main__":
    import asyncio

    # Example usage
    scraper = ONCCScraper(
        num_proc=1,
    )

    articles = asyncio.run(scraper.get_articles())

    print(articles)
