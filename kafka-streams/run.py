import faust
import event_pb2

app = faust.App("streamer", broker="kafka://localhost:9092") 

events_topic = app.topic("graph-log-data", value_serializer="raw")

@app.agent(events_topic)
async def process(stream):
    async for raw_value in stream:
        log_entry = event_pb2.Log()
        log_entry.ParseFromString(raw_value)
        print(f"[{log_entry.nodeName}] service_name={log_entry.job_service_name}")

if __name__ == "__main__":
    app.main()