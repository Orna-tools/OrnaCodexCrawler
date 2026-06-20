from scrapy.http.response import Response

from ..items import Raids

from ._base import BaseSpider


class Spider(BaseSpider):
    name = "raids"

    def parse_item(self, response: Response):
        struct = self.extract_base_fields(response)

        struct['description'] = self.extract_text(
            response, "//div[@class='codex-page-description']")

        events = self.extract_events(response)
        if events:
            struct['events'] = events

        tags = self.extract_tags(response)
        if tags:
            struct['tags'] = tags

        struct['meta'] = self.extract_meta(response)

        drops = self.extract_drops(response)
        if drops:
            struct['drops'] = drops

        yield Raids(struct)
