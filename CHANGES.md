# CHANGES — MCPDocSearch (summary of edits)

Date: 2025-10-23

This file records the edits made during the "HF_TOKEN + throttling" work and related troubleshooting runs. Use this as a quick reference for what changed, why, and where to look.

## Summary
- Purpose: add conservative request throttling, HF token support, and safer HTML->Markdown preprocessing to improve crawling reliability and avoid 429 rate-limits.
- Status: implemented and tested locally. Note: HF will still rate-limit by IP; use HF_TOKEN + delay/concurrency or a different IP if you hit 429.

## Files added
- `IMPLEMENTATION_NOTES.md` — implementation details and rationale
- `/tmp/test-mcp-changes.sh` — local test script (created for debugging; not committed to repository root)
- `CHANGES.md` — this file

## Files modified (with short explanations)

1. `crawler_cli/config.py`
   - Added conservative defaults for crawling and authentication:
     - DEFAULT_CONCURRENCY = 1
     - DEFAULT_REQUEST_DELAY = 2
     - DEFAULT_BROWSER_TIMEOUT = 30
     - DEFAULT_BROWSER_ARGS = ["--disable-blink-features=AutomationControlled", "--no-sandbox"]
     - HF_TOKEN read from environment (HF_TOKEN || HF_API_KEY)
   - Rationale: safe default settings to reduce 429s and basic stealth flags for Playwright.

2. `crawler_cli/main.py`
   - Imported new config constants and `HF_TOKEN`.
   - Added CLI options:
     - `--concurrency` / `-c` (int)
     - `--request-delay` (float)
   - Wired concurrency and request-delay into `CrawlerRunConfig` using:
     - `semaphore_count=concurrency`
     - `mean_delay=request_delay`
   - Adjusted browser configuration code (kept minimal) and added comments noting header limitations.
   - Integrated `LinkRemovingMarkdownGenerator` selection and passed markdown strategy into run config.

3. `crawler_cli/crawler.py`
   - Added `request_delay` parameter to `run_crawl()` and applied an inter-page throttle loop to sleep when necessary (verbose messages printed when waiting).
   - Enhanced verbose output to display configured delays and concurrency.

4. `crawler_cli/markdown.py`
   - Iterated on HTML preprocessing to preserve inline anchor text and lists while removing obvious navigation (`<nav>`, nav-like `header`/`footer` only if nav-like classes/ids).
   - Final approach: minimal, conservative removal; do NOT strip `<a>` tags so the markdown generator can convert them to `[text](url)`.
   - Implemented flexible `LinkRemovingMarkdownGenerator.generate_markdown(*args, **kwargs)` that accepts different crawl4ai signatures and replaces input HTML with preprocessed HTML.

5. `bin/doc-search.py` (user wrapper)
   - Wrapper already present; ensured it exports `HF_TOKEN="$HF_API_KEY"` and PLAYWRIGHT_BROWSERS_PATH and activates the conda env before running the repo's `crawl.py`. (You previously edited this script during troubleshooting.)

6. Documentation updates
   - `IMPLEMENTATION_NOTES.md` added (deep-dive notes on the change and testing)
   - `QUICK_REFERENCE.md` updated with quick commands and flags (helpful summary)

## Tests performed (selected)
- Verified `HF_TOKEN` is read in the conda env: `python -c "from crawler_cli.config import HF_TOKEN; print(bool(HF_TOKEN))"`
- Ran short crawls against `https://example.com` to validate throttling and markdown generation.
- Re-ran full LLM course crawl multiple times; observed intermittent 429s depending on IP.
- Validated `BrowserConfig` and `CrawlerRunConfig` parameter signatures by introspection.

## Known issues / caveats
- HF rate-limits at the IP level; sending HF_TOKEN through BrowserConfig headers isn't sufficient in all cases. When HF returns 429 pages, the crawler correctly records the 429 page content. Mitigation strategies:
  - Ensure HF_TOKEN is exported in the exact environment used to launch the crawler (wrapper already exports HF_TOKEN from HF_API_KEY).
  - Use low concurrency (1) and request_delay >= 2s (increase to 5s if needed).
  - Use a different IP (VPN/proxy) if the IP is already blocklisted.

- `BrowserConfig.headers` and `extra_args` are limited in what they can change; crawl4ai/playwright may not accept arbitrary Authorization headers for browser page navigations. Cookie/session-based authentication or running from a different IP are practical workarounds.

## Rollback notes
- To revert changes, restore the original versions of the four modified files listed above from git. Example:

```bash
git checkout -- crawler_cli/config.py crawler_cli/main.py crawler_cli/crawler.py crawler_cli/markdown.py
```

## Quick reproduction (example command used during tests)

```bash
export HF_TOKEN="$HF_API_KEY"
export PLAYWRIGHT_BROWSERS_PATH="$HOME/Library/Caches/ms-playwright"
/Users/arturboronat/bin/doc-search.py \
  --crawl https://huggingface.co/learn/llm-course/ \
  --output "/path/to/llm-course.md" \
  --depth 3 \
  --include-pattern '*/learn/llm-course/chapter*' \
  --concurrency 1 \
  --request-delay 2.0 \
  --verbose
```

## TODO / follow-ups
- If repeated 429s persist: implement an adaptive backoff that detects 429 responses and exponentially backs off or pauses the crawl run.
- Investigate sending Authorization headers at the HTTP level (via crawl4ai extension or upstream change) or simulate an authenticated session via browser storage (cookies / storage state) where HF accepts it.
- Optionally add per-domain throttle configuration and domain-specific cookie handling.

## Contact / context
Edits performed by local debugging session on 2025-10-23. For details on the implementation rationale and test logs, see `IMPLEMENTATION_NOTES.md` and `QUICK_REFERENCE.md` in this repository.
