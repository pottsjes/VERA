from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from models.constants import ITEM_TYPE

class UploadForm(FlaskForm):
    name = StringField("Item Name", validators=[DataRequired()])
    item_type = SelectField("Type", choices=[])
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
        obj = kwargs.pop('obj', None)
        super().__init__(*args, **kwargs)
        self.item_type.choices = [(item_type.value, item_type.name.capitalize()) for item_type in ITEM_TYPE]
        if obj:
            self.populate_obj(obj)
