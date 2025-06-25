import re
from scraper.utils import fetch_content
from typing import TYPE_CHECKING, Optional
from bs4 import BeautifulSoup
from scraper.scraper import Scraper, ScraperOutput

if TYPE_CHECKING:
    from bs4.element import Tag, ResultSet  # for type hinting


class HTMLScraper(Scraper):
    """
    A scraper for HTML webpage.
    """

    def __init__(
        self,
        index_item_selector: str,
        item_id_selector: str,
        item_title_selector: str,
        item_date_selector: Optional[str] = None,
        item_content_selector: Optional[str] = None,
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
            index_page_html = await fetch_content(
                self.index_url,
                headers={"User-Agent": self.user_agent, "Referer": self.index_url},
            )

            if callable(self.index_item_selector):
                # if the index_item_selector is a callable, call it with the index page content
                items = self.index_item_selector(index_page_html)
                if not isinstance(items, list):
                    raise ValueError("index_item_selector must return a list of items")
                return items

            index_soup = BeautifulSoup(index_page_html, "html.parser")

            items = index_soup.select(self.index_item_selector)

            return items
        except Exception as e:
            print("Error", e)
            return []

    def _get_elem_text(self, tag: "ResultSet[Tag]", selector: str) -> str:
        if callable(selector):
            # if the selector is a callable, call it with the tag
            return selector(tag)

        # if the selector has an attribute, e.g. "a[href]", return the attribute value
        if selector.endswith("]"):
            attr_name_match = re.match(r"^.+(\[[^=]+\])$", selector)
            if attr_name_match:
                attr_name = attr_name_match.group(1)[1:-1]
            else:
                attr_name = ""

            if selector.startswith("&"):  # the attribute is at top level
                if attr_name not in tag.attrs:
                    return None
                return tag[attr_name]
            selector = selector.replace(f"[{attr_name}]", "")
            elem_tag = tag.select_one(selector)

            if elem_tag is None or attr_name not in elem_tag.attrs:
                return None

            return elem_tag[attr_name]

        elem_tag = tag.select_one(selector)

        if elem_tag is None:
            return None

        return elem_tag.text

    def parse_article(self, tag: "ResultSet[Tag]") -> ScraperOutput:
        """
        Parses an article from the given index item.

        Args:
            tag (ResultSet[Tag]): The index item containing the HTML elements to be parsed.

        Returns:
            ScraperOutput: An object containing the parsed article details including id, title, content, author, date, and url.
        """
        id_value = self._get_elem_text(tag, self.item_id_selector)
        title_value = self._get_elem_text(tag, self.item_title_selector)
        content_value = (
            self._get_elem_text(tag, self.item_content_selector)
            if self.item_content_selector is not None
            else str(tag.html)
        )

        date_value = (
            self._get_elem_text(tag, self.item_date_selector)
            if self.item_date_selector
            else None
        )

        author_value = (
            self._get_elem_text(tag, self.item_author_selector)
            if self.item_author_selector
            else None
        )

        url_value = (
            self._get_elem_text(tag, self.item_url_selector)
            if self.item_url_selector
            else None
        )

        if id_value is None or title_value is None or content_value is None:
            return None

        article_id = self._parse_id(id_value)
        title = self._parse_title(title_value)
        content = self._parse_content(content_value)
        date = self._parse_date(date_value)
        author = (
            self._parse_author(author_value)
            if self.item_author_selector and author_value is not None
            else None
        )
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
