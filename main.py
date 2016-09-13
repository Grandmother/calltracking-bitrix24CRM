import bitrix24
import argparse
import time

import bitrix_crm
import calltracking
from credentials import bitrixApplication as bitrixCred
from credentials import calltrackingApplication as calltrackingCred

sources = {
    "CALL" : "CALL",
    "MISSED" : "SELF",
    "EMAIL" : "EMAIL"
}

lastCall = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - 5*60))

def calltrackingInit():
    ct = calltracking.Calltracking(calltrackingCred["login"], calltrackingCred["password"])
    ct.Authorize()
    return ct

def bitrixInit():

    bt = bitrix_crm.BitrixCrm(bitrixCred["appID"],
                              bitrixCred["appSecretKey"],
                              bitrixCred["companyName"],
                              bitrixCred["oauthRedirectURL"])
    bt.Authorize()

    btApi = bitrix24.Bitrix24(bitrixCred["companyName"], bt.access_token)
    return btApi

def parseArgs():
    global lastCall

    argsParser = argparse.ArgumentParser()
    argsParser.add_argument("-a", "--after", help="Set a date of starting tracking calls.")
    args = argsParser.parse_args()

    if args.after:
        lastCall = args.after

def main():
    global lastCall

    parseArgs()
    bt = bitrixInit()

    while True:
        print("Let's look for a callers.")
        ct = calltrackingInit()
        calls = ct.GetInfo(calltrackingCred["project"], lastCall)
        # save the time of the last call.
        if len(calls) > 0:
            lastCall = calls[len(calls)-1]["datetime"]

        for call in calls:
            print(call)
            bt.call("crm.lead.add",
                    {'FIELDS':{'TITLE': call['caller'],
                               'SOURCE_ID': sources["CALL"],
                               'ASSIGNED_BY_ID': bitrixCred["employee"],
                               'PHONE': { '0': {'VALUE': call['caller'], "VALUE_TYPE": "WORK"}}
                               }
                     })

        time.sleep(60 * 2)

if __name__ == "__main__":
    main()