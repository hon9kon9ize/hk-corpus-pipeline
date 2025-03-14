from scraper.rss_scraper import RSSScraper


class RTHKChineseScraper(RSSScraper):
    def __init__(self, **kwargs):
        super().__init__(
            index_url="https://rthk9.rthk.hk/rthk/news/rss/c_expressnews_clocal.xml",
            category="news",
            content_type="text/html",
            **kwargs
        )


if __name__ == "__main__":
    import asyncio

    scraper = RTHKChineseScraper(num_proc=3)
    articles = asyncio.run(scraper.get_articles())

    print(articles[0].content)
