from scrapy.http.response import Response

from ..items import Followers

from ._base import BaseSpider


class Spider(BaseSpider):
    name = "followers"

    def parse_item(self, response: Response):
        struct = self.extract_base_fields(response)

        struct['description'] = self.extract_text(
            response, "//div[@class='codex-page-description']")

        events = self.extract_events(response)
        if events:
            struct['events'] = events

        # exclude `description`, which is also matched by this xpath
        struct['meta'] = self.extract_meta(
            response,
            "//div[@class='codex-page-meta'] | //div[@class='codex-page-description']")[1:]

        stats = response.xpath("//dl[@class='stats']")
        struct['stats'] = list(
            zip(stats.xpath("./dt/text()").getall(), stats.xpath("./dd/text()").getall()))

        drops = self.extract_drops(response)
        if drops:
            struct['drops'] = drops

        yield Followers(struct)
