import os
import io
import uuid
from PIL import Image

GCS_BUCKET = os.environ.get("GCS_BUCKET", "")


def compress_image(image_bytes: bytes, size=(512, 512), quality=70) -> bytes:
    img = Image.open(io.BytesIO(image_bytes)).resize(size)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality)
    return buf.getvalue()


def upload_to_gcs(image_bytes: bytes, filename: str) -> str:
    """Upload image bytes to GCS and return the public URL."""
    if not GCS_BUCKET:
        # Fall back to local storage
        return _save_local(image_bytes, filename)

    from google.cloud import storage
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(f"wardrobe/{filename}")
    blob.upload_from_string(image_bytes, content_type="image/jpeg")
    return f"https://storage.googleapis.com/{GCS_BUCKET}/wardrobe/{filename}"


def _save_local(image_bytes: bytes, filename: str) -> str:
    """Save locally as fallback when no GCS bucket configured."""
    wardrobe_dir = os.path.join(os.path.dirname(__file__), "..", "wardrobe")
    os.makedirs(wardrobe_dir, exist_ok=True)
    path = os.path.join(wardrobe_dir, filename)
    with open(path, "wb") as f:
        f.write(image_bytes)
    return f"/wardrobe/{filename}"


def process_and_upload(image_bytes: bytes, original_filename: str) -> str:
    """Compress image and upload to storage. Returns URL."""
    ext = os.path.splitext(original_filename)[1] or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    compressed = compress_image(image_bytes)
    return upload_to_gcs(compressed, filename)
