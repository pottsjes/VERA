from flask import (
    Blueprint,
    send_from_directory,
)
from models.constants import WARDROBE_FOLDER

bp = Blueprint('wardrobe', __name__, url_prefix='/wardrobe/<filename>')

@bp.route('/')
def wardrobe_file(filename):
    return send_from_directory(WARDROBE_FOLDER, filename)