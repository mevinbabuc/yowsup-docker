"""Fetching Nexonia Data via nexonia api calls."""

from __future__ import unicode_literals
import requests
import json
import time
import uuid
from datetime import datetime, timedelta
from lxml import etree as et
from pymongo import MongoClient


class UserAuth(object):
    """User Authentication on Nexonia."""

    def __init__(self, user_credentials):
        """Constructor Method."""
        self.username = user_credentials['username']
        self.password = user_credentials['password']

    def get_token(self):
        """Return the token for that user."""
        auth_url = "https://system.nexonia.com/assistant/mobile/authentication"
        payload = "{\n\t\"emailAddress\": \"" + self.username + "\",\n\t\"password\": \"" + self.password + "\",\n\t\"device\": \"ANDROID\",\n\t\"apiVersion\": \"23\",\n\t\"product\": \"TIMESHEETS\",\n\t\"organizationId\": \"1-578c2e65-cpj2\",\n\t\"actingUserId\": \"10101-157b69c91c5-1jo6\",\n\t\"productVersion\": \"5.3.2\",\n\t\"deviceId\": \"d46f72fb-6dd2-33a2-bbfb-841c7c839bbb\",\n\t\"osVersion\": \"6.0.1 OnePlus\",\n\t\"modelDescription\": \"ONEPLUS ONE E1003\"\n}"
        headers = {
            'user-agent': "Timesheets/5.3.2/Android6.0.1 OnePlus/ONEPLUS ONE E1003",
            'cache-control': "no-cache",
            'postman-token': "47891d6d-1e5c-b245-d343-3177f7a00da8"
        }
        response = requests.request("POST", auth_url, data=payload, headers=headers)
        token = json.loads(response.content).get('token', None)
        return token


class GetData(object):
    """Get nexonia data."""

    def __init__(self, token):
        """Constructor method."""
        self.token = token

    def get_data(self):
        """Get data."""
        fetch_url = "https://na1.system.nexonia.com/assistant/webapi/api"
        payload = "requestXml=%3CapiRequest%3E%3CapiAction%20actionId%3D%22103%22%3E%3CgetTimeSetup%20%2F%3E%3C%2FapiAction%3E%3CapiAction%20actionId%3D%22104%22%3E%3CgetWeeks%20weekCount%3D%2215%22%20%2F%3E%3C%2FapiAction%3E%3CapiAction%20actionId%3D%22119%22%3E%3CgetTimers%20%2F%3E%3C%2FapiAction%3E%3C%2FapiRequest%3E"
        headers = {
            'authorization': "token " + self.token,
            'content-type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
            'postman-token': "a1fa8c2f-cc41-9366-61ff-c96ca4bce443"
        }
        response = requests.request("POST", fetch_url, data=payload, headers=headers)
        root = et.fromstring(str(response.text))
        doc = root.xpath("//apiResponse//apiResult[@actionId='103']//setup")[0]
        customer_ele = doc.xpath("//customer")
        projects = {}
        for customer in customer_ele:
            cust_id = customer.get("id")
            for project in customer.getchildren():
                projects[project.get("number")] = [project.get("id"), cust_id]
        return projects


