from sus.intents import INTENT_LIST, Intent

def encode_mask(indices: list[int]) -> int:
    mask = 0
    for i in indices:
        mask |= (1 << i)
    return mask

def decode_mask(mask: int) -> list[Intent]:
    intents = []
    for i in range(len(INTENT_LIST)):
        if mask & (1 << i):
            intents.append(INTENT_LIST[i])
    return intents

def get_overlap(mask_a: int, mask_b: int) -> int:
    return bin(mask_a & mask_b).count('1')

def get_quadrant_distribution(mask: int) -> dict:
    intents = decode_mask(mask)
    dist = {}
    for intent in intents:
        dist[intent.quadrant] = dist.get(intent.quadrant, 0) + 1
    return dist

def get_taboo_score(mask: int) -> int:
    intents = decode_mask(mask)
    return sum(intent.taboo_index for intent in intents)
