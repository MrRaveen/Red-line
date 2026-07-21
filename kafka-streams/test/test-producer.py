"""
Test producer — sends sample Protobuf-encoded `Log` messages to the
`graph-log-data` topic so you can verify the Faust worker consumes and
parses them correctly.
"""

import argparse
import time
import uuid

from confluent_kafka import Producer
from google.protobuf.timestamp_pb2 import Timestamp

import log_pb2

TOPIC = "graph-log-data"

BOOTSTRAP_SERVERS = "localhost:9094"

producer = Producer({
    "bootstrap.servers": BOOTSTRAP_SERVERS,
})


def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")
    else:
        print(f"Delivered to {msg.topic()} [{msg.partition()}] @ {msg.offset()}")


def build_sample_log(i: int) -> log_pb2.Log:
    log_entry = log_pb2.Log(
        job_service_name="test-service",
        nodeName=f"node-{i}",
        user_id=str(uuid.uuid4()),
        nodeInput=f"sample input payload #{i}",
        nodeOutput=f"sample output payload #{i}",
        targetUrl="https://example.com/webhook",
        budget_remaining="42.50",
        additionalMessage="test message from test-producer.py",
        jobRequest='{"action": "test"}',
        job_response='{"status": "ok"}',
        executionLogSectionForTheTransaction=f"execution log line for run {i}",
    )

    ts = Timestamp()
    ts.GetCurrentTime()
    log_entry.timeRunning.CopyFrom(ts)

    return log_entry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=1, help="Number of test messages to send")
    args = parser.parse_args()

    for i in range(args.count):
        log_entry = build_sample_log(i)
        payload = log_entry.SerializeToString()

        producer.produce(
            TOPIC,
            key=log_entry.user_id.encode("utf-8"),
            value=payload,
            callback=delivery_report,
        )
        producer.poll(0)
        time.sleep(0.2)  

    producer.flush(timeout=5)
    print(f"Done. Sent {args.count} test message(s) to '{TOPIC}'.")


if __name__ == "__main__":
    main()