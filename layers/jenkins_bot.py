import jenkins
import json
from pymongo import MongoClient


class JenkinsPlugin(object):
    """A jenkins plugin that can be plugged to whatsappbit"""

    def __init__(self, *args, **kwargs):
        super(JenkinsPlugin, self).__init__(*args, **kwargs)
        self.client = MongoClient("mongodb://mongodb/batman")
        db = self.client.test_database
        self.jenkins_table = db.jenkins

        self.jenkins_url = 'http://ec2-35-160-159-20.us-west-2.compute.amazonaws.com:49001/'
        self.__COMMANDS = {
            'INITIALISE': {
                'input': 'hook me up with jenkins',
                'success_messages': ['Hello, What would you like me to do?'],
                'failure_messages': ['Hello, Can you please enter your credentials?'],
                'action': self.handle_initialise,
                'case_sensitive': False
            },
            'VALIDATE_DATA': {
                'input': 'USERNAME: ',
                'success_mesages': ['Authenctication Successful! What would you like to do?'],
                'failure_messages': [
                    "Invalid format! Please enter in this format: USERNAME: username@example.com, PASSWORD: password"
                ],
                'action': self.validate_credentials,
                'case_sensitive': True
            },
            'GET_JOBS': {
                'input': 'get jenkins jobs',
                'success_messages': [],
                'failure_messages': [
                    "Can you please enter your credentials?",
                    "Something went wrong! Please try again later..."
                ],
                'action': self.get_jobs,
                'case_sensitive': False
            },
            'GET_LAST_BUILD_INFO': {
                'input': 'job: ',
                'success_mesages': [],
                'failure_messages': [
                ],
                'failure_messages': [
                    "Invalid format! Please enter in this format: get info job: 'JOB_FULL_NAME'",
                    "Can you please enter your credentials?",
                    "Something went wrong! Please try again later..."
                ],
                'action': self.get_last_build_info,
                'case_sensitive': True
            }
        }

    def parse_message(self, phone, message):
        for key, value in self.__COMMANDS.items():
            if 'case_sensitive' in value and not value['case_sensitive']:
                message = message.lower()
            if value['input'] in message:
                return value['action'](phone, message)
        return "Sorry, I'm not able to understand what you're looking for."

    def handle_initialise(self, phone, message):
        document = self.jenkins_table.find_one({"number": phone})
        if document:
            return self.__COMMANDS['INITIALISE']['success_messages'][0]
        else:
            return self.__COMMANDS['INITIALISE']['failure_messages'][0]

    def authenticate(self, number):
        document = self.jenkins_table.find_one({"number": number})
        if not document:
            return {}
        server = jenkins.Jenkins(
            self.jenkins_url,
            document['username'],
            document['password']
        )
        try:
            server.get_whoami()
        except jenkins.JenkinsException:
            return {}
        return document

    def validate_credentials(self, phone, message):
        if len(message.split(", ")) != 2:
            return self.__COMMANDS['VALIDATE_DATA']['failure_messages'][0]
        username_part = message.split(", ")[0]
        password_part = message.split(", ")[1]
        if len(username_part.split("USERNAME: ")) != 2 or len(password_part.split("PASSWORD: ")) != 2:
            return self.__COMMANDS['VALIDATE_DATA']['failure_messages'][0]
        username = username_part.split("USERNAME: ")[1]
        password = password_part.split("PASSWORD: ")[1]
        # url = 'http://jenkins:8080'
        server = jenkins.Jenkins(self.jenkins_url, username, password)
        try:
            user = server.get_whoami()
        except jenkins.JenkinsException:
            reponse = self.__COMMANDS['VALIDATE_DATA']['failure_messages'][0]
        else:
            reponse = "Authenctication successful! Logged in as: " + user['fullName']
            # save or update the data
            document = self.jenkins_table.find_one({"number": phone})
            if document:
                self.jenkins_table.update_one({
                    '_id': document['_id']
                }, {
                    '$set': {
                        'username': username,
                        'password': password,
                    }
                }, upsert=False)
            else:
                data = {
                    'number': phone,
                    'name': user['fullName'],
                    'username': username,
                    'password': password
                }
                self.jenkins_table.insert_one(data)
        return reponse

    def get_jobs(self, phone, message):
        authenticated_data = self.authenticate(phone)
        if not authenticated_data:
            return self.__COMMANDS['GET_JOBS']['failure_messages'][0]
        else:
            username = authenticated_data['username']
            password = authenticated_data['password']
        server = jenkins.Jenkins(self.jenkins_url, username, password)
        try:
            jobs = server.get_all_jobs()
            job_names = list()
            for job in jobs:
                job_names.append(job['fullname'])
        except jenkins.JenkinsException:
            return self.__COMMANDS['GET_JOBS']['failure_messages'][1]
        reponse = json.dumps(job_names)
        return reponse

    def get_last_build_info(self, phone, message):
        authenticated_data = self.authenticate(phone)
        if not authenticated_data:
            return self.__COMMANDS['GET_JOBS']['failure_messages'][1]
        else:
            username = authenticated_data['username']
            password = authenticated_data['password']
        server = jenkins.Jenkins(self.jenkins_url, username, password)
        if len(message.split("job: ")) != 2:
            return self.__COMMANDS['GET_LAST_BUILD_INFO']['failure_messages'][0]
        job_name = message.split("job: ")[1]

        try:
            job_info = server.get_job_info(job_name)
            job_dict = dict()
            job_dict['fullname'] = job_name
            if job_info['lastBuild']:
                last_build_number = job_info['lastBuild']['number']
                job_dict['last_build_number'] = last_build_number
                build_info = server.get_build_info(job_name, last_build_number)
                job_dict['status'] = build_info['result'] if build_info['result'] else 'In Progress'
                job_dict['url'] = build_info['url']
            else:
                job_dict['status'] = "No builds made yet!"
        except jenkins.JenkinsException:
            return self.__COMMANDS['GET_LAST_BUILD_INFO']['failure_messages'][2]
        else:
            reponse = json.dumps(job_dict)
        return reponse
