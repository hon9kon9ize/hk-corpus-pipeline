from scraper.rss_scraper import RSSScraper


class UnwireScraper(RSSScraper):
    def __init__(self, **kwargs):
        super().__init__(
            index_url="https://feeds.feedburner.com/unwirelife/",
            category="new_media",
            content_type="text/html",
            **kwargs
        )


if __name__ == "__main__":
    import asyncio

    scraper = UnwireScraper(num_proc=3)
    articles = asyncio.run(scraper.get_articles())

    print(articles)

    print(articles[0].content)
