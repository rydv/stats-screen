from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from validation.validators import RuleSheetValidator

rule_sheet_bp = Blueprint('rule_sheet', __name__)

UPLOAD_FOLDER = '/opt/appl/aistore/portal/recon_pulse_mm/controllers/matching_matrix_controller/files/'
ALLOWED_EXTENSIONS = {'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@rule_sheet_bp.route('/validate-rule-sheet', methods=['POST'])
def validate_rule_sheet():
    if 'file' not in request.files:
        return jsonify({
            'status': False,
            'message': 'No file uploaded',
            'validation_results': None
        }), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({
            'status': False,
            'message': 'No file selected',
            'validation_results': None
        }), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        validator = RuleSheetValidator(file_path)
        is_valid, validation_results = validator.validate()

        os.remove(file_path)  # Clean up uploaded file

        return jsonify({
            'status': is_valid,
            'message': 'Validation completed',
            'validation_results': validation_results
        })

    return jsonify({
        'status': False,
        'message': 'Invalid file format',
        'validation_results': None
    }), 400
