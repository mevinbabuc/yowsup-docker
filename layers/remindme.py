from datetime import datetime, timedelta
import re
from pymongo import MongoClient


class WhatappBotSetRemider(object):
    def __init__(self):
        # self.client = MongoClient()
        self.client = MongoClient("mongodb://mongodb/batman")
        self.now = datetime.now()
        self.day_of_week = self.now.date().weekday()
        db = self.client.test_database
        self.scheduled_messages = db.scheduled_messages

    def set_reminder(self, phone, msg):
        if msg.startswith('remind me'):
            message, scheduled_datetime = self.parse_message(msg)

            if message:
                print("GOT message here", message)
                self.scheduled_messages.insert_one({"phone": phone, "message": message, "date": scheduled_datetime})
                return "{0} is scheduled for {1}".format(message, scheduled_datetime)

    def parse_message(self, msg):
        if "at" not in msg:
            msg += " at 9:00 am"
        st = re.search("(\d+):(\d+)\s*([aApP][mM])", msg)
        if not st:
            st = re.search("(\d+)\s*([aApP][mM])", msg)

        st = st.groups(0)
        now = self.now
        slice_message_index = 0

        if "today" in msg:
            date_to_select = datetime.now().date()
            slice_message_index = msg.index("today")

        elif "tomorrow" in msg:
            date_to_select = datetime.now().date() + timedelta(days=1)
            slice_message_index = msg.index("tomorrow")

        else:
            # if neither of the above then we will have monday tuesday.
            for dow in enumerate(["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]):
                if dow[1] in msg:
                    date_to_select = self.get_date_to_schedule(dow[0])
                    slice_message_index = msg.index(dow[1])
                    break
            else:
                return False, "Sorry! - Can you tell me today / tomorrow or monday, tuesday etc."

        if len(st) == 3:
            datestr = "%s-%s-%s %s:%s %s" % (date_to_select.day, date_to_select.month, date_to_select.year, st[0], st[1], st[2])
        else:
            datestr = "%s-%s-%s %s:%s %s" % (date_to_select.day, date_to_select.month, date_to_select.year, st[0], "00", st[1])

        print(datestr)

        datetime_to_schedule = datetime.strptime(datestr, "%d-%m-%Y %I:%M %p")

        if datetime_to_schedule < self.now:
            return False, "Cant scedule for a past date. %s" % datestr

        message = msg[9:slice_message_index]
        message = message.replace("to", "")
        message = message.replace("on", "")
        message = message.strip()
        return message, datetime_to_schedule

    def get_date_to_schedule(self, dow):
        if self.day_of_week == dow:
            date_to_select = self.now
        elif self.day_of_week > dow:
            date_to_select = self.now + timedelta(days=7 - (self.day_of_week - dow))
        else:
            after = dow - self.day_of_week
            date_to_select = self.now + timedelta(after)
        return date_to_select

    def get_messages(self):
        return self.scheduled_messages.find({"date":{"$gte":self.now,"$lte":self.now + timedelta(minutes=5)}})



# message = raw_input("test message: ")
# bot = WhatappBotSetRemider()
# print("setting reminder")
# print(bot.set_reminder("+91-9742544667", message))
# for aa in bot.get_messages():
#     print aa
