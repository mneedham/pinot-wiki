import json
import sseclient
import datetime
import requests
import time
from confluent_kafka import Producer

def with_requests(url, headers):
    """Get a streaming response for the given event feed using requests."""    
    return requests.get(url, stream=True, headers=headers)

def acked(err, msg):
    if err is not None:
        print("Failed to deliver message: {0}: {1}"
              .format(msg.value(), err.str()))

def json_serializer(obj):
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise "Type %s not serializable" % type(obj)

producer = Producer({'bootstrap.servers': 'localhost:9092'})

url = 'https://stream.wikimedia.org/v2/stream/recentchange'
headers = {'Accept': 'text/event-stream'}
response = with_requests(url, headers) 
client = sseclient.SSEClient(response)

events_processed = 0

while True:
    try: 
        for event in client.events():
            stream = json.loads(event.data)
            payload = json.dumps(stream, default=json_serializer, ensure_ascii=False).encode('utf-8')
            producer.produce(topic='wiki_events', key=str(stream['meta']['id']), value=payload, callback=acked)

            events_processed += 1
            if events_processed % 100 == 0:
                print(f"{str(datetime.datetime.now())} Flushing after {events_processed} events")
                producer.flush()
    except Exception as ex:
        print(f"{str(datetime.datetime.now())} Got error:" + str(ex))
        response = with_requests(url, headers) 
        client = sseclient.SSEClient(response)
        time.sleep(2)