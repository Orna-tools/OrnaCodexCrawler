from scrapy.http.response import Response

from ..items import Classes

from ._base import BaseSpider


class Spider(BaseSpider):
    name = "classes"

    def parse_item(self, response: Response):
        struct = self.extract_base_fields(response, include_aura=False)

        struct['description'] = self.extract_text(
            response, "//div[@class='codex-page-description']")

        struct['meta'] = self.extract_meta(response)

        drops = self.extract_drops(response)
        if drops:
            struct['drops'] = drops

        yield Classes(struct)
