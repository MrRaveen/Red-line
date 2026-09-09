import json
import time
import logging
from datetime import datetime
from flask import Blueprint, jsonify, request, Response, stream_with_context
from bson.objectid import ObjectId
from bson import json_util
from pymongo import MongoClient, DESCENDING, ASCENDING
from app.config import Config
from app.models.user import create_user, check_user
from app.core.models.job import jobs_collection, including_jobs_collection, JobType

dashboard_bp = Blueprint('dashboard', __name__)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Shared DB references (read-only views of attack-side collections)
# ------------------------------------------------------------------
client = MongoClient(Config.MONGO_URI)
db = client["redline_logs"]
execution_logs_col = db["execution_logs"]
summaries_col = db["summerriesAttacks"]
transaction_col = db["transaction_data"]


def _ser(doc):
    """Convert MongoDB document to JSON-serialisable dict."""
    if doc is None:
        return None
    doc = dict(doc)
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


def _user():
    """Get user identity from header or query param (no session needed)."""
    return request.headers.get("X-User-ID") or request.args.get("userID") or ""


# ==================================================================
# AUTH
# ==================================================================

@dashboard_bp.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    email = data.get("email", "").strip()
    if not username or not password:
        return jsonify({"error": "username and password required"}), 400
    uid, err = create_user(username, email, password)
    if err:
        return jsonify({"error": err}), 409
    return jsonify({"message": "Account created", "userID": username}), 201


@dashboard_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    user = check_user(username, password)
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    return jsonify({
        "message": "Login successful",
        "userID": username,
        "email": user.get("email", "")
    }), 200


# ==================================================================
# DASHBOARD STATS
# ==================================================================

@dashboard_bp.route('/stats', methods=['GET'])
def get_stats():
    uid = _user()
    q = {"userID": uid} if uid else {}

    total_jobs    = jobs_collection.count_documents(q)
    running_jobs  = jobs_collection.count_documents({**q, "job_status": "PROCESSING"})
    finished_jobs = jobs_collection.count_documents({**q, "job_status": "FINISHED"})

    summaries = list(summaries_col.find(q, {"number_of_breaches": 1}))
    total_breaches = sum(s.get("number_of_breaches", 0) for s in summaries)

    # Attack type distribution
    pipeline = [
        {"$match": q},
        {"$group": {"_id": "$job_type", "count": {"$sum": 1}}}
    ]
    type_dist = [{"type": t["_id"], "count": t["count"]}
                 for t in jobs_collection.aggregate(pipeline)]

    # Jobs over time (last 30 days bucketed by day)
    recent_jobs = list(jobs_collection.find(q, {"created_date": 1, "job_type": 1})
                                      .sort("created_date", DESCENDING).limit(100))
    daily = {}
    for j in recent_jobs:
        day = str(j.get("created_date", ""))[:10]
        daily[day] = daily.get(day, 0) + 1
    jobs_over_time = [{"date": k, "count": v} for k, v in sorted(daily.items())]

    return jsonify({
        "total_jobs":          total_jobs,
        "running_jobs":        running_jobs,
        "finished_jobs":       finished_jobs,
        "total_breaches":      total_breaches,
        "attack_type_distribution": type_dist,
        "jobs_over_time":      jobs_over_time,
    })


# ==================================================================
# JOBS / PROJECTS
# ==================================================================

@dashboard_bp.route('/jobs', methods=['GET'])
def list_jobs():
    uid = _user()
    q = {"userID": uid} if uid else {}
    jobs = list(jobs_collection.find(q).sort("created_date", DESCENDING).limit(200))
    return jsonify([_ser(j) for j in jobs])


