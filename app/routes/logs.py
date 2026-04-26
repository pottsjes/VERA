import os
from flask import (
    Blueprint,
    jsonify,
    render_template,
    request,
)
from datetime import datetime
from app.models.constants import DATETIME_FORMAT

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
    log_files = []
    for f in os.listdir(logs_dir):
        if os.path.isfile(os.path.join(logs_dir, f)):
            # Extract datetime from the file name
            try:
                timestamp_str = f.split("_")[-1].split(".")[0]  # Extract the datetime part
                timestamp = datetime.strptime(timestamp_str, DATETIME_FORMAT)  # Parse it
            except (IndexError, ValueError):
                timestamp = None  # Handle files without a valid datetime

            log_files.append({
                "name": f,
                "timestamp": timestamp,
            })

    # Sort logs by timestamp (newest first)
    log_files.sort(key=lambda x: x["timestamp"] or datetime.min, reverse=True)

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
