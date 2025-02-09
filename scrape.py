import os
import hashlib
import asyncio
import pandas as pd
import tempfile
from tqdm.auto import tqdm
from typing import Dict, TYPE_CHECKING
from scraper.rthk_zh import RTHKChineseTelegramScraper
from scraper.inmediahknet import InMediaHKNetTelegramScraper
from scraper.hk01 import HK01Scraper
from scraper.stheadline import HeadlineScraper
from huggingface_hub import HfApi

if TYPE_CHECKING:
    from scraper.scraper import Scraper

REPO_NAME = os.getenv("HF_REPO_NAME")
HF_TOKEN = os.getenv("HF_TOKEN")

api = HfApi(token=HF_TOKEN)


def main(num_proc=3):
    scrapers: Dict[str, Scraper] = {
        "InMediaHKNet": InMediaHKNetTelegramScraper(num_proc=num_proc),
        "RTHKChinese": RTHKChineseTelegramScraper(num_proc=num_proc),
        "HK01": HK01Scraper(num_proc=num_proc),
        "Headline": HeadlineScraper(num_proc=num_proc),
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
            api.upload_file(
                path_or_fileobj=temp_file_path,
                path_in_repo=f"articles/{key}/{article_id}.csv",
                repo_id=REPO_NAME,
                repo_type="dataset",
            )

    temp_dir.cleanup()


if __name__ == "__main__":
    main()
