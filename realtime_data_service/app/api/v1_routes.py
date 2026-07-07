from flask import Blueprint, jsonify

v1_bp = Blueprint('v1', __name__)

@v1_bp.route('/health')
def health_check():
    return jsonify({"status": "ok", "service": "realtime_data_service"})