@dashboard_bp.route('/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    try:
        job = jobs_collection.find_one({"_id": ObjectId(job_id)})
    except Exception:
        return jsonify({"error": "Invalid job id"}), 400
    if not job:
        return jsonify({"error": "Not found"}), 404
    job = _ser(job)
    steps = list(including_jobs_collection.find({"jobID": job_id})
                                          .sort("timestamp_created", ASCENDING))
    job["steps"] = [_ser(s) for s in steps]
    return jsonify(job)


@dashboard_bp.route('/jobs/<job_id>', methods=['DELETE'])
def delete_job(job_id):
    """Delete a job and all its associated data."""
    try:
        from bson.errors import InvalidId
        # Convert job_id to ObjectId if possible
        try:
            job_oid = ObjectId(job_id)
        except InvalidId:
            job_oid = None

        # Delete from jobs_collection
        if job_oid:
            jobs_collection.delete_one({"_id": job_oid})
        
        # Delete from including_jobs_collection
        including_jobs_collection.delete_many({"jobID": job_id})
        
        # Delete from execution_logs
        execution_logs_col.delete_many({"job_id": job_id})
        
        # Delete from summaries (the vulnerability report)
        summaries_col.delete_many({"job_id": job_id})
        
        # Delete from transaction_data
        transaction_col.delete_many({"job_id": job_id})

        return jsonify({"success": True, "message": "Job deleted successfully"})
    except Exception as e:
        logger.error(f"Error deleting job {job_id}: {e}")
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route('/jobs/<job_id>/report', methods=['GET'])
def get_report(job_id):
    """Full vulnerability report from summeriesAttacks."""
    summary = summaries_col.find_one({"job_id": job_id})
    if not summary:
        return jsonify({"error": "Report not ready yet"}), 404
    result = _ser(summary)
    result["execution_log_count"] = execution_logs_col.count_documents({"job_id": job_id})
    result["transaction_count"]   = transaction_col.count_documents({"job_id": job_id})
    return jsonify(result)


@dashboard_bp.route('/jobs/<job_id>/logs', methods=['GET'])
def get_logs(job_id):
    """Paginated execution logs."""
    page  = max(int(request.args.get("page",  1)), 1)
    limit = min(int(request.args.get("limit", 50)), 200)
    skip  = (page - 1) * limit

    logs  = list(execution_logs_col.find({"job_id": job_id})
                                   .sort("timestamp", ASCENDING)
                                   .skip(skip).limit(limit))
    total = execution_logs_col.count_documents({"job_id": job_id})

    return jsonify({
        "logs":  [_ser(l) for l in logs],
        "total": total,
        "page":  page,
        "pages": max(1, (total + limit - 1) // limit),
    })


@dashboard_bp.route('/jobs/<job_id>/transactions', methods=['GET'])
def get_transactions(job_id):
    """Transaction data (node state snapshots)."""
    txs = list(transaction_col.find({"job_id": job_id}).sort("timestamp", ASCENDING))
    return jsonify([_ser(t) for t in txs])


@dashboard_bp.route('/jobs/start', methods=['POST'])
def start_job():
    from app.core.entryPoint import start_workflow
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "No payload"}), 400
    try:
        task = start_workflow.delay(payload)
        return jsonify({"message": "Job queued", "task_id": task.id}), 202
    except Exception as e:
        logger.error(f"Error starting job: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route('/projects', methods=['GET'])
def list_projects():
    uid = _user()
    q = {"userID": uid} if uid else {}
    # Group jobs by their 'targetURL' or 'job_name' to simulate projects. 
    # Let's use targetURL as the project grouping for simplicity, or just return them grouped by job_name.
    pipeline = [
        {"$match": q},
        {"$group": {
            "_id": "$targetURL",
            "project_name": {"$first": "$targetURL"},
            "total_jobs": {"$sum": 1},
            "last_attack": {"$max": "$created_date"},
            "jobs": {"$push": {
                "job_id": {"$toString": "$_id"},
                "job_name": "$job_name",
                "job_type": "$job_type",
                "status": "$job_status",
                "breaches": "$breachedCount"
            }}
        }},
        {"$sort": {"last_attack": -1}}
    ]
    projects = list(jobs_collection.aggregate(pipeline))
    return jsonify(projects)

# ==================================================================
# ATTACK TYPES
# ==================================================================

@dashboard_bp.route('/attack-types', methods=['GET'])
def attack_types():
    types = [jt.value for jt in JobType if jt.value != "all"]
    return jsonify({"attack_types": types})


# ==================================================================
# SERVER-SENT EVENTS — real-time log stream
# ==================================================================

@dashboard_bp.route('/stream/<job_id>')
def stream_logs(job_id):
    """
    SSE endpoint streaming execution_logs for a job in real-time.
    Replays existing logs first, then polls for new ones until job finishes.
    """
    def generate():
        try:
            yield f"data: {json.dumps({'type': 'connected', 'job_id': job_id})}\n\n"

            # Replay existing logs
            existing = list(
                execution_logs_col.find({"job_id": job_id})
                                  .sort("timestamp", ASCENDING)
                                  .limit(500)
            )
            last_ts = None
            for log in existing:
                doc = _ser(log)
                last_ts = doc.get("timestamp")
                yield f"data: {json.dumps({'type': 'log', 'data': doc})}\n\n"

            # If job already finished, send report + done
            job = jobs_collection.find_one({"_id": ObjectId(job_id)})
            if job and job.get("job_status") == "FINISHED":
                summary = summaries_col.find_one({"job_id": job_id})
                if summary:
                    yield f"data: {json.dumps({'type': 'report_ready', 'data': _ser(summary)})}\n\n"
                yield f"data: {json.dumps({'type': 'finished'})}\n\n"
                return

            # Live poll
            while True:
                time.sleep(2)
                q = {"job_id": job_id}
                if last_ts:
                    q["timestamp"] = {"$gt": last_ts}

                new_logs = list(
                    execution_logs_col.find(q).sort("timestamp", ASCENDING).limit(100)
                )
                
                if not new_logs:
                    # send a keep-alive ping to prevent gunicorn timeout
                    yield ": keep-alive\n\n"
                
                for log in new_logs:
                    doc = _ser(log)
                    last_ts = doc.get("timestamp")
                    yield f"data: {json.dumps({'type': 'log', 'data': doc})}\n\n"

                job = jobs_collection.find_one({"_id": ObjectId(job_id)})
                if job and job.get("job_status") == "FINISHED":
                    summary = summaries_col.find_one({"job_id": job_id})
                    if summary:
                        yield f"data: {json.dumps({'type': 'report_ready', 'data': _ser(summary)})}\n\n"
                    yield f"data: {json.dumps({'type': 'finished'})}\n\n"
                    break

        except GeneratorExit:
            pass
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            "Cache-Control":    "no-cache",
            "X-Accel-Buffering": "no",
            "Connection":       "keep-alive",
        }
    )
