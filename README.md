# Hong Kong Web Corpus Pipeline

[![.github/workflows/scrape.yml](https://github.com/hon9kon9ize/yue-corpus-pipeline/actions/workflows/scrape.yml/badge.svg)](https://github.com/hon9kon9ize/yue-corpus-pipeline/actions/workflows/scrape.yml)

The goal of this project is create a pipeline and tools for scraping and processing Hong Kong web data.

> **How this project works?**

This project uses Github Actions to run a pipeline that scrapes web data from various sources, processes the data, and then pushes the data to a repository.

> **What kind of data are we looking for?**

We're not only looking for text data in Cantonese, but also any Hong Kong related information in general. This includes news articles, social media posts, and other forms of text data.

> **What would this data be used for?**

The data collected will be used to create a corpus of web text data. This corpus can be used for various NLP tasks, such as training language models, sentiment analysis, and other text analysis tasks.

## Data Sources

This is not a comprehensive list of data sources, and we are open to suggestions for other sources of Cantonese text data.

### Encyclopedias

- Yue Wikipedia - https://zh-yue.wikipedia.org/wiki/%E9%A0%AD%E7%89%88
- English Wikipedia - https://en.wikipedia.org/wiki/Main_Page
- Chinese Wikipedia - https://zh.wikipedia.org/wiki/Wikipedia:%E9%A6%96%E9%A1%B5
- 香港網絡大典 - https://evchk.fandom.com/zh/wiki/%E9%A6%96%E9%A0%81

### News

- RTHK News(Telegram) - https://t.me/s/rthk_new_c
- HK01 (API) - https://web-data.api.hk01.com/v2/feed/category/0?bucketId=00000
- 獨立媒體 (Telegram) - https://t.me/s/inmediahknet
- 星島頭條 (Web) - https://www.stheadline.com/
- 政府新聞處 (Web) - https://www.info.gov.hk/gia/general/ctoday.htm
- on.cc (API) - https://hk.on.cc/hk/bkn/js/20250205/news_dailyList.js
- South China Morning Post (Telegram) - https://t.me/s/scmpfeed
- 明報 (Web) - https://news.mingpao.com/

### Blogs

- 就係媒體 - https://beinghongkong.com/Blog
- 新假期 - https://www.weekendhk.com/


## How to Run

Fork this repository and add these secrets or environment variables to your repository:

- `HF_TOKEN` - Hugging Face API token
- `HF_REPO_NAME` - Name of the repository to push the dataset to (e.g. `hon9kon9ize/yue-corpus`)

Then Github workflows will automatically run the pipeline and push the dataset to your repository.