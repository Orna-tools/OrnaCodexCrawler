from scrapy.http.response import Response

from ..utils.extractor import Extractor
from ..items import Items

from ._base import BaseSpider


class Spider(BaseSpider):
    name = "items"

    def parse_item(self, response: Response):
        struct = self.extract_base_fields(response)

        struct['description'] = self.extract_text(
            response, "//pre[@class='codex-page-description']")

        exotic = response.xpath(
            "//div[@class='codex-page-meta']/span[@class='exotic']").xpath('string()').get()
        if exotic is not None:
            struct['exotic'] = exotic

        struct['meta'] = self.extract_meta(
            response, "//div[@class='codex-page-meta' and not(span[@class='exotic'])]")

        tags = self.extract_tags(response)
        if tags:
            struct['tags'] = tags

        stats = response.xpath(
            "//div[@class='codex-stats']/div[contains(@class,'codex-stat')]")
        if stats:
            tmp = []
            for stat in stats:
                s = stat.xpath("string()").get().strip()
                if len(stat.xpath("@class").get().split()) > 1:
                    tmp.append(('element', [s]))
                else:
                    if ' / ' in s:
                        for ss in s.split('/'):
                            tmp.append(tuple(i.strip()
                                       for i in Extractor.extract_kv(ss.strip())))
                    else:
                        tmp.append(tuple(i.strip()
                                   for i in Extractor.extract_kv(s)))
            struct['stats'] = tmp

        # NB: this also looks for a `div.codex-page-description`, which doesn't
        # exist on item pages (items use `pre.codex-page-description`) unless
        # the off-hand-ability markup adds one; kept as-is from upstream.
        ability = response.xpath(
            "//div[@class='codex-page-description']/preceding-sibling::div[1] | //div[@class='codex-page-description']").xpath("string()").getall()
        if len(ability) == 2:
            struct['ability'] = (
                Extractor.extract_kv(ability[0])[-1].strip(),
                ability[1].strip()
            )

        drops = self.extract_drops(response)
        if drops:
            struct['drops'] = drops

        yield Items(struct)
