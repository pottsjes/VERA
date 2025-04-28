from enum import Enum

class ITEM_TYPE(Enum):
    TOP = "Top"
    BOTTOM = "Bottom"
    ACCESSORY = "Accessory"
    OUTER = "Outer"
    SHOE = "Shoe"
    
class ITEM_STATUS(Enum):
    AVAILABLE = 1
    UNAVAILABLE = 0

WASHABLE_ITEM_TYPES = [
    ITEM_TYPE.TOP
]

WARDROBE_FOLDER = 'wardrobe'
DB_NAME = 'wardrobe.db'
DATABASE_COLUMNS = [
    "id",
    "name",
    "item_type",
    "description",
    "tags",
    "image_path",
    "available",
    "last_used",
    "nfc_tag_id",
    "fit",
    "aesthetic",
    "tone",
    "layer",
    "season",
    "color",
    "pattern_style",
    "material",
    "gender_expression",
    "formality",
    "use_case"
]

API_REQUIRED_COLUMNS = [
    "name", "item_type", "description", "tags", "fit", "aesthetic", 
    "tone", "layer", "season", "color", "pattern_style", "material", 
    "gender_expression", "formality", "use_case"
]

OPEN_AI_KEY = "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"
MAX_AI_TRIES = 3
IMAGE_CLASSIFICATION_PROMPT = """You are a fashion wardrobe assistant.
Analyze the provided clothing image and return a well-formatted JSON object for wardrobe database management.
Populate the following fields precisely and consistently:
name: A short descriptive name for the item.
item_type: One of the following options (in ALL CAPS): TOP, BOTTOM, OUTER, SHOE, ACCESSORY.
description: A brief (1–2 sentences) description highlighting key features.
tags: A list of 3–6 relevant keywords about style, usage, or materials.
fit: The item's fit style (e.g., "Slim", "Regular", "Oversized", "Baggy").
aesthetic: The general aesthetic (e.g., "Sporty", "Minimalist", "Grunge", "Bohemian", "Y2K").
tone: The mood or brightness of the color palette (e.g., "Neutral", "Vibrant", "Earthy", "Pastel", "Dark").
layer: How the item is typically worn relative to others. Choose from: Base, Mid, Outer, Accessory.
season: Best suited season(s) (e.g., "Summer", "Fall/Winter", "All Season").
color: The primary, dominant color. Choose one main color (compound descriptors like "Rainbow" acceptable if appropriate).
pattern_style: The pattern style (e.g., "Solid", "Plaid", "Striped", "Graphic", "Floral").
material: Main material or blend (e.g., "Cotton", "Polyester", "Denim", "Leather").
gender_expression: Expected gender presentation (e.g., "Masculine", "Feminine", "Unisex").
formality: General formality level (e.g., "Casual", "Business Casual", "Formal", "Streetwear").
use_case: Common usage scenarios (e.g., "Everyday Wear", "Work", "Gym", "Date Night", "Outdoor Activities").

Output format- Respond only with a single, valid JSON object.
Do not include explanations, commentary, or Markdown formatting (no ```json blocks)."""

REFORMAT_JSON_PROMPT = """You are a strict formatter. The user attempted to parse the 
following text as JSON but failed. Please fix any structural errors (such as missing commas,
 brackets, or quotes) and output valid, well-formatted JSON only."""

MISSING_FIELDS_PROMPT = """You are a wardrobe database assistant. The following JSON is
 structurally correct but missing required fields. Please fill in ALL required fields 
 based on the provided wardrobe schema, even if you have to make reasonable assumptions."""