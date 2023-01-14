import json
import sseclient
import datetime
import requests

from kafka import KafkaProducer

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

# producer = Producer({'bootstrap.servers': 'localhost:9092'})
producer = KafkaProducer(bootstrap_servers="localhost:9092")

events_processed = 0
for event in client.events():
    stream = json.loads(event.data)
    payload = json.dumps(stream, default=json_serializer, ensure_ascii=False).encode('utf-8')
    # producer.produce(topic='wiki-events', key=str(stream['meta']['id']), 
    #   value=payload, callback=acked)

    producer.send(topic='wiki-events', value=payload)

    events_processed += 1
    if events_processed % 100 == 0:
        print(f"{str(datetime.datetime.now())} Flushing after {events_processed} events")
        producer.flush()
