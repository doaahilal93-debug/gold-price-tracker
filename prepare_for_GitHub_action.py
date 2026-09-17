import os 
import json
import requests
import time
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

API_KEY= os.environ['API_KEY']
CREDS_JSON= os.environ['CREDS_JSON']
SHEET_URL= os.environ['SHEET_URL']

scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

creds_dict= json.loads(CREDS_JSON)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_url(SHEET_URL).sheet1

existing = sheet.get_all_values()
if len(existing) == 0:
    sheet.insert_row(['date', 'time', 'price_24', 'price_21', 'price_18'], 1)



def gold_price_repeat():
    headers= {"x-api-key": API_KEY}
    response_24= requests.get("https://goldtimo.com/api/v1/price/XAU/EGP/24", headers= headers)
    response_21= requests.get("https://goldtimo.com/api/v1/price/XAU/EGP/21", headers= headers)
    response_18= requests.get("https://goldtimo.com/api/v1/price/XAU/EGP/18", headers= headers)
    
    data_24= response_24.json()
    data_21= response_21.json()
    data_18= response_18.json()

    price_24= data_24['gramBuy']
    price_21= data_21['gramBuy']
    price_18= data_18['gramBuy']

    updatedAt= data_24['updatedAt']
    dt= datetime.fromisoformat(updatedAt)
    date= dt.strftime('%Y-%m-%d')
    hour= dt.strftime('%I:%M:%S:%p')
    

    all_values = sheet.get_all_values()

    if len(all_values) > 1:
        last_row = all_values[-1]
        last_price = float(last_row[2])
    else:
        last_price = None

    if last_price is None or abs(price_24 - last_price) >= 1:
        sheet.append_row([date, hour, price_24, price_21, price_18])
        print('New line')
    else:
        print("price didn't change")
