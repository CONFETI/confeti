import os
import json
import requests

headers = {
           'Content-Type':'application/json',
           'Content-Encoding': 'utf-8'
          }
url = 'http://46.101.194.178/api/rest/conference'
os.chdir('output/valid_output')

for valid_json in os.listdir():
    with open(valid_json, 'r') as to_send:
        json_dict = json.load(to_send)
        send = requests.post(url=url, json=json.dumps(json_dict))
        print(send.json())