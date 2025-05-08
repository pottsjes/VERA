import base64
import io
import json
import re
from app.utils.image_utils import compress_image
from app.utils.log_utils import save_failed_output
from models.constants import API_REQUIRED_COLUMNS, IMAGE_CLASSIFICATION_PROMPT, MAX_AI_TRIES, MISSING_FIELDS_PROMPT, OPEN_AI_KEY, REFORMAT_JSON_PROMPT
from openai import OpenAI


def analyze_image_with_ai(image):
    compressed_image = compress_image(image)
    output = io.BytesIO()
    compressed_image.save(output, format="JPEG")
    output.seek(0)
    b64_image = base64.b64encode(output.getvalue()).decode("utf-8")

    initial_prompt = [
        {"type": "input_text", "text": IMAGE_CLASSIFICATION_PROMPT},
        {"type": "input_image", "image_url": f"data:image/jpeg;base64,{b64_image}"},
    ]

    return prompt_ai(initial_prompt, retry_count=1)

def prompt_ai(prompt_content, retry_count):
    if retry_count > MAX_AI_TRIES:
        save_failed_output(prompt_content)
        return {"error": "Max retries exceeded for AI response processing."}

    client = OpenAI(api_key=OPEN_AI_KEY)

    # Determine if this is initial image call or a text reformat call
    if retry_count == 1:  # initial classification request
        response = client.responses.create(
            model="gpt-4o-mini",
            instructions="",
            input=[{"role": "user", "content": prompt_content}]
        )
        text_output = response.output_text
    else:  # fallback reformat request
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=prompt_content,
            temperature=0.2,
        )
        text_output = response.choices[0].message.content

    try:
        data = extract_json_from_text(text_output)
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON decoding error: {e}")
        print(f"🔄 Attempting reformat due to invalid JSON structure (retry {retry_count + 1})...")
        reformat_prompt = [
            {"role": "system", "content": REFORMAT_JSON_PROMPT},
            {"role": "user", "content": text_output}
        ]
        return prompt_ai(reformat_prompt, retry_count + 1)
    except ValueError as e:
        print(f"⚠️ Missing required fields error: {e}")
        print(f"🔄 Attempting reformat due to incomplete fields (retry {retry_count + 1})...")
        reformat_prompt = [
            {"role": "system", "content": MISSING_FIELDS_PROMPT},
            {"role": "user", "content": f"Fields required: {API_REQUIRED_COLUMNS}\n\n{text_output}"}
        ]
        return prompt_ai(reformat_prompt, retry_count + 1)

    return data

def extract_json_from_text(text_output):
    text_output = text_output.strip()
    try:
        data = json.loads(text_output)
    except json.JSONDecodeError as e:
        if "```json" in text_output:
            match = re.search(r'```json(.*?)```', text_output, re.DOTALL)
            if match:
                text_output = match.group(1).strip()
                data = json.loads(text_output)
        else:
            raise
    
    missing_fields = [field for field in API_REQUIRED_COLUMNS if field not in data]
    if missing_fields:
        raise ValueError(f"Missing required fields: {missing_fields}")

    return data
