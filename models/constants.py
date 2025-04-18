from enum import Enum

class ITEM_TYPE(Enum):
    TOP = "TOP"
    BOTTOM = "BOTTOM"
    ACCESSORY = "ACCESSORY"
    OUTER = "OUTER"
    SHOE = "SHOE"
    
class ITEM_STATUS(Enum):
    AVAILABLE = 1
    UNAVAILABLE = 0

WASHABLE_ITEM_TYPES = [
    ITEM_TYPE.TOP
]
