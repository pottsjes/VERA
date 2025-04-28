import os
import io
from PIL import Image
from werkzeug.utils import secure_filename
from flask import url_for

def compress_image(input_image, size=(512, 512), quality=70):
    image = Image.open(input_image)
    image = image.resize(size)
    output = io.BytesIO()
    image.save(output, format="JPEG", quality=quality)
    output.seek(0)
    return Image.open(output)

def save_image(image, compress=False, upload_folder="wardrobe"):
    filename = secure_filename(image.filename)
    save_path = os.path.join(upload_folder, filename)
    image = compress_image(image) if compress else image
    image.save(save_path, format="JPEG")
    return url_for('wardrobe.wardrobe_file', filename=filename)