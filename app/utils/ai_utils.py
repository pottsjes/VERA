import base64
import io
import json
import os
import re
from app.utils.image_utils import compress_image
from app.utils.log_utils import save_failed_output
from app.models.constants import API_REQUIRED_COLUMNS, IMAGE_CLASSIFICATION_PROMPT, MAX_AI_TRIES, MISSING_FIELDS_PROMPT, REFORMAT_JSON_PROMPT

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")


def analyze_image_with_ai(image):
    if not ANTHROPIC_API_KEY:
        return {"error": "AI analysis unavailable — no API key configured."}

    try:
        import anthropic
    except ImportError:
        return {"error": "AI analysis unavailable — anthropic package not installed."}

    compressed_image = compress_image(image)
    output = io.BytesIO()
    compressed_image.save(output, format="JPEG")
    output.seek(0)
    b64_image = base64.b64encode(output.getvalue()).decode("utf-8")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64_image}},
                {"type": "text", "text": IMAGE_CLASSIFICATION_PROMPT},
            ],
        }],
    )
    text_output = response.content[0].text

    try:
        data = extract_json_from_text(text_output)
    except (json.JSONDecodeError, ValueError) as e:
        save_failed_output([{"type": "text", "text": text_output}])
        return {"error": f"Failed to parse AI response: {e}"}

    return data


def extract_json_from_text(text_output):
    text_output = text_output.strip()
    try:
        data = json.loads(text_output)
    except json.JSONDecodeError:
        if "```json" in text_output:
            match = re.search(r'```json(.*?)```', text_output, re.DOTALL)
            if match:
                text_output = match.group(1).strip()
                data = json.loads(text_output)
            else:
                raise
        else:
            raise

    missing_fields = [field for field in API_REQUIRED_COLUMNS if field not in data]
    if missing_fields:
        raise ValueError(f"Missing required fields: {missing_fields}")

    return data
