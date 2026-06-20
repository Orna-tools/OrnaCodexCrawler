from scrapy.http import HtmlResponse

from ornacodex.spiders.items import Spider as ItemSpider


def make_response(url: str, body: str) -> HtmlResponse:
    return HtmlResponse(url=url, body=body.encode('utf-8'), encoding='utf-8')


def make_spider(category_text: str = 'Items') -> ItemSpider:
    spider = ItemSpider.__new__(ItemSpider)
    spider.category_text = category_text
    return spider


PAGE_HTML = """
<html><body>
<h1>Sword of Testing</h1>
<div class="codex-page-icon"><img src="/i/swords/test_sword.png" class="fire"/></div>
<div class="codex-page">
<h4>Dropped By: Test Mobs</h4>
<a href="/codex/monsters/test-mob/"><span>Test Mob (5%)</span></a>
<hr/>
<h4>Upgrade Materials</h4>
<a href="/codex/items/test-mat/"><img src="/i/mats/m.png"/><span>Test Material</span></a>
</div>
</body></html>
"""


def test_extract_base_fields():
    response = make_response('https://playorna.com/codex/items/test-sword/', PAGE_HTML)
    spider = make_spider()
    struct = spider.extract_base_fields(response)
    assert struct == {
        'category': 'Items',
        'id': 'test-sword',
        'name': 'Sword of Testing',
        'icon': 'ds/test_sword.png',
        'aura': 'fire',
    }


def test_extract_base_fields_without_aura():
    response = make_response(
        'https://playorna.com/codex/items/test-sword/',
        '<html><body><h1>X</h1><div class="codex-page-icon">'
        '<img src="/i/x.png" class=""/></div></body></html>',
    )
    spider = make_spider()
    struct = spider.extract_base_fields(response, include_aura=False)
    assert 'aura' not in struct


def test_extract_drops():
    response = make_response('https://playorna.com/codex/items/test-sword/', PAGE_HTML)
    spider = make_spider()
    drops = spider.extract_drops(response)
    assert drops == [
        ('Dropped By', [{'name': 'Test Mob', 'chance': '5%'}]),
        ('Upgrade Materials', [{'name': 'Test Material', 'icon': '/m.png'}]),
    ]


def test_extract_drops_no_drops_section():
    response = make_response(
        'https://playorna.com/codex/items/test-sword/',
        '<html><body><h1>X</h1></body></html>',
    )
    spider = make_spider()
    assert spider.extract_drops(response) == []


def test_parse_page_stops_when_no_entries_found():
    """Regression test: pagination used to recurse forever past the last page."""
    import scrapy

    spider = ItemSpider.__new__(ItemSpider)
    spider.language = 'en'
    spider.category_url = 'https://playorna.com/codex/items'

    request = scrapy.Request(
        'https://playorna.com/codex/items', meta={'page': 99})
    empty_page = HtmlResponse(
        url='https://playorna.com/codex/items',
        body=b'<html><body><div class="codex-entries"></div></body></html>',
        encoding='utf-8',
        request=request,
    )

    assert list(spider.parse_page(empty_page)) == []
