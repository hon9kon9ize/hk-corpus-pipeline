from scraper.utils import fetch_json
from typing import TYPE_CHECKING, Optional
from scraper.scraper import Scraper, ScraperOutput

if TYPE_CHECKING:
    from bs4.element import Tag, ResultSet  # for type hinting


class APIScraper(Scraper):
    """
    A scraper for HTML webpage.
    """

    def __init__(
        self,
        index_item_selector: str,
        item_id_selector: str,
        item_title_selector: str,
        item_content_selector: str,
        item_date_selector: str,
        item_url_selector: Optional[str] = None,
        item_author_selector: Optional[str] = None,
        **kwargs,
    ):
        self.index_item_selector = index_item_selector
        self.item_id_selector = item_id_selector
        self.item_url_selector = item_url_selector
        self.item_title_selector = item_title_selector
        self.item_content_selector = item_content_selector
        self.item_date_selector = item_date_selector
        self.item_author_selector = item_author_selector

        super().__init__(**kwargs)

    async def parse_index(self):
        """
        Asynchronously parses the index page and extracts a list of URLs.
        """
        try:
            api_res = await fetch_json(self.index_url)
            list_items = self._get_value(api_res, self.index_item_selector)

            return list_items
        except Exception as e:
            print("Error", e)
            return []

    def _get_value(self, item: dict, selector: str) -> str:
        # selector is dot annotated path to the value
        keys = selector.split(".")
        value = item
        for key in keys:
            if key.isdigit() and isinstance(value, list):
                key = int(key)
                if key < len(value):
                    value = value[key]
                else:
                    return None
            else:
                if key in value:
                    value = value[key]
                else:
                    return None

        return value

    def parse_article(self, item: dict) -> ScraperOutput:
        """
        Parses an article from the given index item.

        Args:
            tag (ResultSet[Tag]): The index item containing the item object to parse.

        Returns:
            ScraperOutput: An object containing the parsed article details including id, title, content, author, date, and url.
        """
        id_value = self._get_value(item, self.item_id_selector)
        title_value = self._get_value(item, self.item_title_selector)
        content_value = self._get_value(item, self.item_content_selector)
        date_value = self._get_value(item, self.item_date_selector)
        author_value = (
            self._get_value(item, self.item_author_selector)
            if self.item_author_selector
            else None
        )
        url_value = (
            self._get_value(item, self.item_url_selector)
            if self.item_url_selector
            else None
        )

        if id_value is None or title_value is None or content_value is None:
            return None

        article_id = self._parse_id(str(id_value))
        title = self._parse_title(title_value)
        content = self._parse_content(content_value)
        date = self._parse_date(date_value)
        author = self._parse_author(author_value) if self.item_author_selector else None
        url = self._parse_url(url_value) if self.item_url_selector else None

        return ScraperOutput(
            article_id,
            title,
            category=self.category,
            content_type=self.content_type,
            content=content,
            author=author,
            date=date,
            url=url,
        )
