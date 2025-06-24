from scraper.rss_scraper import RSSScraper


class EdigestHKScraper(RSSScraper):
    def __init__(self, **kwargs):
        super().__init__(
            index_url="https://www.edigest.hk/feed/",
            category="news",
            content_type="text/html",
            **kwargs
        )


if __name__ == "__main__":
    import asyncio

    scraper = EdigestHKScraper(max_items=2)
    articles = asyncio.run(scraper.get_articles())

    print(articles)
