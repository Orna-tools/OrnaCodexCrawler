"""Produce `output/cleaned/<language>/items.json` for each supported language.

This is the step that the `.github/workflows/crawl.yml` "Copy cleaned items
to OA_Database" job has always expected to exist, but never actually did --
`download` only writes raw per-language data to TMP_DIR, and nothing else in
this project ever wrote anything under OUTPUT_DIR/cleaned/. That meant the
copy step silently found nothing to copy on every run.

This reads the raw item entries `download` already wrote to
`TMP_DIR/entries/<language>/items.json` and republishes them, one list per
language, under `OUTPUT_DIR/cleaned/<language>/items.json` -- id, name, icon,
category, description, stats, drops, etc. all included, so a consumer
doesn't need to cross-reference codex.json/i18n to make sense of an entry.

Only needs `download` to have run first; doesn't depend on the `codex` step.
"""

import json
from pathlib import Path

from scrapy.settings import Settings

from ..utils.path_config import TmpPathConfig


def run(settings: Settings):
    tmp_dir_config = TmpPathConfig(settings.get('TMP_DIR'))
    output_dir = Path(settings.get('OUTPUT_DIR'))
    languages = settings.get('SUPPORTED_LANGUAGES', [])

    cleaned_dir = output_dir.joinpath('cleaned')
    cleaned_dir.mkdir(parents=True, exist_ok=True)

    for language in languages:
        entries_file = tmp_dir_config.entries.joinpath(language, 'items.json')
        try:
            with open(entries_file) as f:
                entries = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f'Skipping {language}: could not read {entries_file} ({e})')
            continue

        entries.sort(key=lambda e: e['id'])

        lang_dir = cleaned_dir.joinpath(language)
        lang_dir.mkdir(exist_ok=True)
        items_file = lang_dir.joinpath('items.json')
        with open(items_file, 'w') as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)

        print(f'Cleaned {len(entries)} items -> {items_file}')
