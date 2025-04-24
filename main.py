# main.py
import db.db_client as db
from flask import Flask, render_template, redirect, request, send_from_directory, url_for, jsonify
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
import os
from models.constants import ITEM_TYPE
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vera-secret-key'  # Replace for prod
app.config['UPLOAD_FOLDER'] = 'wardrobe'
DB_NAME = 'wardrobe.db'

# WTForms Form
class UploadForm(FlaskForm):
    name = StringField("Item Name", validators=[DataRequired()])
    item_type = SelectField("Type", choices=[])  # Initialize with an empty list
    description = StringField("Description", validators=[DataRequired()])
    tags = StringField("Tags (comma-separated)")
    image = FileField("Image", validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    nfc_tag_id = StringField("NFC Tag ID")
    fit = StringField("Fit")
    aesthetic = StringField("Aesthetic")
    tone = StringField("Tone")
    layer = StringField("Layer")
    season = StringField("Season")
    color = StringField("Color")
    pattern_style = StringField("Pattern Style")
    material = StringField("Material")
    gender_expression = StringField("Gender Expression")
    formality = StringField("Formality")
    use_case = StringField("Use Case")
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
            self.fit.data = obj.fit
            self.aesthetic.data = obj.aesthetic
            self.tone.data = obj.tone
            self.layer.data = obj.layer
            self.season.data = obj.season
            self.color.data = obj.color
            self.pattern_style.data = obj.pattern_style
            self.material.data = obj.material
            self.gender_expression.data = obj.gender_expression
            self.formality.data = obj.formality
            self.use_case.data = obj.use_case

@app.route("/upload", methods=["GET", "POST"])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        # Clean up the tags input
        tags = ",".join(tag.strip() for tag in form.tags.data.split(",") if tag.strip())

        filename = secure_filename(form.image.data.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        form.image.data.save(save_path)
        image_url = url_for('wardrobe_file', filename=filename)

        db.add_item(
            name=form.name.data,
            item_type=form.item_type.data,
            description=form.description.data,
            tags=tags,
            image_path=image_url,
            nfc_tag_id=form.nfc_tag_id.data,
            fit=form.fit.data,
            aesthetic=form.aesthetic.data,
            tone=form.tone.data,
            layer=form.layer.data,
            season=form.season.data,
            color=form.color.data,
            pattern_style=form.pattern_style.data,
            material=form.material.data,
            gender_expression=form.gender_expression.data,
            formality=form.formality.data,
            use_case=form.use_case.data
        )
        return redirect(url_for("browse"))
    return render_template("upload.html", form=form, edit_item=False)

@app.route("/edit/<string:item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    item = db.get_item(item_id)
    if not item:
        return redirect(url_for("browse"))

    if request.method == "POST":
        form = UploadForm()
        if form.validate_on_submit():
            tags = ",".join(tag.strip() for tag in form.tags.data.split(",") if tag.strip())

            if form.image.data:
                filename = secure_filename(form.image.data.filename)
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                form.image.data.save(save_path)
                image_url = url_for('wardrobe_file', filename=filename)
            else:
                image_url = item.image_path

            db.update_item(
                item_id=item_id,
                name=form.name.data,
                item_type=form.item_type.data,
                description=form.description.data,
                tags=tags,  # Save cleaned tags
                image_path=image_url,
                nfc_tag_id=form.nfc_tag_id.data,
                fit=form.fit.data,
                aesthetic=form.aesthetic.data,
                tone=form.tone.data,
                layer=form.layer.data,
                season=form.season.data,
                color=form.color.data,
                pattern_style=form.pattern_style.data,
                material=form.material.data,
                gender_expression=form.gender_expression.data,
                formality=form.formality.data,
                use_case=form.use_case.data
            )
            return redirect(url_for("browse"))
    else:
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

@app.route("/database", methods=["GET", "POST"])
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

@app.route('/analyze_image', methods=['POST'])
def analyze_image():
    file = request.files.get('image')
    if not file:
        return jsonify({'error': 'No image provided'}), 400

    # Load the image (e.g., using PIL or OpenCV)
    from PIL import Image
    image = Image.open(file.stream)

    # Analyze the image using your AI model (replace with actual logic)
    analysis_results = analyze_image_with_ai(image)

    return jsonify(analysis_results)

def analyze_image_with_ai(image):
    # Example: Dummy analysis logic (replace with your AI model's predictions)
    return {
        'name': 'Predicted Name',
        'item_type': 'Predicted Type',
        'description': 'Predicted Description',
        'tags': 'tag1, tag2, tag3',
        'fit': 'Predicted Fit',
        'aesthetic': 'Predicted Aesthetic',
        'tone': 'Predicted Tone',
        'layer': 'Predicted Layer',
        'season': 'Predicted Season',
        'color': 'Predicted Color',
        'pattern_style': 'Predicted Pattern Style',
        'material': 'Predicted Material',
        'gender_expression': 'Predicted Gender Expression',
        'formality': 'Predicted Formality',
        'use_case': 'Predicted Use Case'
    }

if __name__ == "__main__":
    db.init_db()
    app.run(host="0.0.0.0", port=5050, debug=True)
