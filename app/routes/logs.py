import os
from flask import (
    Blueprint,
    jsonify,
    render_template,
    request,
)
from models.constants import WARDROBE_FOLDER

bp = Blueprint('logs', __name__, url_prefix='/logs')

@bp.route("/", methods=["GET", "POST"])
def logs():
    logs_dir = "failed_ai_responses"
    os.makedirs(logs_dir, exist_ok=True)

    # Handle deletion of a log file
    if request.method == "POST":
        action = request.form.get("action")
        filename = request.form.get("filename")
        if action == "delete" and filename:
            file_path = os.path.join(logs_dir, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                return jsonify({"success": True, "message": f"Deleted {filename}"}), 200
            else:
                return jsonify({"success": False, "message": "File not found"}), 404

    # Get all log files
    log_files = [
        {"name": f, "timestamp": os.path.getmtime(os.path.join(logs_dir, f))}
        for f in os.listdir(logs_dir) if os.path.isfile(os.path.join(logs_dir, f))
    ]

    # Sort logs by timestamp (newest first)
    log_files.sort(key=lambda x: x["timestamp"], reverse=True)

    # Handle filtering/sorting (optional)
    filter_query = request.args.get("filter", "").lower()
    if filter_query:
        log_files = [log for log in log_files if filter_query in log["name"].lower()]

    return render_template("logs.html", logs=log_files)

@bp.route("/<filename>")
def view_log(filename):
    logs_dir = "failed_ai_responses"
    file_path = os.path.join(logs_dir, filename)

    if not os.path.exists(file_path):
        return "Log file not found", 404

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    return render_template("view_log.html", filename=filename, content=content)
