import json
import pprint
import sseclient
import requests

def with_requests(url, headers):
    """Get a streaming response for the given event feed using requests."""    
    return requests.get(url, stream=True, headers=headers)

url = 'https://stream.wikimedia.org/v2/stream/recentchange'
headers = {'Accept': 'text/event-stream'}
response = with_requests(url, headers)
client = sseclient.SSEClient(response)

for event in client.events():
    stream = json.loads(event.data)
    pprint.pprint(stream)