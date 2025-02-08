from scraper.html_scraper import HTMLScraper


class TelegramScraper(HTMLScraper):
    """
    A scraper for Telegram channels.
    """

    def __init__(
        self,
        index_item_selector=".tgme_widget_message",
        item_id_selector="&[data-post]",
        item_title_selector=".tgme_widget_message_text",
        item_content_selector=".tgme_widget_message_text",
        item_date_selector=".tgme_widget_message_text",
        item_url_selector=None,
        item_author_selector=None,
        **kwargs
    ):
        super().__init__(
            index_item_selector,
            item_id_selector,
            item_title_selector,
            item_content_selector,
            item_date_selector,
            item_url_selector,
            item_author_selector,
            **kwargs,
        )
