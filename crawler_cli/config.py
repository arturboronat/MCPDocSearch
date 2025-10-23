import os
from crawl4ai import CacheMode

# --- Default Configuration Values ---
DEFAULT_INCLUDE_PATTERNS = [
    "*doc*",
    "*docs*",
    "*tutorial*",
    "*guide*",
    "*quickstart*",
    "*introduction*",
    "*getting started*",
    "*installation*",
    "*setup*",
    "*manual*",
    "*faq*",
]
DEFAULT_EXCLUDE_PATTERNS = ["*#*"]
DEFAULT_CONTENT_TYPES = ["text/html"]
DEFAULT_KEYWORDS = [
    "docs",
    "documentation",
    "doc",
    "guide",
    "tutorial",
    "example",
    "quickstart",
    "introduction",
    "getting started",
    "installation",
    "setup",
    "manual",
    "faq",
]
DEFAULT_KEYWORD_WEIGHT = 0.7
DEFAULT_OUTPUT_TITLE = "# Crawled Documentation"
DEFAULT_MAX_DEPTH = 1
DEFAULT_CACHE_MODE = CacheMode.BYPASS

# --- Request Throttling & Authentication Defaults ---
# Conservative defaults to avoid 429 rate-limiting and respect server resources
DEFAULT_CONCURRENCY = 1  # Single concurrent request
DEFAULT_REQUEST_DELAY = 2  # 2 second delay between requests
DEFAULT_BROWSER_TIMEOUT = 30  # seconds
DEFAULT_BROWSER_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--no-sandbox",
]

# --- Hugging Face Authentication ---
# Attempt to read HF_TOKEN from environment; used for authenticated requests
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("HF_API_KEY")
