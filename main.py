import db.db_client as db

db.init_db()
print(db.list_items())