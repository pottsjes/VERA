import sqlite3
from flask import (
    Blueprint,
    jsonify,
    render_template,
    request,
)
from app.forms.upload_form import UploadForm
from app.utils.image_utils import save_image
from db.db_client import get_item, update_item
from models.constants import DB_NAME

bp = Blueprint('database', __name__, url_prefix='/database')

@bp.route("/", methods=["GET", "POST"])
def database():
    if request.method == "POST":
        data = request.get_json()
        query = data.get("query")
        results = {"columns": [], "rows": []}
        error = None

        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                if query.strip().lower().startswith("select"):
                    results["columns"] = [desc[0] for desc in cursor.description]
                    results["rows"] = cursor.fetchall()
                else:
                    conn.commit()
        except sqlite3.Error as e:
            error = str(e)

        if error:
            return jsonify({"error": error}), 400
        return jsonify(results)

    # For GET requests, render the query editor
    return render_template("database.html")