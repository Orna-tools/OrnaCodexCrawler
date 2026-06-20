from scrapy.http.response import Response

from ..utils.extractor import Extractor
from ..items import Spells

from ._base import BaseSpider


class Spider(BaseSpider):
    name = "spells"

    def parse_item(self, response: Response):
        struct = self.extract_base_fields(response, include_aura=False)

        struct['description'] = self.extract_text(
            response, "//div[@class='codex-page-description']")

        meta = response.xpath(
            "//div[@class='codex-page-meta']").xpath('string()').getall()
        struct['tier'], struct['spell_type'] = meta[0].strip().strip('★').split()
        struct['stats'] = [Extractor.extract_kv(m.strip()) for m in meta[1:]]

        element = response.xpath(
            "//div[contains(@class,'codex-stat')]").xpath('string()').get()
        if element:
            struct['stats'].append(
                ('element', [s.strip() for s in Extractor.extract_kv(element)[-1].split(',')]))

        tags = self.extract_tags(response)
        if tags:
            struct['tags'] = tags

        drops = self.extract_drops(response)
        if drops:
            struct['drops'] = drops

        yield Spells(struct)
