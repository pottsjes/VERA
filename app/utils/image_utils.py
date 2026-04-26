import os
import io
from PIL import Image
from werkzeug.utils import secure_filename
from flask import url_for

WARDROBE_DIR = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")), "wardrobe")

def compress_image(input_image, size=(512, 512), quality=70):
    image = Image.open(input_image)
    image = image.resize(size)
    output = io.BytesIO()
    image.save(output, format="JPEG", quality=quality)
    output.seek(0)
    return Image.open(output)

def save_image(image, upload_folder=None):
    if upload_folder is None:
        upload_folder = WARDROBE_DIR
    os.makedirs(upload_folder, exist_ok=True)
    filename = secure_filename(image.filename)
    save_path = os.path.join(upload_folder, filename)
    pil_image = compress_image(image)
    pil_image.save(save_path, format="JPEG")
    return url_for('wardrobe.wardrobe_file', filename=filename)
