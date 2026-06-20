from scrapy.http.response import Response

from ..items import Monsters

from ._base import BaseSpider


class Spider(BaseSpider):
    name = "monsters"

    def parse_item(self, response: Response):
        struct = self.extract_base_fields(response)

        events = self.extract_events(response)
        if events:
            struct['events'] = events

        struct['meta'] = self.extract_meta(
            response,
            "//div[@class='codex-page-meta'] | //div[@class='codex-page-description']")

        drops = self.extract_drops(response)
        if drops:
            struct['drops'] = drops

        yield Monsters(struct)
