from html_scraper import HTMLScraper


class TelegramScraper(HTMLScraper):
    """
    A scraper for Telegram channels.
    """

    def __init__(self, index_url: str, num_proc=1):
        super().__init__(
            index_url,
            ".tgme_widget_message",
            "&[data-post]",
            ".tgme_widget_message_text",
            ".tgme_widget_message_text",
            ".tgme_widget_message_text",
            ".tgme_widget_message_author",
            num_proc=num_proc,
        )
