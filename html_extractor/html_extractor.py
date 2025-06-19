import difflib
from bs4 import BeautifulSoup


def load_and_clean_html(html_text: str) -> str:
    """
    Load HTML content and remove unwanted elements.

    This function parses HTML text and removes script tags, style tags,
    meta tags, navigation elements, link tags, and images to clean up the HTML.

    Args:
        html_text: Raw HTML content as a string

    Returns:
        A prettified string of the cleaned HTML
    """
    soup = BeautifulSoup(html_text, "html.parser")
    for tag in soup(["script", "style", "meta", "nav", "link", "img"]):
        tag.decompose()
    return soup.prettify()


def html_to_text(html_text: str) -> str:
    """
    Convert HTML to plain text.

    This function extracts all text content from HTML, separating
    elements with newlines and removing extra whitespace.

    Args:
        html_text: HTML content as a string

    Returns:
        Plain text extracted from the HTML
    """
    soup = BeautifulSoup(html_text, "html.parser")
    text = soup.get_text(separator="\n", strip=True)
    return text


def remove_consecutive_duplicates(lines):
    """
    Remove consecutive duplicate lines from a list of strings.

    This function iterates through a list of strings and removes
    consecutive duplicates, returning a new list with unique entries.

    Args:
        lines: List of strings

    Returns:
        A list with consecutive duplicates removed
    """
    if not lines:
        return []

    unique_lines = [lines[0]]
    for line in lines[1:]:
        if line != unique_lines[-1]:
            unique_lines.append(line)

    return unique_lines


def html_extract(ref_html, tgt_html):
    """
    Extract text differences between two HTML documents.

    This function compares two HTML documents and extracts the text
    content from lines that are present in the target HTML but not
    in the reference HTML (additions). It removes duplicates and
    returns the unique extracted text content.

    Args:
        ref_html: Reference HTML document as a string
        tgt_html: Target HTML document to compare against reference

    Returns:
        A string containing the extracted text differences, joined by newlines
    """
    ref_lines = load_and_clean_html(ref_html).splitlines()
    tgt_lines = load_and_clean_html(tgt_html).splitlines()
    lines = []
    d = difflib.unified_diff(ref_lines, tgt_lines, lineterm="")
    for line in d:
        if line.startswith("+") and not line.startswith("+++"):
            text = html_to_text(line.lstrip("+"))

            if len(text) > 0 and text not in lines:
                lines.append(text.strip())

    lines = remove_consecutive_duplicates(lines)

    return "\n".join(lines)
