from scraper.rss_scraper import RSSScraper


class WeekendHKScraper(RSSScraper):
    def __init__(self, **kwargs):
        super().__init__(
            index_url="https://www.weekendhk.com/feed",
            category="new_media",
            content_type="text/html",
            **kwargs
        )


if __name__ == "__main__":
    import asyncio

    scraper = WeekendHKScraper(num_proc=3)
    articles = asyncio.run(scraper.get_articles())

    print(articles)

    print(articles[0].content)
