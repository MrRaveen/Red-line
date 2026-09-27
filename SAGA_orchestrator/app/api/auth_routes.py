from SAGA_orchestrator.app.models.TokenBlocklist import TokenBlocklist
from SAGA_orchestrator.app.services.auth_service import check_user
from SAGA_orchestrator.app.services.auth_service import create_user
from flask import Blueprint, jsonify, request

from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)

auth_routes_bp = Blueprint('auth_routes_bp', __name__)

@auth_routes_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json() or {}
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
        email = data.get("email", "").strip()
        if not username or not password:
            return jsonify({"status": "failed", "message": "username and password required", "data": {}}), 400
        uid, err = create_user(username, email, password)
        if err:
            return jsonify({"status": "failed", "message": err, "data": {}}), 409
        return jsonify({"status": "success", "message": "Account created", "data": {"userID": username}}), 201
    except Exception as e:
        return jsonify({"status": "failed", "message": "unknown error occured", "data": {}}), 500

@auth_routes_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json() or {}
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()
        if not email or not password:
            return jsonify({"status": "failed", "message": "enter credentials", "data": {}}), 400
        output = check_user(email, password)
        if not output:
            return jsonify({"status": "failed", "message": "unknown error occured", "data": {}}), 401
        return jsonify(output), 200
    except Exception as e:
        return jsonify({"status": "failed", "message": "unknown error occured", "data": str(e)}), 500


@auth_routes_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)
        return jsonify({"status": "success", "message": "token refreshed", "data": {"access_token": access_token}}), 200
    except Exception as e:
        return jsonify({"status": "failed", "message": "unknown error occured", "data": {}}), 500

@auth_routes_bp.route('/logout', methods=['DELETE'])
@jwt_required(verify_type=False) 
def logout():
    try:
        token = get_jwt()
        jti = token["jti"]
        TokenBlocklist(jti=jti).save()
        return jsonify({"status": "success", "message": "token revoked", "data": {}}), 200
    except Exception as e:
        return jsonify({"status": "failed", "message": "unknown error occured", "data": {}}), 500


@auth_routes_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    try:
        identity = get_jwt_identity()
        return jsonify({"status": "success", "message": "You have access!", "data": {"user_id": identity}}), 200
    except Exception as e:
        return jsonify({"status": "failed", "message": "unknown error occured", "data": {}}), 500


