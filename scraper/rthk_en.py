from scraper.rss_scraper import RSSScraper


class RTHKEnglishScraper(RSSScraper):
    def __init__(self, **kwargs):
        super().__init__(
            index_url="https://rthk9.rthk.hk/rthk/news/rss/e_expressnews_elocal.xml",
            category="news",
            content_type="text/html",
            **kwargs
        )


if __name__ == "__main__":
    import asyncio

    scraper = RTHKEnglishScraper(num_proc=3)
    articles = asyncio.run(scraper.get_articles())

    print(articles)
