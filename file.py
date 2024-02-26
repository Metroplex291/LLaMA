import requests
import json
 

data = {'model': 'dolphin', 'messages': [{'role': 'user', 'content': 'hey!'}], 'stream': False}
headers = {'api-key': 'shard-jsW4ZXRuuKRyfu27opINzywriKiQLq', 'Content-Type': 'application/json'}
r = requests.post(url='https://shard-ai.xyz/v1/chat/completions', headers=headers, data=json.dumps(data))
print(r.text)
