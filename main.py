# main.py
import db.db_client as db
from flask import Flask, render_template, redirect, request, send_from_directory, url_for
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
import os
from models.constants import ITEM_TYPE

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vera-secret-key'  # Replace for prod
app.config['UPLOAD_FOLDER'] = 'wardrobe'

# WTForms Form
class UploadForm(FlaskForm):
    name = StringField("Item Name", validators=[DataRequired()])
    item_type = SelectField("Type", choices=[])  # Initialize with an empty list
    description = StringField("Description", validators=[DataRequired()])
    tags = StringField("Tags (comma-separated)")
    image = FileField("Image", validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    nfc_tag_id = StringField("NFC Tag ID")
    submit = SubmitField("Add Item")

    def __init__(self, *args, **kwargs):
        # Allow passing an object to prepopulate the form
        obj = kwargs.pop('obj', None)
        super().__init__(*args, **kwargs)
        # Dynamically set choices using the ITEM_TYPE enum
        self.item_type.choices = [(item_type.value, item_type.name.capitalize()) for item_type in ITEM_TYPE]
        if obj:
            self.name.data = obj.name
            self.item_type.data = obj.item_type
            self.description.data = obj.description
            self.tags.data = ",".join(obj.tags) if obj.tags else ""
            self.nfc_tag_id.data = obj.nfc_tag_id

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

        db.add_item(
            name=form.name.data,
            item_type=form.item_type.data,
            description=form.description.data,
            tags=form.tags.data,
            image_path=image_url,
            nfc_tag_id=form.nfc_tag_id.data
        )
        return redirect(url_for("browse"))
    return render_template("upload.html", form=form)

@app.route("/edit/<string:item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    item = db.get_item(item_id)  # Fetch the item from the database
    if not item:
        return redirect(url_for("browse"))  # Redirect if the item doesn't exist

    if request.method == "POST":
        # Instantiate the form without the `obj` to process the submitted data
        form = UploadForm()
        if form.validate_on_submit():
            # Handle the image upload
            if form.image.data:
                filename = secure_filename(form.image.data.filename)
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                form.image.data.save(save_path)
                image_url = url_for('wardrobe_file', filename=filename)
            else:
                image_url = item.image_path  # Keep the existing image path if no new image is uploaded

            # Update the item in the database
            db.update_item(
                item_id=item_id,
                name=form.name.data,  # Get the updated name from the form
                item_type=form.item_type.data,  # Get the updated item type from the form
                description=form.description.data,  # Get the updated description from the form
                tags=form.tags.data,  # Get the updated tags from the form
                image_path=image_url,  # Use the updated or existing image path
                nfc_tag_id=form.nfc_tag_id.data  # Get the updated NFC tag ID from the form
            )
            return redirect(url_for("browse"))
    else:
        # Instantiate the form with the `obj` to prepopulate the fields on a GET request
        form = UploadForm(obj=item)

    return render_template("upload.html", form=form, edit_mode=True)

@app.route("/")
@app.route("/browse", methods=["GET"])
def browse():
    filter_type = request.args.get("filter_type")  # Get the filter from query parameters
    if filter_type:
        items = db.get_items_by_type(filter_type)  # Fetch filtered items from the database
    else:
        items = db.list_items()  # Fetch all items if no filter is applied

    return render_template("browse.html", items=items, filter_type=filter_type, ITEM_TYPE=ITEM_TYPE)

@app.route('/wardrobe/<filename>')
def wardrobe_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    db.init_db()
    app.run(host="0.0.0.0", port=5050, debug=True)
