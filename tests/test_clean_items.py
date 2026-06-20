import json

from scrapy.settings import Settings

from ornacodex.scripts import clean_items

RAW_ITEMS = [
    {
        'category': 'Items',
        'id': 'zzz-sword',
        'name': 'Zzz Sword',
        'icon': '/i/swords/zzz.png',
        'description': 'A late-alphabet blade.',
        'meta': [['Tier', '5']],
        'stats': [['Attack', '50']],
    },
    {
        'category': 'Items',
        'id': 'aaa-shield',
        'name': 'Aaa Shield',
        'icon': '/i/shields/aaa.png',
        'exotic': 'Exotic',
        'description': 'An early-alphabet shield.',
        'meta': [['Tier', '10']],
        'stats': [['Defense', '100']],
        'drops': [['Dropped By', [{'name': 'Test Mob', 'chance': '5%'}]]],
    },
]


def write_settings(tmp_path) -> Settings:
    tmp_dir = tmp_path / 'tmp'
    entries_dir = tmp_dir / 'entries' / 'en'
    entries_dir.mkdir(parents=True)
    with open(entries_dir / 'items.json', 'w') as f:
        json.dump(RAW_ITEMS, f)

    settings = Settings()
    settings.set('TMP_DIR', str(tmp_dir))
    settings.set('OUTPUT_DIR', str(tmp_path / 'output'))
    settings.set('SUPPORTED_LANGUAGES', ['en'])
    return settings


def test_clean_items_writes_per_language_file(tmp_path):
    settings = write_settings(tmp_path)
    clean_items.run(settings)

    output_file = tmp_path / 'output' / 'cleaned' / 'en' / 'items.json'
    assert output_file.exists()

    with open(output_file) as f:
        cleaned = json.load(f)
    assert len(cleaned) == 2


def test_clean_items_preserves_all_fields(tmp_path):
    """The whole point is to be richer than the old name+stats-only shape."""
    settings = write_settings(tmp_path)
    clean_items.run(settings)

    with open(tmp_path / 'output' / 'cleaned' / 'en' / 'items.json') as f:
        cleaned = json.load(f)

    shield = next(e for e in cleaned if e['id'] == 'aaa-shield')
    assert shield['name'] == 'Aaa Shield'
    assert shield['icon'] == '/i/shields/aaa.png'
    assert shield['category'] == 'Items'
    assert shield['exotic'] == 'Exotic'
    assert shield['description'] == 'An early-alphabet shield.'
    assert shield['stats'] == [['Defense', '100']]
    assert shield['drops'] == [['Dropped By', [{'name': 'Test Mob', 'chance': '5%'}]]]


def test_clean_items_sorts_by_id(tmp_path):
    settings = write_settings(tmp_path)
    clean_items.run(settings)

    with open(tmp_path / 'output' / 'cleaned' / 'en' / 'items.json') as f:
        cleaned = json.load(f)

    assert [e['id'] for e in cleaned] == ['aaa-shield', 'zzz-sword']


def test_clean_items_skips_missing_language_without_aborting(tmp_path):
    """A missing/failed download for one language shouldn't lose every
    other language's output."""
    settings = write_settings(tmp_path)
    settings.set('SUPPORTED_LANGUAGES', ['en', 'es'])  # 'es' was never written

    clean_items.run(settings)

    assert (tmp_path / 'output' / 'cleaned' / 'en' / 'items.json').exists()
    assert not (tmp_path / 'output' / 'cleaned' / 'es').exists()
