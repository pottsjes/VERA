# main.py
from flask import Flask, render_template, redirect, request, send_from_directory, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vera-secret-key'  # Replace for prod
app.config['UPLOAD_FOLDER'] = 'wardrobe'

ITEM_TYPES = ["Top", "Bottom", "Outerwear", "Shoes"]

# WTForms Form
class UploadForm(FlaskForm):
    name = StringField("Item Name", validators=[DataRequired()])
    item_type = SelectField("Type", choices=[(t, t) for t in ITEM_TYPES])
    image = FileField("Image", validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    submit = SubmitField("Add Item")

# Fake in-memory store
items = []

@app.route("/upload", methods=["GET", "POST"])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        filename = secure_filename(form.image.data.filename)
        # Where to save the file (on disk)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        form.image.data.save(save_path)
        # Where to serve the file (in the browser)
        image_url = url_for('wardrobe_file', filename=filename)

        items.append({
            "name": form.name.data,
            "type": form.item_type.data,
            "image_path": image_url
        })
        return redirect(url_for("browse"))
    return render_template("upload.html", form=form)

@app.route("/")
@app.route("/browse")
def browse():
    return render_template("browse.html", items=items)

@app.route('/wardrobe/<filename>')
def wardrobe_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
