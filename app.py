# importing all required libraries
import telebot
from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerUser, InputPeerChannel
from telethon import TelegramClient, sync, events

from cowin_api import CoWinAPI
import pprint

from datetime import date, datetime
from datetime import timedelta

import time
import requests
import json

from lxml.html import fromstring
from itertools import cycle
import traceback
import random

import os
from dotenv import load_dotenv

load_dotenv()

import psycopg2

#functin to send message to telegram
def send_message(errorMessage, availableShots = "NA", forDate = "NA", errorCode = "NA", centerName = "NA", centerPincode = "NA", vaccine = "NA"):
    #creating the message
    if(errorMessage == "error"):
        message = "API call didn't work " + str(forDate) + " with error " + str(errorCode) + " for pincode " + str(centerPincode)
    elif(errorMessage == "running"):
        message = "change kr diya hihihihi"
    elif(errorMessage == "noError"):
        message = availableShots + " shots available at " + centerName + ", " + centerPincode + " of vaccine " + vaccine + " for date " + str(forDate)
    elif(errorMessage == "authError"):
        message = "Auth token expired, last ten calls didn't work"

    # get your api_id, api_hash, token
    # from telegram as described above
    api_id = os.getenv('API_ID')
    api_hash = os.getenv('API_HASH')
    #token = os.getenv('TOKEN')
    destination_group_invite_link = os.getenv('DESTINATION_GROUP_INVITE_LINK')

    # your phone number
    phone = os.getenv('PHONE')

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

#function to call each day
def apiCallForDay(x, pin_code, conn, noOfTimes):
    nextDate = date.today()+timedelta(x)
    inputDate = nextDate.strftime("%d-%m-%Y")

    url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByPin?pincode=" + pin_code + "&date=" + inputDate
    
    payload={}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.51'}

    #proxy = random.sample(proxies, k=1)[0]
    #print(proxy)
    #proxy = '59.94.176.111:3128'
    """
    for proxy in proxies:
        break
    """
    """
    try:
        response = requests.request("GET", url, data=payload, proxies={"http": proxy, "https": proxy}, headers = headers) 
    except:
        print("Connection Error")
        break
    """
    response = requests.request("GET", url, data=payload, headers=headers) 
    #response = requests.get(url,proxies={"http": proxy, "https": proxy}, headers = headers)
    logText = str(noOfTimes) + " " + str(pin_code) + " " + str(inputDate) + " " + str(response.status_code) + " Day " + str(time.strftime("%H:%M:%S", time.localtime()))
    insertInDB(conn=conn, logText=logText)
    
    if(response.status_code != 200):
        send_message(errorMessage="error", forDate=str(inputDate), errorCode=str(response.status_code), centerPincode=str(pin_code))
        return
    available_centers = json.loads(response.text)
    #pprint.pprint(available_centers["sessions"])
    if(len(available_centers["sessions"]) != 0):
        for y in available_centers["sessions"]:
            if(y["available_capacity"] != 0 and y["min_age_limit"] == 18):
                centerName = str(y["name"])
                centerPincode = str(y["pincode"])
                availableShots = str(y["available_capacity"])
                vaccine = str(y["vaccine"])
                send_message(errorMessage="noError", centerName=centerName, centerPincode=centerPincode, availableShots=availableShots, vaccine=vaccine, forDate=inputDate)
    time.sleep(10)

