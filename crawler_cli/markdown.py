from bs4 import BeautifulSoup
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator


# --- HTML Link Removal Logic ---
def remove_links(html):
    """Minimally process HTML: only remove explicit nav/header/footer tags that are clearly navigation.
    Preserve all content anchors and text so markdown generator gets complete information."""
    soup = BeautifulSoup(html, "html.parser")

    nav_indicators = ["nav", "navbar", "navigation", "sidebar", "toc", "breadcrumb", "menu"]
    
    # Remove explicit <nav> tags (these are always navigation)
    for element in soup.find_all(["nav"]):
        element.decompose()
    
    # Remove <header> and <footer> tags ONLY if they have nav-like class/id
    for tag in ["header", "footer"]:
        for element in soup.find_all(tag):
            cls = " ".join(element.get("class", [])).lower() if element.get("class") else ""
            idv = (element.get("id") or "").lower()
            # Only remove if has nav-indicator in class or id
            if any(ind in cls or ind in idv for ind in nav_indicators):
                element.decompose()

    # Remove empty list items only
    for li in soup.find_all("li"):
        if not li.get_text(strip=True):
            li.decompose()

    # IMPORTANT: Do NOT remove or modify anchor tags (<a> elements)
    # The markdown generator will convert them to [text](url) format
    # Removing them here loses all the link text and URLs

    return str(soup)


class LinkRemovingMarkdownGenerator(DefaultMarkdownGenerator):
    """Custom markdown generator that removes links and nav elements before processing"""

    # Keep signature flexible for compatibility with different crawl4ai versions
    def generate_markdown(self, *args, **kwargs):
        # Determine the HTML argument (support both `cleaned_html` positional and `input_html`/`cleaned_html` kw)
        cleaned_html = None
        if len(args) >= 1:
            cleaned_html = args[0]
        elif 'cleaned_html' in kwargs:
            cleaned_html = kwargs.get('cleaned_html')
        elif 'input_html' in kwargs:
            cleaned_html = kwargs.get('input_html')

        if cleaned_html is None:
            # Nothing to process, call parent directly
            return super().generate_markdown(*args, **kwargs)

        # Pre-process the HTML to remove nav wrappers but preserve link elements
        processed_html = remove_links(cleaned_html)

        # Convert relative hrefs to absolute if base_url is provided
        base_url = kwargs.get('base_url') or kwargs.get('base_url', None)
        if base_url:
            try:
                from urllib.parse import urljoin
                from bs4 import BeautifulSoup as _BS
                _soup = _BS(processed_html, 'html.parser')
                for a in _soup.find_all('a', href=True):
                    a['href'] = urljoin(base_url, a['href'])
                processed_html = str(_soup)
            except Exception:
                # non-fatal; leave processed_html unchanged
                pass

        # Replace the input in args/kwargs with processed HTML: prefer keyword replacement
        if 'cleaned_html' in kwargs:
            kwargs['cleaned_html'] = processed_html
        elif 'input_html' in kwargs:
            kwargs['input_html'] = processed_html
        else:
            # Replace first positional argument
            new_args = list(args)
            new_args[0] = processed_html
            args = tuple(new_args)

        # Call the parent implementation with the modified HTML
        return super().generate_markdown(*args, **kwargs)
