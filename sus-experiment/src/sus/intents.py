from enum import Enum
from typing import List, Dict

class Intent(Enum):
    # PHYSICAL
    P1 = ("Skin & Silence", "PHYSICAL", 4)
    P2 = ("One Night, No Trace", "PHYSICAL", 5)
    P3 = ("Slow Burn", "PHYSICAL", 3)
    P4 = ("Kinetic Energy", "PHYSICAL", 2)
    P5 = ("Forbidden Curiosity", "PHYSICAL", 5)

    # INTELLECTUAL
    I1 = ("3 AM Philosophy", "INTELLECTUAL", 2)
    I2 = ("Intellectual Sparring", "INTELLECTUAL", 2)
    I3 = ("Career / Ambition Talk", "INTELLECTUAL", 1)
    I4 = ("Teach Me Something", "INTELLECTUAL", 2)
    I5 = ("Unfiltered Opinions", "INTELLECTUAL", 3)

    # EMOTIONAL
    E1 = ("Honest Stranger", "EMOTIONAL", 3)
    E2 = ("Non-Judgmental Venting", "EMOTIONAL", 2)
    E3 = ("Shared Silence", "EMOTIONAL", 2)
    E4 = ("Casual Listening", "EMOTIONAL", 1)
    E5 = ("Soft Landing", "EMOTIONAL", 2)

    # CHAOS
    S1 = ("Escape From the City", "CHAOS", 3)
    S2 = ("Cultural Observer", "CHAOS", 3)
    S3 = ("Random Adventure", "CHAOS", 3)
    S4 = ("Spontaneous Chaos", "CHAOS", 4)
    S5 = ("Food & Corner Spot Hunt", "CHAOS", 4)

    def __init__(self, label: str, quadrant: str, taboo_index: int):
        self.label = label
        self.quadrant = quadrant
        self.taboo_index = taboo_index

# Poetic labels to Intent mapping
LABEL_TO_INTENT: Dict[str, Intent] = {intent.label: intent for intent in Intent}

# Ordered list for index-based bitmask (20 bits)
INTENT_LIST: List[Intent] = list(Intent)

def get_intent_by_index(index: int) -> Intent:
    return INTENT_LIST[index]

def get_index_by_intent(intent: Intent) -> int:
    return INTENT_LIST.index(intent)
