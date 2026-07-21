from flask import Blueprint, jsonify, request
import asyncio
from app.services.agent_service import AgentService

v1_bp = Blueprint('v1', __name__)

@v1_bp.route('/health')
def health_check():
    return jsonify({"status": "ok", "service": "prompt_injection_attack"})

@v1_bp.route('/test-attack', methods=['POST'])
def test_attack():
    data = request.get_json() or {}
    target_url = data.get("target_url")
    
    if not target_url:
        return jsonify({"status": "error", "message": "target_url is required"}), 400

    agent = AgentService()
    try:
        # Run the async agent loop in the synchronous Flask view
        result = asyncio.run(agent.get_response(target_url))
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
