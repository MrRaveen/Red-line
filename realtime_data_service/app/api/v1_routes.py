import time
from app.config import Config
from common.redis_instance import get_redis_ins
from flask import Response
from flask import Blueprint, jsonify

v1_bp = Blueprint('v1', __name__)
r = Config.r
@v1_bp.route('/health')
def health_check():
    return jsonify({"status": "ok", "service": "realtime_data_service"})

def event_stream():
    try:
        pubsub = r.pubsub()
        pubsub.subscribe(Config.REDIS_PUBSUB_PART)
        INTERVAL = 15
        start_time = time.monotonic()
        last_time = start_time
        while True:
            current_time = time.monotonic()
            if current_time - last_time >= INTERVAL:
                yield ":keepalive\n\n"
                last_time = current_time
            message = pubsub.get_message(timeout=1.0)            
            if message and message['type'] == 'message':
                yield f"data: {message['data']}\n\n"    
    finally:
        pubsub.unsubscribe(Config.REDIS_PUBSUB_PART)
        pubsub.close()            

@v1_bp.route('/stream')
def stream():
    return Response(event_stream(), mimetype="text/event-stream")

