import base64
import io
import json
import os
import re
from fastapi import APIRouter, File, UploadFile
from PIL import Image
from api.constants import API_REQUIRED_COLUMNS, IMAGE_CLASSIFICATION_PROMPT

router = APIRouter(tags=["ai"])

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")


def _compress(image_bytes: bytes, size=(512, 512), quality=70) -> bytes:
    img = Image.open(io.BytesIO(image_bytes)).resize(size)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality)
    return buf.getvalue()


@router.post("/api/analyze-image")
async def analyze_image(image: UploadFile = File(...)):
    if not ANTHROPIC_API_KEY:
        return {"error": "AI analysis unavailable — no API key configured."}

    try:
        import anthropic
    except ImportError:
        return {"error": "AI analysis unavailable — anthropic package not installed."}

    raw = await image.read()
    compressed = _compress(raw)
    b64 = base64.b64encode(compressed).decode("utf-8")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}},
                {"type": "text", "text": IMAGE_CLASSIFICATION_PROMPT},
            ],
        }],
    )
    text = response.content[0].text

    try:
        text = text.strip()
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r'```json(.*?)```', text, re.DOTALL)
            if match:
                data = json.loads(match.group(1).strip())
            else:
                raise
        missing = [f for f in API_REQUIRED_COLUMNS if f not in data]
        if missing:
            return {"error": f"Missing fields: {missing}", "raw": text}
        return data
    except (json.JSONDecodeError, ValueError) as e:
        return {"error": f"Failed to parse AI response: {e}", "raw": text}
