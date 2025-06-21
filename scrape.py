import os
import asyncio
import logging
import datetime
from tqdm.auto import tqdm
import json
from typing import Dict, TYPE_CHECKING, List
import requests
from scraper.hk01 import HK01Scraper
from scraper.stheadline import HeadlineScraper
from scraper.rthk_zh import RTHKChineseScraper
from scraper.rthk_en import RTHKEnglishScraper
from scraper.oncc import ONCCScraper
from scraper.scmp import SCMPScraper
from scraper.govhk import GovHKScraper
from scraper.c881903 import C881903Scraper
from scraper.weekendhk import WeekendHKScraper
from scraper.hket import HKETScraper
from scraper.orangenews import OrangeNewsScraper
from scraper.rfa import RFACantoneseScraper
from scraper.tvbnews import TVBNewsScraper
from scraper.nownews import NowNewsScraper
from scraper.unwire import UnwireScraper
from scraper.mingpao import MingPaoScraper
from scraper.am730 import AM730Scraper
from scraper.ulifestyle import ULifestyleScraper
from scraper.scraper import ScraperOutput
from html_extractor.html_extractor import html_extract

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from scraper.scraper import Scraper

PIPELINE_ENDPOINT = os.getenv("PIPELINE_ENDPOINT")


def is_dict_over_1mb(data: dict) -> bool:
    json_str = json.dumps(data)
    size_bytes = len(json_str.encode("utf-8"))
    return (
        size_bytes > 990_000
    )  # 0.99 MB threshold, there a limit of 1 MB for Cloudflare Workers


def send_to_pipeline(article, pipeline_endpoint=PIPELINE_ENDPOINT):
    if not pipeline_endpoint:
        raise ValueError("PIPELINE_ENDPOINT is not set.")

    if is_dict_over_1mb(article):
        logger.warning("Article size exceeds 1MB, skipping sending to pipeline.")
        return

    headers = {"Content-Type": "application/json"}
    response = requests.post(
        pipeline_endpoint, json=article, headers=headers, timeout=60
    )

    if response.status_code != 200:
        raise requests.exceptions.HTTPError(
            f"Pipeline request failed with status code {response.status_code}: {response.text}"
        )

    return response.json()


def extract_content_from_html(articles: List[ScraperOutput]):
    """
    Extracts text content from HTML articles using the html_extract function.
    """
    extracted_articles = []

    for index, article in enumerate(articles):
        if isinstance(article.content, str):
            prev_index = index - 1 if index > 0 else len(articles) - 1
            prev_article = articles[prev_index]

            if prev_article is None:
                logger.warning(
                    f"No previous article found for index {index}. Skipping HTML extraction."
                )
                continue

            ref_content = (
                prev_article.content if isinstance(prev_article.content, str) else ""
            )

            if not ref_content:
                logger.warning(
                    f"No reference content found for the article at index {index}. Skipping HTML extraction."
                )
                continue

            # Extract text from HTML content
            extracted_article = article.to_dict().copy()
            extracted_article["extracted"] = html_extract(ref_content, article.content)
            extracted_article["date"] = (
                article.date.isoformat() + "Z" if article.date else None
            )
            extracted_articles.append(extracted_article)

    return extracted_articles


def main(num_proc=3):
    scrapers: Dict[str, Scraper] = {
        "881903": C881903Scraper(num_proc=num_proc),
        "RTHKChinese": RTHKChineseScraper(num_proc=num_proc),
        "RTHKEnglish": RTHKEnglishScraper(num_proc=num_proc),
        "HK01": HK01Scraper(num_proc=num_proc),
        # "InMediaHKNet": InMediaHKNetTelegramScraper(num_proc=num_proc), # Cloudflare blocked
        "Headline": HeadlineScraper(num_proc=num_proc),
        "GOVHK": GovHKScraper(num_proc=num_proc),
        "On.cc": ONCCScraper(num_proc=num_proc),
        "SCMP": SCMPScraper(num_proc=num_proc),
        "MingPao": MingPaoScraper(num_proc=num_proc),
        "hket": HKETScraper(num_proc=num_proc),
        "OrangeNews": OrangeNewsScraper(num_proc=num_proc),
        "RFACantonese": RFACantoneseScraper(num_proc=num_proc),
        "TVBNews": TVBNewsScraper(num_proc=num_proc),
        "NowNews": NowNewsScraper(num_proc=num_proc),
        "WeekendHK": WeekendHKScraper(num_proc=num_proc),
        "UnwireHK": UnwireScraper(num_proc=num_proc),
        "AM730": AM730Scraper(num_proc=num_proc),
        "ULifestyleScraper": ULifestyleScraper(num_proc=num_proc),
    }
    failed_scrapers = []
    now = datetime.datetime.now(datetime.timezone.utc)
    today = now.date()
    timestamp = now.isoformat() + "Z"

    for key in tqdm(scrapers.keys(), desc="Scraping"):
        scraper = scrapers[key]

        try:
            articles = asyncio.run(scraper.get_articles())

            if len(articles) == 0:
                logger.error(f"No articles found for {key}. Skipping...")
                failed_scrapers.append(key)
                continue

            # extract article content from HTML
            if scraper.content_type == "text/html":
                articles = extract_content_from_html(articles)

            # send to Cloudflare pipeline
            for article in articles:
                # only get article published in today
                if (
                    article["date"]
                    and datetime.datetime.fromisoformat(
                        article["date"].replace("Z", "")
                    ).date()
                    != today
                ):
                    logger.warning(
                        f"Article {article['title']} is not published today. Skipping..."
                    )
                    continue

                send_to_pipeline(
                    [
                        {
                            "event": "scraping",
                            "scraper": key,
                            "timestamp": timestamp,
                            "payload": article,
                        }
                    ],
                )

        except Exception as e:
            logger.error(f"Error scraping {key}: {e}")
            failed_scrapers.append(key)

    if failed_scrapers:
        raise RuntimeError(
            f"Failed to scrape the following scrapers: {', '.join(failed_scrapers)}"
        )


if __name__ == "__main__":
    main()
