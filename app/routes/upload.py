from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for
)
from app.forms.upload_form import UploadForm
from app.utils.image_utils import save_image
from app.db.db_client import add_item

bp = Blueprint('upload', __name__, url_prefix='/upload')

@bp.route("/", methods=["GET", "POST"])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        tags = ",".join(tag.strip() for tag in form.tags.data.split(",") if tag.strip())
        image_url = save_image(form.image.data)

        add_item(
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
        return redirect(url_for("browse.browse"))
    return render_template("upload.html", form=form, edit_item=False)