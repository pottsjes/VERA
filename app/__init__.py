from flask import Flask
from app.routes import (
    upload,
    edit,
    browse,
    database,
    analyze,
    logs,
    wardrobe,
)

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'vera-secret-key'  # Replace for prod

    # Import and register blueprints
    app.register_blueprint(upload.bp)
    app.register_blueprint(edit.bp)
    app.register_blueprint(browse.bp)
    app.register_blueprint(database.bp)
    app.register_blueprint(analyze.bp)
    app.register_blueprint(logs.bp)
    app.register_blueprint(wardrobe.bp)

    return app