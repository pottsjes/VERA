import json
import os
import re
from typing import List, Optional
import anthropic
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from api.database import get_db
from api.embeddings import generate_embedding, item_to_text
from api.models import Item

router = APIRouter(prefix="/api/recommend", tags=["recommend"])

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

OUTFIT_PROMPT = """You are V.E.R.A., a fashion stylist AI. The user wants an outfit matching this vibe:

"{vibe}"

Here are the candidate items from their wardrobe, grouped by category. Each item has an ID, name, and description.

{candidates}

Select ONE item per category to create a complete outfit. Not every category needs to be used — only pick items that fit the vibe. Return a JSON object with:
- "items": list of selected item IDs
- "reasoning": a short, conversational explanation of why this outfit works for the vibe (2-3 sentences)
- "styling_tips": one optional styling tip

Respond only with valid JSON. No markdown formatting."""


class RecommendRequest(BaseModel):
    vibe: str
    top_k: int = 5


class RecommendedItem(BaseModel):
    id: int
    name: str
    item_type: str
    image_path: str
    description: str


class RecommendResponse(BaseModel):
    vibe: str
    items: List[RecommendedItem]
    reasoning: str
    styling_tips: Optional[str] = None


def _format_candidates(items: List[Item]) -> str:
    by_type = {}
    for item in items:
        t = item.item_type or "Other"
        by_type.setdefault(t, []).append(item)

    sections = []
    for item_type, type_items in by_type.items():
        lines = [f"**{item_type}:**"]
        for item in type_items:
            desc = item_to_text(item)
            lines.append(f"  - ID {item.id}: {item.name} — {desc}")
        sections.append("\n".join(lines))
    return "\n\n".join(sections)


def _fallback_response(vibe: str, items: List[Item], reason: str) -> RecommendResponse:
    return RecommendResponse(
        vibe=vibe,
        items=[RecommendedItem(id=i.id, name=i.name, item_type=i.item_type,
                               image_path=i.image_path, description=i.description or "")
               for i in items[:6]],
        reasoning=reason,
    )


@router.post("/", response_model=RecommendResponse)
async def recommend_outfit(req: RecommendRequest, db: AsyncSession = Depends(get_db)):
    # 1. Embed the vibe prompt
    vibe_embedding = await generate_embedding(req.vibe)
    if not vibe_embedding:
        raise HTTPException(status_code=503, detail="Embedding service unavailable")

    # 2. Vector similarity search
    embedding_str = "[" + ",".join(str(v) for v in vibe_embedding) + "]"
    query = text("""
        SELECT * FROM items
        WHERE embedding IS NOT NULL AND available = true
        ORDER BY embedding <=> :embedding
        LIMIT :limit
    """)
    result = await db.execute(query, {"embedding": embedding_str, "limit": req.top_k * 5})
    candidates = result.fetchall()

    if not candidates:
        raise HTTPException(status_code=404, detail="No items with embeddings found. Upload some clothes first!")

    # Map rows to Item objects
    column_names = result.keys()
    candidate_items = []
    for row in candidates:
        item = Item(**{col: val for col, val in zip(column_names, row) if col != "embedding"})
        candidate_items.append(item)

    # 3. Ask Claude to assemble the outfit
    if not ANTHROPIC_API_KEY:
        return _fallback_response(req.vibe, candidate_items, "AI styling unavailable — showing closest matches by vibe.")

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        prompt = OUTFIT_PROMPT.format(vibe=req.vibe, candidates=_format_candidates(candidate_items))
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        text_out = response.content[0].text.strip()

        if "```json" in text_out:
            match = re.search(r'```json(.*?)```', text_out, re.DOTALL)
            if match:
                text_out = match.group(1).strip()

        result_data = json.loads(text_out)
        selected_ids = set(result_data.get("items", []))
        selected_items = [i for i in candidate_items if i.id in selected_ids]

        return RecommendResponse(
            vibe=req.vibe,
            items=[RecommendedItem(id=i.id, name=i.name, item_type=i.item_type,
                                   image_path=i.image_path, description=i.description or "")
                   for i in selected_items],
            reasoning=result_data.get("reasoning", ""),
            styling_tips=result_data.get("styling_tips"),
        )
    except Exception as e:
        return _fallback_response(req.vibe, candidate_items, f"AI styling failed ({e}) — showing closest matches by vibe.")
