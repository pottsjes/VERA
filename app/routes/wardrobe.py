import os
from flask import (
    Blueprint,
    send_from_directory,
)
from app.models.constants import WARDROBE_FOLDER

# Resolve wardrobe folder against the project root so it works regardless of CWD
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_WARDROBE_DIR = os.path.join(_PROJECT_ROOT, WARDROBE_FOLDER)

bp = Blueprint('wardrobe', __name__, url_prefix='/wardrobe')

@bp.route('/<filename>')
def wardrobe_file(filename):
    return send_from_directory(_WARDROBE_DIR, filename)