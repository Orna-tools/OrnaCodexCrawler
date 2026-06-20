import pytest
from scrapy.settings import Settings

from ornacodex.scripts import download


def test_run_preserves_caller_settings(monkeypatch):
    """Regression test: run() used to discard whatever settings main.py built
    from CLI flags (--tmp/--output/--extra/--dump/--export/--base/--httpcache)
    and replace it with a fresh get_project_settings(), silently defeating all
    of them. It should use the settings object it was actually given.
    """
    received = {}

    def fake_crawl_codex(settings):
        received['settings'] = settings

    monkeypatch.setattr(download, 'crawl_codex', fake_crawl_codex)

    settings = Settings()
    settings.set('TMP_DIR', '/custom/tmp')
    settings.set('BASE_URL', 'https://example.invalid')

    download.run(settings)

    assert received['settings'] is settings
    assert received['settings'].get('TMP_DIR') == '/custom/tmp'
    assert received['settings'].get('BASE_URL') == 'https://example.invalid'


def test_run_sets_info_log_level_by_default(monkeypatch):
    received = {}
    monkeypatch.setattr(download, 'crawl_codex', lambda settings: received.update(s=settings))

    settings = Settings()
    download.run(settings)

    assert received['s'].get('LOG_LEVEL') == 'INFO'


def test_run_respects_explicit_loglevel_override(monkeypatch):
    """A --loglevel flag (applied at cmdline priority, like main.py does)
    should survive run()'s own settings['LOG_LEVEL'] = 'INFO' assignment.
    """
    received = {}
    monkeypatch.setattr(download, 'crawl_codex', lambda settings: received.update(s=settings))

    settings = Settings()
    settings.set('LOG_LEVEL', 'DEBUG', priority='cmdline')

    download.run(settings)

    assert received['s'].get('LOG_LEVEL') == 'DEBUG'


def test_select_crawlers_defaults_to_everything():
    assert download.select_crawlers(None) == download.ALL_CRAWLERS
    assert download.select_crawlers([]) == download.ALL_CRAWLERS


def test_select_crawlers_filters_to_requested_categories():
    result = download.select_crawlers(['items'])
    assert [c.Spider.name for c in result] == ['items']


def test_select_crawlers_preserves_requested_order():
    result = download.select_crawlers(['spells', 'items'])
    assert [c.Spider.name for c in result] == ['spells', 'items']


def test_select_crawlers_rejects_unknown_category():
    with pytest.raises(ValueError, match="unknown categories"):
        download.select_crawlers(['items', 'not-a-real-category'])
