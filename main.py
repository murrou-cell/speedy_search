import requests
import json
import time
import datetime
import configparser

config = configparser.ConfigParser()
config.read('config.cfg')
token = config['DEFAULT']['token']
barcode = config['DEFAULT']['barcode']


url = f"https://myspeedy.speedy.bg/rest/public/shipment/location?barcode={barcode}&token={token}"

payload = {}
headers = {
  'authority': 'myspeedy.speedy.bg',
  'accept': 'application/json, text/javascript, */*; q=0.01',
  'accept-language': 'en-US,en;q=0.9,bg;q=0.8,de;q=0.7',
  'content-type': 'application/json;charset=utf-8',
  'referer': f'https://myspeedy.speedy.bg/shipment/location?barcode={barcode}&token={token}',
  'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'x-requested-with': 'XMLHttpRequest'
}
old_long_lat = None
while True:

    response = requests.request("GET", url, headers=headers, data=payload)

    data = json.loads(response.text)

    long_lat = f'{data["shipment"]["latLng"]["lat"]},{data["shipment"]["latLng"]["lng"]}'
    if long_lat != old_long_lat:
        print(f'{datetime.datetime.now()} --- https://www.google.com/maps/place/{data["shipment"]["latLng"]["lat"]},{data["shipment"]["latLng"]["lng"]}?entry=ttu')
        print('\n')
        old_long_lat = long_lat
        time.sleep(30)