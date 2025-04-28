# main.py
import base64
import io
import json
import re
from openai import OpenAI
import db.db_client as db
from flask import (
    Flask,
    render_template,
    redirect,
    request,
    send_from_directory,
    url_for,
    jsonify
)
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
import os
from models.constants import (
    ITEM_TYPE,
    API_REQUIRED_COLUMNS,
    OPEN_AI_KEY,
    IMAGE_CLASSIFICATION_PROMPT,
    REFORMAT_JSON_PROMPT,
    MISSING_FIELDS_PROMPT,
    MAX_AI_TRIES,
)
import sqlite3
from PIL import Image

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

def compress_image(input_image, size=(512, 512), quality=70):
    image = Image.open(input_image)
    image = image.resize(size)
    output = io.BytesIO()
    image.save(output, format="JPEG", quality=quality)
    output.seek(0)
    return Image.open(output)

def save_image(image, compress=False):
    filename = secure_filename(image.filename)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image = compress_image(image) if compress else image
    image.save(save_path, format="JPEG")
    return url_for('wardrobe_file', filename=filename)

@app.route("/upload", methods=["GET", "POST"])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        # Clean up the tags input
        tags = ",".join(tag.strip() for tag in form.tags.data.split(",") if tag.strip())

        image_url = save_image(form.image.data)

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
                image_url = save_image(form.image.data)
            else:
                image_url = item.image_path

            db.update_item(
                item_id=item_id,
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
    analysis_results = analyze_image_with_ai(file)
    return jsonify(analysis_results)

def analyze_image_with_ai(image):
    compressed_image = compress_image(image)
    output = io.BytesIO()
    compressed_image.save(output, format="JPEG")
    output.seek(0)
    b64_image = base64.b64encode(output.getvalue()).decode("utf-8")

    initial_prompt = [
        {"type": "input_text", "text": IMAGE_CLASSIFICATION_PROMPT},
        {"type": "input_image", "image_url": f"data:image/jpeg;base64,{b64_image}"},
    ]

    return prompt_ai(initial_prompt, retry_count=1)

def prompt_ai(prompt_content, retry_count):
    if retry_count > MAX_AI_TRIES:
        raise Exception("Max retries exceeded for AI response processing.")

    client = OpenAI(api_key=OPEN_AI_KEY)

    # Determine if this is initial image call or a text reformat call
    if retry_count == 1:  # initial classification request
        response = client.responses.create(
            model="gpt-4o-mini",
            instructions="",
            input=[{"role": "user", "content": prompt_content}]
        )
        text_output = response.output_text
    else:  # fallback reformat request
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=prompt_content,
            temperature=0.2,
        )
        text_output = response.choices[0].message.content

    try:
        data = extract_json_from_text(text_output)
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON decoding error: {e}")
        print(f"🔄 Attempting reformat due to invalid JSON structure (retry {retry_count + 1})...")
        reformat_prompt = [
            {"role": "system", "content": REFORMAT_JSON_PROMPT},
            {"role": "user", "content": text_output}
        ]
        return prompt_ai(reformat_prompt, retry_count + 1)
    except ValueError as e:
        print(f"⚠️ Missing required fields error: {e}")
        print(f"🔄 Attempting reformat due to incomplete fields (retry {retry_count + 1})...")
        reformat_prompt = [
            {"role": "system", "content": MISSING_FIELDS_PROMPT},
            {"role": "user", "content": f"Fields required: {API_REQUIRED_COLUMNS}\n\n{text_output}"}
        ]
        return prompt_ai(reformat_prompt, retry_count + 1)

    return data

def extract_json_from_text(text_output):
    text_output = text_output.strip()
    try:
        data = json.loads(text_output)
    except json.JSONDecodeError as e:
        if "```json" in text_output:
            match = re.search(r'```json(.*?)```', text_output, re.DOTALL)
            if match:
                text_output = match.group(1).strip()
                data = json.loads(text_output)
        else:
            raise
    
    missing_fields = [field for field in API_REQUIRED_COLUMNS if field not in data]
    if missing_fields:
        raise ValueError(f"Missing required fields: {missing_fields}")

    return data

if __name__ == "__main__":
    db.init_db()
    app.run(host="0.0.0.0", port=5050, debug=True)
