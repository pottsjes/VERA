from typing import List, Optional

from models.constants import ITEM_TYPE

class Item():
    def __init__(self, name: str,
                 item_type: ITEM_TYPE,
                 description: str = "",
                 tags: Optional[List[str]] = None,
                 image_path: str = "",
                 available: bool = True,
                 last_used: Optional[str] = None,
                 nfc_tag_id: Optional[str] = None,
                 item_id: Optional[int] = None,
                ):
        self.name = name
        self.item_type = item_type
        self.description = description
        self.tags = tags or []
        self.image_path = image_path
        self.available = available
        self.last_used = last_used
        self.nfc_tag_id = nfc_tag_id
        self.item_id = item_id
