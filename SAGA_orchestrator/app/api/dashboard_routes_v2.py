from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
import json
import time
import logging
from datetime import datetime
from flask import Blueprint, jsonify, request, Response, stream_with_context
from bson.objectid import ObjectId
from bson import json_util
from pymongo import MongoClient, DESCENDING, ASCENDING
from app.config import Config
from app.core.models.job import jobs_collection, including_jobs_collection, JobType
from app.models.Jobs import Jobs
from app.models.ExecutionLogs import JobLogs


dashboard_bp_v2 = Blueprint('dashboard_bp_v2', __name__)
@dashboard_bp_v2.route('/all_attacks',methods=['GET'])
@jwt_required()
def all_attacks():
    try:
        identity = get_jwt_identity()
        jobs = Jobs.objects(userID=identity)
        jobs_json = [json.loads(job.to_json()) for job in jobs]
        return jsonify({
            "status": "success",
            "message": "Jobs retrieved successfully",
            "data": jobs_json
        }), 200
    except Exception as e:
        logging.error(f"Error fetching jobs: {str(e)}")
        return jsonify({
            "status": "failed",
            "message": "An error occurred while fetching jobs",
            "data": str(e)
        }), 500

@dashboard_bp_v2.route('/get_execution_logs',methods=['GET'])
@jwt_required()
def get_execution_logs():
    try:
        identity = get_jwt_identity()
        logs = JobLogs.objects(userID=identity)
        logs_json = [json.loads(log.to_json()) for log in logs]
        return jsonify({
            "status": "success",
            "message": "Execution logs retrieved successfully",
            "data": logs_json
        }), 200
    except Exception as e:
        logging.error(f"Error fetching execution logs: {str(e)}")
        return jsonify({
            "status": "failed",
            "message": "An error occurred while fetching execution logs",
            "data": str(e)
        }), 500

