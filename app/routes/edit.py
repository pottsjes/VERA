from flask import (
    Blueprint,
    render_template,
    redirect,
    request,
    url_for
)
from app.forms.upload_form import UploadForm
from app.utils.image_utils import save_image
from app.db.db_client import get_item, update_item

bp = Blueprint('edit', __name__, url_prefix='/edit/<string:item_id>')

@bp.route("/", methods=["GET", "POST"])
def edit_item(item_id):
    item = get_item(item_id)
    if not item:
        return redirect(url_for("browse.browse"))

    if request.method == "POST":
        form = UploadForm()
        if form.validate_on_submit():
            tags = ",".join(tag.strip() for tag in form.tags.data.split(",") if tag.strip())

            if form.image.data:
                image_url = save_image(form.image.data)
            else:
                image_url = item.image_path

            update_item(
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
            return redirect(url_for("browse.browse"))
    else:
        # Tags are stored as a list on the item but the form uses a comma-separated string
        if isinstance(item.tags, list):
            item.tags = ", ".join(item.tags)
        form = UploadForm(obj=item)

    return render_template("upload.html", form=form, edit_mode=True)