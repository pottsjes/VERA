from enum import Enum

class ITEM_TYPE(Enum):
    TOP = "Top"
    BOTTOM = "Bottom"
    ACCESSORY = "Accessory"
    OUTER = "Outer"
    SHOE = "Shoe"
    
class ITEM_STATUS(Enum):
    AVAILABLE = 1
    UNAVAILABLE = 0

WASHABLE_ITEM_TYPES = [
    ITEM_TYPE.TOP
]
