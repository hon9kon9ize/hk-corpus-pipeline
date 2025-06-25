import re
from typing import TYPE_CHECKING
from datetime import datetime
from scraper.rss_scraper import RSSScraper

if TYPE_CHECKING:
    from scraper.scraper import ScraperOutput


class MenClubScraper(RSSScraper):
    def __init__(self, **kwargs):
        super().__init__(
            index_url="https://www.menclub.hk/etc/rss.php",
            category="news",
            content_type="text/html",
            **kwargs
        )

    def parse_article(self, item: dict) -> "ScraperOutput":
        article = super().parse_article(item)

        # there no publish date in the RSS feed, we can find it in the content, eg: <span>POSTED ON 25 Jun 2025</span>
        content = article.content

        if content:
            # find the date in the content
            match = re.search(r"<span>POSTED ON (\d{1,2} \w+ \d{4})</span>", content)
            if match:
                date_str = match.group(1)
                try:
                    article.date = datetime.strptime(date_str, "%d %b %Y").isoformat()
                except ValueError:
                    pass

        return article


if __name__ == "__main__":
    import asyncio

    scraper = MenClubScraper(num_proc=3)
    articles = asyncio.run(scraper.get_articles())

    print(articles)
