# OrnaCodexCrawler

A [Scrapy](https://scrapy.org/)-based crawler and data pipeline for the
[Orna](https://playorna.com) game codex (`playorna.com/codex`). It crawls
every codex category (items, spells, classes, followers, monsters, bosses,
raids) in every language the site supports, merges them into a single
cross-referenced `codex.json` plus per-language translation files, and offers
a few downstream commands for exporting/curating that data.

> Forked from [67au/OrnaCodexCrawler](https://github.com/67au/OrnaCodexCrawler).

## Requirements

- Python 3.12+
- [Scrapy](https://scrapy.org/) and [tomlkit](https://github.com/sdispater/tomlkit)

## Installation

With [uv](https://docs.astral.sh/uv/) (recommended — this repo ships a
`uv.lock`):

```bash
uv sync
```

Or with plain `pip`:

```bash
python -m venv venv
source venv/bin/activate
pip install scrapy tomlkit
```

## Usage

Everything runs through `main.py`:

```bash
python main.py <command> [options]
```

```
python main.py --help
```

### Pipeline

The commands are typically run in this order. Each one reads the output of
the previous step from disk, so they can be re-run independently once the
earlier steps have produced their files.

| # | Command        | What it does |
|---|----------------|---------------|
| 1 | `download`     | Crawls every codex category, in every supported language, into raw per-language JSON. Also resolves cross-references (e.g. a monster drop pointing at an item that wasn't crawled yet) in up to 3 follow-up passes. |
| 2 | `codex`        | Merges the raw crawl output into one cross-referenced `codex.json` (entries, icon map, filter options, sort metadata) plus a translation file per language. |
| 3 | `clean_items`  | Republishes `download`'s raw per-language item entries (id, name, icon, category, description, stats, drops, ...) as `output/cleaned/<language>/items.json`, for consumers like [OA_Database](https://github.com/Orna-tools/OA_Database) that want self-contained item data without joining against `codex.json`/i18n. Only needs `download`, not `codex`. |
| 4 | `dump_toml`    | Converts `codex.json` and the translation files into TOML, which diffs much more readably than minified JSON in version control. |
| 5 | `export_extra` | Converts the hand-maintained TOML files in `EXTRA_DIR` (see `update_extra` below) into JSON for downstream consumption. |
| 6 | `realm_raids`  | Builds `realm.json` (tier/HP/icon/localized name for every raid) and downloads the raid icon images. |
| 7 | `update_extra` | Regenerates the editable TOML stubs in `EXTRA_DIR`: a boss-scaling list for weapons/armor, and per-boss/monster/raid files for hand-filling elemental weaknesses/resistances/immunities. Existing hand-edited values are preserved across runs. |

```bash
python main.py download
python main.py codex
python main.py clean_items     # optional, only needed for OA_Database-style consumers
python main.py dump_toml       # optional
python main.py update_extra    # optional, then hand-edit the generated TOML
python main.py export_extra    # optional, after editing the TOML above
python main.py realm_raids     # optional
```

### Options

| Flag | Overrides | Default |
|------|-----------|---------|
| `--tmp DIR` | `TMP_DIR` (raw per-language crawl output) | `tmp` |
| `--output DIR` | `OUTPUT_DIR` (merged `codex.json` + i18n) | `output` |
| `--extra DIR` | `EXTRA_DIR` (hand-maintained TOML extras) | `extra` |
| `--dump DIR` | `DUMP_DIR` (TOML dump of the codex) | `dump` |
| `--export DIR` | `EXPORT_EXTRA_DIR` (JSON export of `EXTRA_DIR`) | `export` |
| `--base URL` | `BASE_URL` | `https://playorna.com` |
| `--httpcache` | enables Scrapy's HTTP cache (handy while iterating locally) | off |
| `--force-ipv4` | resolve DNS to IPv4 only — workaround for hosts with broken/unreachable IPv6 routing (symptom: `download`/`realm_raids` finish instantly with 0 pages crawled, but `curl https://playorna.com` works fine) | off |

All of the above are also plain Scrapy settings in `ornacodex/settings.py`,
including `SUPPORTED_LANGUAGES`.

### Output layout

```
output/
├── index.json        # version, timestamp, and paths to the files below
├── codex.json         # { main, icons, options, sorts, base_stats }
├── i18n/
│   ├── en.json
│   ├── es.json
│   └── ...
└── cleaned/           # only after `clean_items`
    ├── en/items.json
    ├── es/items.json
    └── ...
```

## Development

```bash
uv sync   # installs project + dev dependencies (pytest), as declared in [dependency-groups]
# or: pip install scrapy tomlkit pytest
python -m pytest
```

The test suite covers the pure parsing/formatting helpers
(`ornacodex/utils/`) and the shared spider extraction logic
(`ornacodex/spiders/_base.py`) against small synthetic HTML fixtures — it
doesn't hit the network.

## License

[MIT](LICENSE)
