# importing all required libraries
import telebot
from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerUser, InputPeerChannel
from telethon import TelegramClient, sync, events

from cowin_api import CoWinAPI
import pprint

from datetime import date
from datetime import timedelta

import time
import requests
import json

#fucntin to send message to telegram
def send_message(availableShots, forDate = "NA", errorCode = "NA", centerName = "NA", centerPincode = "NA", vaccine = "NA"):
    
    #creating the message
    if(availableShots == "error"):
        message = "website got shitfucked " + forDate + " with error " + errorCode 
    elif(availableShots == "running"):
        message = "Still No Hope"
    else:
        message = availableShots + " shots available at " + centerName + ", " + centerPincode + " of vaccine " + vaccine

    # get your api_id, api_hash, token
    # from telegram as described above
    api_id = '5779293'
    api_hash = 'e351456e7d3c2bcde8cc72662272a359'
    token = '1709171208:AAF5Fgyvr5X4vPOKrQIRyVl0HSw5HJwWyyU'
    destination_group_invite_link='tg://join?invite=FioEWI7d-sYUIo2J'

    # your phone number
    phone = '+918597165881'

    # creating a telegram session and assigning
    # it to a variable client
    client = TelegramClient('session', api_id, api_hash)

    # connecting and building the session
    client.connect()

    # in case of script ran first time it will
    # ask either to input token or otp sent to
    # number or sent or your telegram id
    if not client.is_user_authorized():

        client.send_code_request(phone)
        
        # signing in the client
        client.sign_in(phone, input('Enter the code: '))

    entity=client.get_entity(destination_group_invite_link)
    client.send_message(entity=entity,message=message)

    # disconnecting the telegram session
    client.disconnect()

#function to get dates
def get_dates():
    today = date.today()
    # dd/mm/YY
    d1 = today.strftime("%d-%m-%Y")
    d2 = today + timedelta(days=1)

#check availability of vaccines
def check_slots():
    pin_codes = ["133001", "457001", "461111", "464001"]
    today = date.today()
    for pin_code in pin_codes:
        for x in range(0,8):
            nextDate = today+timedelta(x)
            inputDate = nextDate.strftime("%d-%m-%Y")

            url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByPin?pincode=" + pin_code + "&date=" + inputDate
            proxies = {
                "http": 'http://59.94.176.111:3128', 
                "https": 'http://59.94.176.111:3128'
            }
            payload={}
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.51'}

            response = requests.request("GET", url, headers=headers, data=payload, proxies=proxies) 
            if(response.status_code != 200):
                send_message(availableShots="error", forDate=str(inputDate), errorCode=str(response.status_code))
                break
            available_centers = json.loads(response.text)
            
            if(len(available_centers["sessions"]) != 0):
                for y in available_centers["sessions"]:
                    if(y["available_capacity"] != 0 and y["min_age_limit"] == 18):
                        centerName = str(y["name"])
                        centerPincode = str(y["pincode"])
                        availableShots = str(y["available_capacity"])
                        vaccine = str(y["vaccine"])
                        send_message(centerName=centerName, centerPincode=centerPincode, availableShots=availableShots, vaccine=vaccine)
            
#control frequency for checking
def main_function():
    i = 0
    send_message(availableShots="running")
    while True:
        i = i + 1
        check_slots()
        time.sleep(60)
        if(i%60 == 0):
            send_message(availableShots="running")

#run the program
main_function()
