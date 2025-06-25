# Hong Kong Web Archive Pipeline

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

### News

- HK01 (API) - https://web-data.api.hk01.com/v2/feed/category/0?bucketId=00000
- ~~獨立媒體 (Telegram) - https://t.me/s/inmediahknet~~ Cloudflare blocked
- 星島頭條 (Web) - https://www.stheadline.com/
- 政府新聞處 (Web) - https://www.info.gov.hk/gia/general/ctoday.htm
- on.cc (API) - https://hk.on.cc
- South China Morning Post (Telegram) - https://t.me/s/scmpfeed
- 明報 (Web) - https://news.mingpao.com/
- 香港經濟日報 (RSS) - https://www.hket.com/
- 橙新聞 (API) - https://www.orangenews.hk/
- 自由亞洲電台 (API) - https://www.rfa.org/cantonese/
- TVB News (Web) - https://news.tvb.com/
- Now 新聞 (Web) - https://news.now.com/
- AM730 (API) - https://www.am730.com.hk/
- The Standard (Web) - https://www.thestandard.com.hk/

### New Media/Blogs/Radio/Social Media

- 新假期 (RSS) - https://www.weekendhk.com/
- unwire (RSS) - https://www.unwire.hk/
- ULifestyle (API) - https://www.ulifestyle.com.hk/
- Fortune Insight (API) - https://fortuneinsight.com/
- 堅料網 (RSS) - https://n.kinliu.hk/
- 經濟一週 (RSS) - https://www.edigest.hk/
- MenClub (RSS) - https://www.menclub.hk/
- 點新聞 (HTML) - https://www.dotdotnews.com/
- 881903 (API) - https://www.881903.com/news2/recent
- RTHK 新聞 (RSS) - https://news.rthk.hk/rthk/ch/
- RTHK News English(RSS) - https://news.rthk.hk/rthk/en/
- 新城電台 (Web) - https://www.metroradio.com.hk/

## How to Run

Fork this repository and add these secrets or environment variables to your repository:

- `PIPELINE_ENDPOINT` - Cloudflare pipeline endpoint

Then Github workflows will automatically run the pipeline and sending the data the Cloudflare R2 object storage as a sink.
