import argparse
import importlib
from pathlib import Path

from scrapy.utils.project import get_project_settings

SCRIPTS_DIR = Path(__file__).parent / 'ornacodex' / 'scripts'
COMMANDS = sorted(
    p.stem for p in SCRIPTS_DIR.glob('*.py') if not p.stem.startswith('_')
)


def main():
    parser = argparse.ArgumentParser(
        prog="OrnaCodexCrawler",
        description="Crawl and process the Orna game codex (playorna.com/codex).",
    )
    parser.add_argument(
        'command', choices=COMMANDS,
        help='Pipeline step to run, in typical order: download, codex, '
             'dump_toml, export_extra, realm_raids, update_extra. '
             'See README.md for what each one does.',
    )
    parser.add_argument('--tmp', help="override TMP_DIR (raw per-language crawl output)")
    parser.add_argument('--output', help="override OUTPUT_DIR (merged codex.json + i18n)")
    parser.add_argument('--extra', help="override EXTRA_DIR (hand-maintained TOML extras)")
    parser.add_argument('--dump', help="override DUMP_DIR (TOML dump of the codex)")
    parser.add_argument('--export', help="override EXPORT_EXTRA_DIR (JSON export of EXTRA_DIR)")
    parser.add_argument('--httpcache', action='store_true', help='enable Scrapy HTTP cache')
    parser.add_argument('--base', help='override BASE_URL (default: https://playorna.com)')
    parser.add_argument(
        '--force-ipv4', action='store_true',
        help="resolve DNS to IPv4 only. Workaround for hosts where IPv6 DNS "
             "records exist but aren't actually routable, which can make every "
             "request silently fail even though e.g. curl works fine -- see "
             "ornacodex/utils/network.py.",
    )

    args = parser.parse_args()

    try:
        mod = importlib.import_module(f'ornacodex.scripts.{args.command}')
    except Exception as e:
        parser.error(f'failed to load command {args.command!r}: {e}')

    settings = get_project_settings()
    if args.tmp:
        settings.set('TMP_DIR', args.tmp)
    if args.output:
        settings.set('OUTPUT_DIR', args.output)
    if args.extra:
        settings.set('EXTRA_DIR', args.extra)
    if args.dump:
        settings.set('DUMP_DIR', args.dump)
    if args.export:
        settings.set('EXPORT_EXTRA_DIR', args.export)
    if args.httpcache:
        settings.set('HTTPCACHE_ENABLED', True)
    if args.base:
        settings.set('BASE_URL', args.base)
    if args.force_ipv4:
        from ornacodex.utils.network import force_ipv4_resolution
        force_ipv4_resolution()

    mod.run(settings)


if __name__ == '__main__':
    main()