class SaveData(object):
    """Save User data."""

    def __init__(self, projects_dict, user_data, token):
        """Constructor method."""
        self.user_data = user_data
        self.projects_dict = projects_dict
        self.token = token

    def save_data(self):
        """Save data."""
        fetch_url = "https://na1.system.nexonia.com/assistant/webapi/api"
        duration = str(int(float(self.user_data['work_hours']) * 60))
        day_worked = self.user_data['day']
        project_id = self.projects_dict[self.user_data['project_id']][0]
        customer_id = self.projects_dict[self.user_data['project_id']][1]
        client_creation_date = str(int(time.time() * 1000))
        client_id = str(uuid.uuid4())

        day_worked = self.get_date(day_worked)
        payload = "requestXml=%3CapiRequest%3E%3CapiAction%20actionId%3D%22101%22%3E%3CeditTimeEntry%20clientId%3D%22" + client_id + "%22%20customerId%3D%22" + customer_id + "%22%20projectId%3D%22" + project_id + "%22%20categoryId%3D%22165-3ff8549b-6%22%20taskId%3D%2210101-157d33d0948-ou6%22%20billable%3D%22false%22%20dayWorked%3D%22" + day_worked + "%22%20overridden%3D%22false%22%20duration%3D%22" + duration + "%22%20startTime%3D%22-1%22%20stopTime%3D%22-1%22%20breakTime%3D%22-1%22%20clientCreationDate%3D%22" + client_creation_date + "%22%3E%3CfieldValue%20id%3D%2210101-15797b40023-6h69%22%3E%3C%2FfieldValue%3E%3CfieldValue%20id%3D%2210101-15797b40023-6h67%22%3E140%3C%2FfieldValue%3E%3C%2FeditTimeEntry%3E%3C%2FapiAction%3E%3C%2FapiRequest%3E"
        headers = {
            'authorization': "token " + self.token,
            'content-type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
            'postman-token': "94939451-12bb-f634-7349-7006b7ef95f2"
        }
        response = requests.request("POST", fetch_url, data=payload, headers=headers)
        root = et.fromstring(str(response.text))
        doc = root.xpath("//apiResponse//apiResult//editTimeEntry")[0]
        result = doc.get('success')
        print(response.text)
        return "Saved" if result == "true" else "Failed"

    def get_date(self, day):
        """Get formatted date."""
        day = day.lower()
        current_date = datetime.now()
        start_date = current_date - timedelta((current_date.weekday() + 2) % 7)
        end_date = start_date + timedelta(days=6)
        dates = {
            'saturday': (start_date).strftime("%Y%%2F%m%%2F%d"),
            'sunday': (start_date + timedelta(days=1)).strftime("%Y%%2F%m%%2F%d"),
            'monday': (start_date + timedelta(days=2)).strftime("%Y%%2F%m%%2F%d"),
            'tuesday': (start_date + timedelta(days=3)).strftime("%Y%%2F%m%%2F%d"),
            'wednesday': (start_date + timedelta(days=4)).strftime("%Y%%2F%m%%2F%d"),
            'thursday': (start_date + timedelta(days=5)).strftime("%Y%%2F%m%%2F%d"),
            'friday': (end_date).strftime("%Y%%2F%m%%2F%d"),
        }
        day = [d for d in dates.keys() if day in d][0]
        return dates[day]


class Nexonia(object):
    """Class for calling all the apis."""

    def __init__(self):
        """Constructor Method."""
        # self.client = MongoClient()
        self.client = MongoClient("mongodb://mongodb/batman")
        self.now = datetime.now()
        self.day_of_week = self.now.date().weekday()
        db = self.client.nexonia
        self.user_data = db.user_data

    def login(self, phone, msg):
        """Login and save user credentials."""
        if msg.startswith('login') or msg.startswith('Login'):
            msg = msg.split(" ")
            username, password = msg[0], msg[1]
            token = UserAuth(user_credentials={
                'username': username,
                'password': password
            })
            self.user_data.insert_one({"phone": phone, "username": username, "password": password, "token": token})
            return "Login Successful :)" if token else "Invalid Username/Password :("

    def fill_timesheet(self, phone, msg):
        """Timesheet data per day."""
        if msg.startswith('timesheet') or msg.startswith('Timesheet'):
            msg = msg.split(" ")
            obj = self.user_data.find_one({"phone": phone})
            token = UserAuth(user_credentials={
                'username': obj["username"],
                'password': obj["password"]
            })
            get_data = GetData(token=token)
            projects_dict = get_data.get_data()

            save_data = SaveData(
                projects_dict,
                {
                    'day': msg[1],
                    'project_id': msg[2],
                    'work_hours': msg[3]
                },
                token
            )
            save_data.save_data()

    # token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvcmdJZCI6IjEtNTc4YzJlNjUtY3BqMiIsImF1aWQiOiIxMDEwMS0xNTdiNjljOTFjNS0xam82IiwiY3VpZCI6IjEwMTAxLTE1N2I2OWM5MWM1LTFqbzYiLCJpYXQiOjE0OTcwODc1MjgwMDYsImRldmljZSI6IkFORFJPSUQiLCJkZXZpY2VJZCI6ImQ0NmY3MmZiLTZkZDItMzNhMi1iYmZiLTg0MWM3YzgzOWJiYiIsImFwaVZlcnNpb24iOjIzLCJwcm9kdWN0IjoiVElNRVNIRUVUUyIsInByb2R1Y3RWZXJzaW9uIjoiNS4zLjIiLCJzY29wZSI6Im1vYmlsZSJ9.TGIycm_KbPPrpDzO2nRPsoSTY6AoqMUMuacyw8SrsR1X8czAxyp-j-ZAR0ma_ZbOgoQiCbGzbx67qR-lLSDp-j3oA3DYIP8Pjq5c0TjF5d3OpO7drolhkWHjGGCTXzuM4gEjTB7JY7e3hGDHd5oDrReW5isDgDeUo-IouzSttFrtuBuAs9g-Wc8UtgJabX6IsBUb8Z3cqMwxhwJOeMBuVmNEHKmX80afevtxTMdEyZlEVxvJ03RNpWhb3LT_pr2TpJgkWdqK8i4UhuTAuirkZVIOoi3hFxpz6C-9hbLfTNpFVHJyxeG4nhk6_vbcRPtZEMWD3ijF4IiBcGIV9ShlbA'  # authenticate.get_token()
