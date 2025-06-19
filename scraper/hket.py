from scraper.rss_scraper import RSSScraper


class HKETScraper(RSSScraper):
    def __init__(self, **kwargs):
        super().__init__(
            index_url="https://www.hket.com/rss/hongkong",
            category="news",
            content_type="text/html",
            **kwargs
        )


if __name__ == "__main__":
    import asyncio

    scraper = HKETScraper(num_proc=3)
    articles = asyncio.run(scraper.get_articles())

    print(articles[0])
