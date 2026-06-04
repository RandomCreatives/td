from sus.intent_engine import encode_mask, decode_mask, get_overlap, get_quadrant_distribution, get_taboo_score
from sus.intents import INTENT_LIST

def test_bitmask_encoding():
    indices = [0, 2, 6, 10, 17]
    mask = encode_mask(indices)
    assert bin(mask).count('1') == 5

    decoded = decode_mask(mask)
    assert len(decoded) == 5
    assert decoded[0] == INTENT_LIST[0]
    assert decoded[2] == INTENT_LIST[6]

def test_overlap():
    m1 = encode_mask([0, 1, 2, 3, 4])
    m2 = encode_mask([3, 4, 5, 6, 7])
    assert get_overlap(m1, m2) == 2

    m3 = encode_mask([0, 1, 2, 3, 4])
    assert get_overlap(m1, m3) == 5

def test_quadrant_distribution():
    # P1, P2 (PHYSICAL), I1 (INTELLECTUAL), E1 (EMOTIONAL), S1 (CHAOS)
    mask = encode_mask([0, 1, 5, 10, 15])
    dist = get_quadrant_distribution(mask)
    assert dist["PHYSICAL"] == 2
    assert dist["INTELLECTUAL"] == 1
    assert dist["EMOTIONAL"] == 1
    assert dist["CHAOS"] == 1

def test_taboo_score():
    # P1(4), P2(5)
    mask = encode_mask([0, 1])
    assert get_taboo_score(mask) == 9
