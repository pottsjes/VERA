from flask import (
    Blueprint,
    jsonify,
    request,
)

bp = Blueprint('analyze_image', __name__, url_prefix='/analyze_image')

@bp.route('/', methods=['POST'])
def analyze_image():
    file = request.files.get('image')
    if not file:
        return jsonify({'error': 'No image provided'}), 400
    analysis_results = analyze_image_with_ai(file)
    return jsonify(analysis_results)