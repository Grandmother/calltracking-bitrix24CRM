import bitrix24
import argparse
import time

import bitrix_crm
import phonenumbers
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

def get_existed_calls(bt):
    next = 0
    total = 1
    existed_calls = list()
    while next < total:
        print("next: ", next, "total: ", total)
        resp = bt.call("crm.lead.list",{
                                    'SELECT': {'0': {'PHONE'}},
                                    'start': next
                                        })
        raw_existed_calls = resp['result']
        print("calls this time: ", len(raw_existed_calls))
        total = resp['total']
        next += len(raw_existed_calls)
        for call in raw_existed_calls:
            try:
                call['PHONE']
            except KeyError:
                continue

            for phone in call['PHONE']:
                val = phone["VALUE"]
                if val in existed_calls:
                    continue
                try:
                    phoneObj = phonenumbers.parse(val, "RU")
                    if phonenumbers.is_possible_number(phoneObj):
                        val = phonenumbers.format_number(phoneObj, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                except:
                    print("Exception on this number: ", val)
                existed_calls.append(val)
                print(val)

        print("total calls: ", len(existed_calls))

    return existed_calls

def main():
    global lastCall

    parseArgs()
    bt = bitrixInit()

    # return get_existed_calls(bt)
    existed_calls = get_existed_calls(bt)

    while True:
        print("Let's look for a callers.")
        ct = calltrackingInit()
        calls = ct.GetInfo(calltrackingCred["project"], lastCall)
        # save the time of the last call.
        if len(calls) > 0:
            lastCall = calls[len(calls)-1]["datetime"]

        for call in calls:
            val = call['caller']
            try:
                phoneObj = phonenumbers.parse(val, "RU")
                if phonenumbers.is_possible_number(phoneObj):
                    val = phonenumbers.format_number(phoneObj, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            except:
                print("Exception on this number: ", val)

            if val in existed_calls:
                continue
            print(call)
            bt.call("crm.lead.add",
                    {'FIELDS':{'TITLE': val,
                               'SOURCE_ID': sources["CALL"],
                               'ASSIGNED_BY_ID': bitrixCred["employee"],
                               'PHONE': { '0': {'VALUE': val, "VALUE_TYPE": "WORK"}}
                               }
                     })
            existed_calls.append(val)

        time.sleep(60 * 2)

if __name__ == "__main__":
    main()

# SOME EXAMPLES:

    # GET LEAD FIELDS AND THEM DESCRIPTIONS

    # print(json.dumps(bt.call("crm.lead.fields",
    #                          {}), sort_keys=True, indent=4))


    # GET ALL FIELDS OF SPECIFIED LEAD

    # print(json.dumps(bt.call("crm.lead.get",
    #         {'ID': 244 }), sort_keys=True, indent=4))


    # GET A LIST OF LEADS WITH SPECIFIED FIELDS

    # print(json.dumps(bt.call("crm.lead.list",
    #         {'SELECT': {
    #                 '0' : {'ID'},
    #                 '1': {'PHONE'},
    #                 '2': {'TITLE'}
    #             }
    #         }), sort_keys=True, indent=4))
