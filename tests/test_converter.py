from ornacodex.utils.converter import Converter, UniqueKeyGenerator


def test_convert_key_lowercases_and_replaces_spaces():
    assert Converter.convert_key('Off-Hand Ability') == 'off-hand_ability'


def test_convert_key_replaces_punctuation():
    assert Converter.convert_key("Foresight: +1.5/5'") == 'foresight__+1_5_5_'


def test_unique_key_generator_first_use_is_unsuffixed():
    gen = UniqueKeyGenerator()
    assert gen.generate_unique_key(('fireball', 'icon-a.png')) == 'fireball'


def test_unique_key_generator_suffixes_on_collision():
    gen = UniqueKeyGenerator()
    gen.generate_unique_key(('fireball', 'icon-a.png'))
    assert gen.generate_unique_key(('fireball', 'icon-b.png')) == 'fireball_1'


def test_unique_key_generator_reuses_key_for_identical_identifier():
    gen = UniqueKeyGenerator()
    first = gen.generate_unique_key(('fireball', 'icon-a.png'))
    second = gen.generate_unique_key(('fireball', 'icon-a.png'))
    assert first == second == 'fireball'
