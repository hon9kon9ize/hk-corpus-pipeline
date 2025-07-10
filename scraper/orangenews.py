from datetime import datetime as DateTime
from scraper.utils import fetch_content
from scraper.api_scraper import APIScraper


class OrangeNewsScraper(APIScraper):
    def __init__(self, **kwargs):
        super().__init__(
            index_url="https://apps.orangenews.hk/app/bus/channel/common/get_channel_data",
            category="news",
            content_type="text/html",
            index_item_selector="data.records",
            item_id_selector="contentId",
            item_title_selector="title",
            item_content_selector="content",  # html content
            item_date_selector="releaseDate",  # 2025-06-18 23:31:17
            item_url_selector="detailsUrl",
            item_author_selector="authorUserId",
            fetch_index_method="POST",
            fetch_index_content_type="application/x-www-form-urlencoded;charset=UTF-8",
            fetch_index_body="limit=12&handlerName=contentPageListHandler&params=%7B%22channelId%22%3A%2295%22%2C%22channelType%22%3A%223%22%2C%22isPc%22%3A%221%22%7D&page=1",
            **kwargs,
        )

    def _parse_date(self, date):
        return DateTime.strptime(date, "%Y-%m-%d %H:%M:%S") if date else None

    async def fetch_article(self, item: dict):
        # NOTE: Replace the content with the full article content
        item["content"] = await fetch_content(
            item["detailsUrl"],
            headers={**self.headers, "Referer": self.index_url},
        )

        return item


if __name__ == "__main__":
    import asyncio

    # Example usage
    scraper = OrangeNewsScraper(
        num_proc=1,
    )

    articles = asyncio.run(scraper.get_articles())

    print(articles[0])
