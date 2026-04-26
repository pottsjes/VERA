from flask import (
    Blueprint,
    render_template,
    request,
)
from app.db.db_client import get_items_by_type, list_items
from app.models.constants import ITEM_TYPE

bp = Blueprint('browse', __name__)

@bp.route("/")
@bp.route("/browse", methods=["GET"])
def browse():
    filter_type = request.args.get("filter_type")
    if filter_type:
        items = get_items_by_type(filter_type)
    else:
        items = list_items()

    return render_template("browse.html", items=items, filter_type=filter_type, ITEM_TYPE=ITEM_TYPE)
