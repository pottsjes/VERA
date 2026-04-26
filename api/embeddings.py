import os
from typing import List, Optional
from api.models import Item

GCP_PROJECT = os.environ.get("GCP_PROJECT", "vera-494519")
GCP_REGION = os.environ.get("GCP_REGION", "us-central1")


def item_to_text(item: Item) -> str:
    """Convert item attributes into a text string for embedding."""
    parts = [item.name]
    if item.description:
        parts.append(item.description)
    for attr in [item.item_type, item.aesthetic, item.tone, item.fit,
                 item.color, item.pattern_style, item.material, item.layer,
                 item.season, item.formality, item.gender_expression, item.use_case]:
        if attr:
            parts.append(attr)
    if item.tags:
        parts.append(item.tags.replace(",", ", "))
    return ". ".join(parts)


async def generate_embedding(text: str) -> Optional[List[float]]:
    """Generate a 768-dim embedding using Vertex AI text-embedding-004."""
    try:
        from vertexai.language_models import TextEmbeddingModel
        import vertexai

        vertexai.init(project=GCP_PROJECT, location=GCP_REGION)
        model = TextEmbeddingModel.from_pretrained("text-embedding-004")
        embeddings = model.get_embeddings([text])
        return embeddings[0].values
    except Exception as e:
        print(f"WARNING: Embedding generation failed: {e}")
        return None


async def generate_item_embedding(item: Item) -> Optional[List[float]]:
    """Generate embedding for a wardrobe item."""
    text = item_to_text(item)
    return await generate_embedding(text)
