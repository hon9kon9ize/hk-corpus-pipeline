from bs4 import BeautifulSoup
from utils import fetch_content
from typing import TYPE_CHECKING
from scraper import Scraper, ScraperOutput

if TYPE_CHECKING:
    from bs4.element import Tag, ResultSet  # for type hinting


class HTMLScraper(Scraper):
    """
    A scraper for HTML webpage.
    """

    def __init__(
        self,
        index_url: str,
        index_item_selector: str,
        item_id_selector: str,
        item_title_selector: str,
        item_content_selector: str,
        item_date_selector: str,
        item_url_selector: str | None = None,
        item_author_selector: str | None = None,
        num_proc=1,
    ):
        self.index_item_selector = index_item_selector
        self.item_id_selector = item_id_selector
        self.item_url_selector = item_url_selector
        self.item_title_selector = item_title_selector
        self.item_content_selector = item_content_selector
        self.item_date_selector = item_date_selector
        self.item_author_selector = item_author_selector

        super().__init__(index_url, num_proc)

    async def parse_index(self):
        try:
            index_page = await fetch_content(self.index_url)
            index_soup = BeautifulSoup(index_page, "html.parser")

            items = index_soup.select(self.index_item_selector)

            return items
        except Exception as e:
            print("Error", e)
            return []

    def _get_elem_text(self, index_item: "ResultSet[Tag]", selector: str) -> str:
        # if the selector has an attribute, e.g. "a[href]", return the attribute value
        if "[" in selector:
            selector, attr_name = selector.split("[")
            attr_name = attr_name[:-1]

            if selector.startswith("&"):  # the attribute is at top level
                return index_item[attr_name]

            return index_item.select_one(selector)[attr_name]

        return index_item.select_one(selector).text

    def parse_article(self, index_item: "ResultSet[Tag]") -> ScraperOutput:
        id = self._parse_id(self._get_elem_text(index_item, self.item_id_selector))
        title = self._parse_title(
            self._get_elem_text(index_item, self.item_title_selector)
        )
        content = self._parse_content(
            self._get_elem_text(index_item, self.item_content_selector)
        )
        date = self._parse_date(
            self._get_elem_text(index_item, self.item_date_selector)
        )
        author = (
            self._parse_author(
                self._get_elem_text(index_item, self.item_author_selector)
            )
            if self.item_author_selector
            else None
        )
        url = (
            self._parse_url(self._get_elem_text(index_item, self.item_url_selector))
            if self.item_url_selector
            else None
        )

        return ScraperOutput(id, title, content, author, date, url)
