from ornacodex.utils.extractor import Extractor


def test_extract_kv_basic():
    assert Extractor.extract_kv('Tier: 10') == ('Tier', '10')


def test_extract_kv_handles_fullwidth_colon():
    assert Extractor.extract_kv('属性：火') == ('属性', '火')


def test_extract_kv_only_splits_once():
    assert Extractor.extract_kv('Drop: Item: Bonus') == ('Drop', 'Item: Bonus')


def test_extract_kv_no_colon_returns_single_tuple():
    assert Extractor.extract_kv('Just a label') == ('Just a label',)


def test_extract_chance_match():
    assert Extractor.extract_chance('Iron Sword (12.5%)') == ('Iron Sword', '12.5%')


def test_extract_chance_no_match_returns_none():
    assert Extractor.extract_chance('Iron Sword') is None


def test_extract_codex_id():
    assert Extractor.extract_codex_id('/codex/items/iron-sword/') == ['items', 'iron-sword']


def test_extract_bond_bond_entry():
    bb = Extractor.extract_bond('Test Bond (25%)')
    assert bb == [{'name': 'Test Bond', 'chance': '25%', 'type': 'BOND'}]


def test_extract_bond_ability_entry():
    bb = Extractor.extract_bond('+Special: Fireball')
    assert bb == [{'name': 'Fireball', 'type': 'ABILITY'}]


def test_extract_bond_bonus_entry():
    bb = Extractor.extract_bond('Attack: +10%')
    assert bb == [{'name': 'Attack', 'value': '+10%', 'type': 'BONUS'}]


def test_extract_bond_buff_entry():
    bb = Extractor.extract_bond('+Haste')
    assert bb == [{'name': 'Haste', 'type': 'BUFF'}]


def test_extract_bond_multiple_comma_separated():
    bb = Extractor.extract_bond('+Haste, Attack: +10%')
    assert bb == [
        {'name': 'Haste', 'type': 'BUFF'},
        {'name': 'Attack', 'value': '+10%', 'type': 'BONUS'},
    ]
