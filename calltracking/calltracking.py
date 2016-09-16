import urllib.request
import json
import time
from urllib.parse import quote
import logging

SECONDS_PER_DAY=60*60*24


class Calltracking:
    def __init__(self, login, passwd):
        self.login = login
        self.passwd = passwd
        self.loginURL = "https://calltracking.ru/api/login.php"
        self.getDataURL = "https://calltracking.ru/api/get_data.php"

    def Authorize(self):
        resp = urllib.request.urlopen(self.loginURL + "?account_type=calltracking" +
                                      "&login=" + self.login +
                                      "&password=" + self.passwd +
                                      "&service=analytics").read().decode("UTF-8")
        resp = json.loads(resp)
        if resp["error_code"] == "0":
            self.token = resp["data"]
            print("Authorized as " + self.login)
            return True
        else:
            print("Not uthorized. Error text: " + resp["error_text"])
            return False

    def getCalls(self, prNum):
        q = self.getDataURL +\
              "?auth=" + self.token +\
              "&project=" + str(prNum) +\
              "&metrics=" + quote("ct:duration") +\
              "&dimensions=" + quote("ct:datetime,ct:source,ct:caller,ct:virtual_number") +\
              "&start-date=" + time.strftime("%Y-%m-%d", time.localtime(time.time() - 20*SECONDS_PER_DAY)) +\
              "&end-date=" + time.strftime("%Y-%m-%d", time.localtime(time.time())) +\
              "&view-type=" + "list" +\
              "&max-results=" + "500"
        # print("query: ", q)
        resp = urllib.request.urlopen(q).read().decode("UTF-8")
        resp = json.loads(resp)
        if resp["error_code"] == "0":
            return sorted(resp["data"], key=lambda k: k['datetime'])
        else:
            print("Error: " + resp["error_code"])
            print("Error text: " + resp["error_text"])
            print()
            return []

    def GetInfo(self, project:int, after:str):
        calls = self.getCalls(project)
        if calls == None:
            return None

        callsAfter = [call for call in calls if call['datetime'] > after]
        return callsAfter
