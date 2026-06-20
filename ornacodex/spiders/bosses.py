from scrapy.http.response import Response

from ..items import Bosses

from ._base import BaseSpider


class Spider(BaseSpider):
    name = "bosses"

    def parse_item(self, response: Response):
        struct = self.extract_base_fields(response)

        events = self.extract_events(response)
        if events:
            struct['events'] = events

        struct['meta'] = self.extract_meta(
            response,
            "//div[@class='codex-page-meta'] | //div[@class='codex-page-description']")

        if 'aura' in struct:
            # patch for `kin-of-kerberos`: keep only the last aura class token
            struct['aura'] = struct['aura'].split()[-1]

        drops = self.extract_drops(response)
        if drops:
            struct['drops'] = drops

        yield Bosses(struct)
