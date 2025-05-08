# main.py
from app import create_app
import db.db_client as db

if __name__ == "__main__":
    db.init_db()
    app = create_app()
    app.run(host="0.0.0.0", port=5050, debug=True)
