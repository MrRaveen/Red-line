from typing import Any, Dict, List
import os
from pymongo import MongoClient

MONGO_URI = os.getenv('MONGO_URI')
MONGO_DB = os.getenv('MONGO_DB')
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
summerriesAttacks = db['summerriesAttacks']

def fetch_job_records(userID: str, job_id: str) -> Dict[str, List[Dict[str, Any]]]:
    """Pull the job's node/transaction data + execution logs from Mongo."""
    tx = list(db["transaction_data"].find({"userID": userID, "job_id": job_id}))
    logs = list(db["execution_logs"].find({"userID": userID, "job_id": job_id}))
 
    for rec in tx:
        rec["_id"] = str(rec["_id"])
    for rec in logs:
        rec["_id"] = str(rec["_id"])
    return {"transaction_data": tx, "execution_logs": logs}
    client.close()


