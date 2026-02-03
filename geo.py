import math
from typing import Optional

def distance(a_x, a_y, b_x, b_y) -> Optional[float]:
    if None in (a_x, a_y, b_x, b_y):
        return None
    return math.sqrt((a_x - b_x)**2 + (a_y - b_y)**2)
