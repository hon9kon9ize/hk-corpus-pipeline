import os
import hashlib
import asyncio
import time
import pandas as pd
import tempfile
from tqdm.auto import tqdm
from typing import Dict, TYPE_CHECKING
import tenacity
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
import requests
from scraper.rthk_zh_telegram import RTHKChineseTelegramScraper
from scraper.inmediahknet import InMediaHKNetTelegramScraper
from scraper.hk01 import HK01Scraper
from scraper.stheadline import HeadlineScraper
from scraper.rthk_zh import RTHKChineseScraper
from scraper.rthk_en import RTHKEnglishScraper
from scraper.oncc import ONCCScraper
from scraper.scmp import SCMPScraper
from huggingface_hub import HfApi

if TYPE_CHECKING:
    from scraper.scraper import Scraper

REPO_NAME = os.getenv("HF_REPO_NAME")
HF_TOKEN = os.getenv("HF_TOKEN")

api = HfApi(token=HF_TOKEN)


def is_rate_limit_error(exception):
    return (
        isinstance(exception, requests.exceptions.HTTPError)
        and exception.response.status_code == 429
    )


@retry(
    retry=retry_if_exception_type((requests.exceptions.HTTPError, ConnectionError)),
    stop=stop_after_attempt(7),  # Maximum 7 attempts
    wait=wait_exponential(
        multiplier=1, min=32, max=128
    ),  # Start with 4s, double each time, max 60s
    before_sleep=lambda retry_state: print(
        f"Rate limited. Retry attempt {retry_state.attempt_number}. Waiting {retry_state.next_action.sleep} seconds..."
    ),
)
def upload_to_hf(local_path, path_in_repo, repo_id, repo_type="dataset", wait_time=5):
    # Add a wait time before each call, even on first attempt
    time.sleep(wait_time)

    return api.upload_file(
        path_or_fileobj=local_path,
        path_in_repo=path_in_repo,
        repo_id=repo_id,
        repo_type=repo_type,
    )


def main(num_proc=3):
    scrapers: Dict[str, Scraper] = {
        "InMediaHKNet": InMediaHKNetTelegramScraper(num_proc=num_proc),
        "RTHKChineseTelegram": RTHKChineseTelegramScraper(num_proc=num_proc),
        "RTHKChinese": RTHKChineseScraper(num_proc=num_proc),
        "RTHKEnglish": RTHKEnglishScraper(num_proc=num_proc),
        "HK01": HK01Scraper(num_proc=num_proc),
        "Headline": HeadlineScraper(num_proc=num_proc),
        "On.cc": ONCCScraper(num_proc=num_proc),
        "SCMP": SCMPScraper(num_proc=num_proc),
    }
    temp_dir = tempfile.TemporaryDirectory()

    for key in tqdm(scrapers.keys(), desc="Scraping"):
        scraper = scrapers[key]
        articles = asyncio.run(scraper.get_articles())

        for article in tqdm(articles, desc=f"Uploading {key}"):
            # Convert article to a DataFrame
            article_dict = article.to_dict()
            df = pd.DataFrame([article_dict])

            # md5 of the article id
            article_id = hashlib.md5(article.id.encode()).hexdigest()

            # Save DataFrame to a temporary CSV file
            temp_file_name = f"{article_id}.csv"
            temp_file_path = os.path.join(temp_dir.name, temp_file_name)
            df.to_csv(temp_file_path, index=False)

            # Upload the CSV file to Huggingface
            upload_to_hf(
                temp_file_path,
                f"articles/{key}/{article_id}.csv",
                REPO_NAME,
                "dataset",
            )

    temp_dir.cleanup()


if __name__ == "__main__":
    main()
