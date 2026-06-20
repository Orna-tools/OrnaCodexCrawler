from abc import abstractmethod
from collections.abc import Iterable
import scrapy

from scrapy.http.request import Request
from scrapy.http.response import Response
from scrapy.utils.project import get_project_settings

from ..utils.extractor import Extractor
from ..utils.url_utils import UrlBuilder, UrlParser

settings = get_project_settings()


class BaseSpider(scrapy.Spider):
    """Common pagination + field-extraction logic shared by every codex category spider.

    A category spider only needs to define `name` (matching the codex URL segment,
    e.g. "items", "bosses") and a `parse_item` method that builds the category-specific
    fields on top of `extract_base_fields`.
    """

    name = "_base"
    allowed_domains = []

    def __init__(
        self,
        name: str = None,
        language: str = None,
        start_ids: list[str] | str = None,
        **kwargs
    ) -> None:
        super().__init__(name, **kwargs)
        self.language = language or settings.get('BASE_LANGUAGE')
        self.category_url = UrlBuilder.category(self.name)
        if isinstance(start_ids, str):
            self.start_ids = [start_ids]
        else:
            self.start_ids = start_ids or []

    # -- crawling -----------------------------------------------------------

    def start_requests(self) -> Iterable[Request]:
        yield scrapy.FormRequest(
            self.category_url,
            method='GET',
            formdata={'lang': self.language},
            callback=self.parse_pre,
        )

    def parse_pre(self, response: Response):
        self.category_text = self.extract_text(response, '//h1[@class="herotext"]')
        if self.start_ids:
            for id in self.start_ids:
                yield scrapy.FormRequest(
                    f"{self.category_url}/{id}",
                    method='GET',
                    formdata={'lang': self.language},
                    callback=self.parse_item,
                )
        else:
            yield self.parse(response)

    def parse(self, response: Response) -> scrapy.FormRequest:
        page = response.meta.get("page") or 1
        return scrapy.FormRequest(
            url=self.category_url,
            method='GET',
            formdata={'p': str(page), 'lang': self.language},
            callback=self.parse_page,
            errback=self.parse_err,
            meta={'page': page + 1}
        )

    def parse_page(self, response: Response):
        entries = response.xpath('//div[@class="codex-entries"]/a')
        if not entries:
            # Past the last page: stop paginating instead of requesting forever.
            return
        for entry in entries:
            id = entry.attrib['href']
            yield scrapy.FormRequest(
                f"{UrlBuilder.base}{id}",
                method='GET',
                formdata={'lang': self.language},
                callback=self.parse_item,
            )
        yield self.parse(response)

    @abstractmethod
    def parse_item(self, response: Response):
        pass

    def parse_err(self, response: Response):
        pass

    # -- shared field extraction --------------------------------------------
    # These cover the markup that's identical across every codex page type;
    # spiders only need to extract the fields that make their category unique.

    def extract_text(self, response: Response, xpath_expr: str) -> str:
        """Return the stripped string content of the first node matching xpath_expr.

        Safe against missing nodes (returns '' rather than raising on None).
        """
        return (response.xpath(xpath_expr).xpath('string()').get() or '').strip()

    def extract_base_fields(self, response: Response, include_aura: bool = True) -> dict:
        """Extract the fields present on every codex entry: category, id, name, icon
        and (optionally) aura.
        """
        struct = {
            'category': self.category_text,
            'id': response.url.split('/')[-2],
            'name': self.extract_text(response, '//h1'),
            'icon': UrlParser.icon(
                response.xpath("//div[@class='codex-page-icon']/img/@src").get()),
        }
        if include_aura:
            aura = (response.xpath(
                "//div[@class='codex-page-icon']/img/@class").get() or '').strip()
            if aura:
                struct['aura'] = aura
        return struct

    def extract_meta(
        self,
        response: Response,
        xpath_expr: str = "//div[@class='codex-page-meta']",
    ) -> list[tuple[str, str] | tuple[str]]:
        """Extract `Key: Value` rows from the codex-page-meta block(s)."""
        meta = response.xpath(xpath_expr).xpath('string()').getall()
        return [Extractor.extract_kv(m.strip()) for m in meta]

    def extract_events(self, response: Response) -> list[str] | None:
        """Extract the sorted realm/event names from the highlighted description
        block, if the page has one (bosses, monsters, followers, raids).
        """
        events = response.xpath(
            '//div[@class="codex-page-description codex-page-description-highlight"]'
        ).xpath('string()')
        if not events:
            return None
        return sorted(
            e.strip() for e in Extractor.extract_kv(events.get().strip())[-1].split('/')
        )

    def extract_tags(self, response: Response) -> list[str] | None:
        """Extract codex-page-tag labels (e.g. item/spell/raid tags), if present."""
        tags = response.xpath(
            "//div[@class='codex-page-tag']").xpath('string()').getall()
        if not tags:
            return None
        return [s.strip()[2:] for s in tags]

    def extract_drops(self, response: Response) -> list[tuple[str, list[dict]]]:
        """Parse the `<h4>`-headed drop/reward tables shared by every codex page
        (e.g. "Dropped By", "Upgrade Materials", "Abilities").
        """
        headings = response.xpath("//div[@class='codex-page'][1]/h4")
        drops = []
        for heading in headings:
            drop_name = Extractor.extract_kv(heading.xpath('string()').get())[0].strip()
            sibling = heading.xpath('./following-sibling::*[1]')
            entries = []
            while sibling:
                if sibling.xpath('self::hr | self::h4'):
                    break
                entries.append(Extractor.extract_drop(sibling))
                sibling = sibling.xpath('./following-sibling::*[1]')
            drops.append((drop_name, entries))
        return drops
