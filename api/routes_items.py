from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from api.database import get_db
from api.models import Item
from api.schemas import ItemCreate, ItemResponse, ItemUpdate

router = APIRouter(prefix="/api/items", tags=["items"])


def _tags_to_str(tags: List[str]) -> str:
    return ",".join(tags)


def _item_to_response(item: Item) -> ItemResponse:
    return ItemResponse(
        id=item.id,
        name=item.name,
        item_type=item.item_type,
        description=item.description,
        tags=item.tags.split(",") if item.tags else [],
        image_path=item.image_path,
        available=item.available,
        last_used=item.last_used,
        nfc_tag_id=item.nfc_tag_id,
        fit=item.fit,
        aesthetic=item.aesthetic,
        tone=item.tone,
        layer=item.layer,
        season=item.season,
        color=item.color,
        pattern_style=item.pattern_style,
        material=item.material,
        gender_expression=item.gender_expression,
        formality=item.formality,
        use_case=item.use_case,
    )


@router.get("/", response_model=List[ItemResponse])
async def list_items(
    item_type: Optional[str] = None,
    available_only: bool = False,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Item)
    if item_type:
        stmt = stmt.where(Item.item_type == item_type)
    if available_only:
        stmt = stmt.where(Item.available == True)
    result = await db.execute(stmt)
    return [_item_to_response(i) for i in result.scalars().all()]


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return _item_to_response(item)


@router.post("/", response_model=ItemResponse, status_code=201)
async def create_item(data: ItemCreate, db: AsyncSession = Depends(get_db)):
    item = Item(
        name=data.name,
        item_type=data.item_type.value,
        description=data.description,
        tags=_tags_to_str(data.tags),
        image_path=data.image_path,
        available=data.available,
        nfc_tag_id=data.nfc_tag_id,
        fit=data.fit,
        aesthetic=data.aesthetic,
        tone=data.tone,
        layer=data.layer,
        season=data.season,
        color=data.color,
        pattern_style=data.pattern_style,
        material=data.material,
        gender_expression=data.gender_expression,
        formality=data.formality,
        use_case=data.use_case,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return _item_to_response(item)


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, data: ItemUpdate, db: AsyncSession = Depends(get_db)):
    item = await db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.name = data.name
    item.item_type = data.item_type.value
    item.description = data.description
    item.tags = _tags_to_str(data.tags)
    item.image_path = data.image_path
    item.available = data.available
    item.nfc_tag_id = data.nfc_tag_id
    item.fit = data.fit
    item.aesthetic = data.aesthetic
    item.tone = data.tone
    item.layer = data.layer
    item.season = data.season
    item.color = data.color
    item.pattern_style = data.pattern_style
    item.material = data.material
    item.gender_expression = data.gender_expression
    item.formality = data.formality
    item.use_case = data.use_case
    await db.commit()
    await db.refresh(item)
    return _item_to_response(item)


@router.delete("/{item_id}", status_code=204)
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    await db.delete(item)
    await db.commit()


@router.post("/{item_id}/toggle-availability", response_model=ItemResponse)
async def toggle_availability(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.available = not item.available
    if not item.available:
        item.last_used = datetime.now()
    await db.commit()
    await db.refresh(item)
    return _item_to_response(item)
