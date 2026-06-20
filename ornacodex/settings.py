"""Scrapy settings for the ornacodex project.

Most of these are plain Scrapy settings; see the Scrapy docs for the full
list of what's available:
https://docs.scrapy.org/en/latest/topics/settings.html

The project-specific settings (BASE_URL, SUPPORTED_LANGUAGES, *_DIR, ...) are
at the bottom and can be overridden via `main.py` CLI flags -- see README.md.
"""

BOT_NAME = "ornacodex"

SPIDER_MODULES = ["ornacodex.spiders"]
NEWSPIDER_MODULE = "ornacodex.spiders"

# Identify ourselves to the server we're crawling.
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.3"

# Obey robots.txt rules.
ROBOTSTXT_OBEY = True

# Required for the asyncio-based Twisted reactor used by the scripts in
# ornacodex/scripts/ (they call `runner.join()` / await events).
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# --- Project-specific settings -----------------------------------------

BASE_URL = "https://playorna.com"
BASE_LANGUAGE = 'en'
SUPPORTED_LANGUAGES = [
    BASE_LANGUAGE,  # English
    'es',           # Spanish
    'fr',           # French
    'de',           # German
    'zh-hans',      # Chinese Simplified
    'zh-hant',      # Chinese Traditional
    'ja',           # Japanese
    'ko',           # Korean
    'pt',           # Portuguese
    'ru',           # Russian
    'ar',           # Arabic
    'it',           # Italian
]
VERSION = '1.0.0'

# Working directories used by ornacodex/scripts/*.py (overridable via
# `python main.py <command> --tmp/--output/--extra/--dump/--export`).
TMP_DIR = 'tmp'
OUTPUT_DIR = 'output'
EXTRA_DIR = 'extra'
DUMP_DIR = 'dump'
EXPORT_EXTRA_DIR = 'export'
