from datetime import datetime
import os
from app.models.constants import DATETIME_FORMAT

def save_failed_output(prompt_content):
    """Save failed AI prompt content to disk for manual inspection."""
    failed_dir = "failed_ai_responses"
    os.makedirs(failed_dir, exist_ok=True)

    timestamp = datetime.now().strftime(DATETIME_FORMAT)
    filename = os.path.join(failed_dir, f"failed_response_{timestamp}.txt")

    # Flatten prompt_content nicely
    if isinstance(prompt_content, list):
        content_text = "\n\n".join(
            f"{block.get('type', block.get('role'))}: {block.get('text', block.get('content', ''))}"
            for block in prompt_content
        )
    else:
        content_text = str(prompt_content)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content_text)