#function to call for week
def apiCallForWeek(pin_code, conn, noOfTimes):
    inputDate = (datetime.now() + timedelta(hours = 5, minutes = 30)).strftime("%d-%m-%Y")
    #inputDate = date.today().strftime("%d-%m-%Y")

    url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByPin?pincode=" + pin_code + "&date=" + inputDate

    payload={}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.51',
                'Authorization': 'Bearer Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX25hbWUiOiI0ZjUxMWJlMi05OWRjLTQxZTUtOTRhNy0zMjY2ZTFmMDFhZWYiLCJ1c2VyX2lkIjoiNGY1MTFiZTItOTlkYy00MWU1LTk0YTctMzI2NmUxZjAxYWVmIiwidXNlcl90eXBlIjoiQkVORUZJQ0lBUlkiLCJtb2JpbGVfbnVtYmVyIjo4NTk3MTY1ODgxLCJiZW5lZmljaWFyeV9yZWZlcmVuY2VfaWQiOjUzMTc4MzY2MTQyODIwLCJzZWNyZXRfa2V5IjoiYjVjYWIxNjctNzk3Ny00ZGYxLTgwMjctYTYzYWExNDRmMDRlIiwidWEiOiJNb3ppbGxhLzUuMCAoV2luZG93cyBOVCAxMC4wOyBXaW42NDsgeDY0KSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvOTAuMC40NDMwLjkzIFNhZmFyaS81MzcuMzYgRWRnLzkwLjAuODE4LjU2IiwiZGF0ZV9tb2RpZmllZCI6IjIwMjEtMDUtMTFUMTk6MDc6NTAuNTc1WiIsImlhdCI6MTYyMDc2MDA3MCwiZXhwIjoxNjIwNzYwOTcwfQ.3qLReOcYr0hFu9KRMpShBmn0sXt1Lms8VF_uoBBMVs4'
    }

    response = requests.request("GET", url, data=payload, headers=headers) 
    logText = str(noOfTimes) + " " + str(pin_code) + " " + str(inputDate) + " " + str(response.status_code) + " Week " + str((datetime.now()+timedelta( hours=5, minutes=30 )).strftime('%H:%M:%S'))
    insertInDB(conn=conn, logText=logText)
    print(logText)
    
    if(response.status_code != 200):
        #send_message(errorMessage="error", forDate=str(inputDate), errorCode=str(response.status_code), centerPincode=str(pin_code))
        time.sleep(10)
        return response.status_code
    available_centers = json.loads(response.text)
    if(len(available_centers["centers"]) != 0):
        for z in available_centers["centers"]:
            centerName = str(z["name"])
            centerPincode = str(z["pincode"])
            if(len(z["sessions"]) != 0):
                for y in z["sessions"]:
                    if(y["available_capacity"] != 0 and y["min_age_limit"] == 18):
                        availableShots = str(y["available_capacity"])
                        vaccine = str(y["vaccine"])
                        shotDate = str(y['date'])
                        send_message(errorMessage="noError", centerName=centerName, centerPincode=centerPincode, availableShots=availableShots, vaccine=vaccine, forDate=shotDate)
    time.sleep(10)
    return response.status_code

#check availability of vaccines
def check_slots(noOfTimes, conn):
    pin_codes = os.getenv('PIN_CODES').split(',')

    #proxies = get_proxies()
    noOfErrors = 0
    for x in range(0,7):
        for pin_code in pin_codes:
            
            statusCode = apiCallForWeek(pin_code = pin_code, conn = conn, noOfTimes=noOfTimes)

            if(statusCode == 200):
                noOfErrors = 0
            elif(statusCode != 200):
                noOfErrors = noOfErrors + 1
                if(noOfErrors == 10):
                    send_message(errorMessage="authError")
                    noOfErrors = 0

            #apiCallForDay(x = x, pin_code = pin_code, conn = conn, noOfTimes=noOfTimes)
            
            """
            nextDate = date.today()+timedelta(x)
            inputDate = nextDate.strftime("%d-%m-%Y")

            url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByPin?pincode=" + pin_code + "&date=" + inputDate
            
            payload={}
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.51'}
            response = requests.request("GET", url, data=payload, headers=headers) 
            logText = str(pin_code) + " " + str(inputDate) + " " + str(response.status_code)
            print(logText)
            
            if(response.status_code != 200):
                send_message(errorMessage="error", forDate=str(inputDate), errorCode=str(response.status_code), centerPincode=str(pin_code))
                break
            available_centers = json.loads(response.text)
            if(len(available_centers["sessions"]) != 0):
                for y in available_centers["sessions"]:
                    if(y["available_capacity"] != 0 and y["min_age_limit"] == 18):
                        centerName = str(y["name"])
                        centerPincode = str(y["pincode"])
                        availableShots = str(y["available_capacity"])
                        vaccine = str(y["vaccine"])
                        send_message(errorMessage="noError", centerName=centerName, centerPincode=centerPincode, availableShots=availableShots, vaccine=vaccine, forDate=inputDate)
            time.sleep(10)
            """
           
#control frequency for checking
def main_function():
    i = 0
    conn = makeDBconnection()
    send_message(errorMessage="running")
    while True:
        check_slots(noOfTimes=i, conn = conn)
        i = i + 1
        #time.sleep(60)
        if(i%25 == 0):
            send_message(errorMessage="running")
    conn.close()

#getting proxies function
def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:100]:
        if(i.xpath('.//td[7][contains(text(),"yes")]') and i.xpath('.//td[4][contains(text(),"India")]')):
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies

#make db connection
def makeDBconnection():
    #Establishing the connection
    conn = psycopg2.connect(
        database="botdb", user='postgres', password='admin', host='127.0.0.1', port= '5432'
    )
    #Setting auto commit false
    conn.autocommit = True
    return conn

#insert new entry
def insertInDB(conn, logText):
    #Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    
    # Preparing SQL queries to INSERT a record into the database.
    cursor.execute('''INSERT INTO logger (log) VALUES (%s);''', (logText,))

    # Commit your changes in the database
    conn.commit()

#run the program
main_function()
