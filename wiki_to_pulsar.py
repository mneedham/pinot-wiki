import json
import sseclient
import datetime
import requests
import pulsar

def with_requests(url, headers):
    return requests.get(url, stream=True, headers=headers)

def json_serializer(obj):
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise f"Type {type(obj)} not serializable"

url = 'https://stream.wikimedia.org/v2/stream/recentchange'
headers = {'Accept': 'text/event-stream'}
response = with_requests(url, headers) 
client = sseclient.SSEClient(response)

pulsar_client = pulsar.Client('pulsar://localhost:6650')
producer = pulsar_client.create_producer('wiki-events')

events_processed = 0
for event in client.events():
    stream = json.loads(event.data)
    payload = json.dumps(stream, default=json_serializer, ensure_ascii=False).encode('utf-8')
    producer.send(payload)

    events_processed += 1
    if events_processed % 100 == 0:
        print(f"{str(datetime.datetime.now())} Flushing after {events_processed} events")
        producer.flush()
