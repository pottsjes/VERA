from enum import Enum
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, field_validator


class ItemType(str, Enum):
    TOP = "Top"
    BOTTOM = "Bottom"
    ACCESSORY = "Accessory"
    OUTER = "Outer"
    SHOE = "Shoe"


class ItemBase(BaseModel):
    name: str
    item_type: ItemType
    description: str = ""
    tags: List[str] = []
    image_path: str = ""
    available: bool = True
    nfc_tag_id: Optional[str] = None
    fit: str = ""
    aesthetic: str = ""
    tone: str = ""
    layer: str = ""
    season: str = ""
    color: str = ""
    pattern_style: str = ""
    material: str = ""
    gender_expression: str = ""
    formality: str = ""
    use_case: str = ""

    @field_validator("item_type", mode="before")
    @classmethod
    def normalize_item_type(cls, v):
        if isinstance(v, str):
            lookup = {t.value.lower(): t for t in ItemType}
            match = lookup.get(v.lower())
            if match:
                return match
        return v


class ItemCreate(ItemBase):
    pass


class ItemUpdate(ItemBase):
    pass


class ItemResponse(ItemBase):
    id: int
    last_used: Optional[datetime] = None

    model_config = {"from_attributes": True}
