from app.config import Config
from app.services.get_records import fetch_job_records
from app.services.agentEvaluate import JudgingAgent
import asyncio
import json
import uuid
import logging
logger = logging.getLogger(__name__)
from datetime import datetime
from typing import Any, Dict, List, Optional
import os
from pymongo import MongoClient
from semantic_kernel.contents import ChatHistory
from common.kafka_producer import send_message

class JudgeAgentExecution:
    def __init__(self):
        self.judge = JudgingAgent()

    @staticmethod
    def _robust_json(text: str):
        if not text:
            return {}
        try:
            return json.loads(text)
        except Exception:
            pass
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except Exception:
                pass
        return {"raw_result": text}

    async def run(self, userID: str, job_id: str, target_url: str,
                  budget: int = 3,total_breaches: int = 0, attempts: Optional[List[Any]] = None)->bool:
        if attempts is None:
            attempts = []

        mongo_records = fetch_job_records(userID, job_id)
        print(f"[Mongo] execution_logs={len(mongo_records['execution_logs'])} "
              f"transaction_data={len(mongo_records['transaction_data'])}")

        judgment = await self.judge.evaluate(userID, job_id, attempts, mongo_records)
        print("[JudgingAgent] report received.")

        report_payload = {
            "userID": userID,
            "job_id": job_id,
            "total_categories_processed": len(attempts),
            "number_of_breaches": total_breaches,
            "attempts": attempts,
            "mongo_records": {
                "execution_logs_count": len(mongo_records["execution_logs"]),
                "transaction_data_count": len(mongo_records["transaction_data"]),
            },
            "judging_report": judgment,
        }
        #procude to the topic
        return_status = send_message(Config.JUDGE_OUT_TOPIC,report_payload)
        return return_status
       