import base64
import json
import os
import re
from fastapi import APIRouter, File, UploadFile
from api.constants import API_REQUIRED_COLUMNS, IMAGE_CLASSIFICATION_PROMPT
from api.storage import compress_image, process_and_upload

router = APIRouter(tags=["ai"])

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")


@router.post("/api/analyze-image")
async def analyze_image(image: UploadFile = File(...)):
    raw = await image.read()

    # Upload image to storage regardless of AI availability
    image_url = process_and_upload(raw, image.filename)

    if not ANTHROPIC_API_KEY:
        return {"image_path": image_url, "error": "AI analysis unavailable — no API key configured."}

    try:
        import anthropic
    except ImportError:
        return {"image_path": image_url, "error": "AI analysis unavailable — anthropic package not installed."}

    compressed = compress_image(raw)
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
            return {"image_path": image_url, "error": f"Missing fields: {missing}", "raw": text}
        data["image_path"] = image_url
        return data
    except (json.JSONDecodeError, ValueError) as e:
        return {"image_path": image_url, "error": f"Failed to parse AI response: {e}", "raw": text}
