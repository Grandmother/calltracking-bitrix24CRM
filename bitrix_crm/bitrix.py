import json
import urllib.parse as urlparse
import pycurl
import io


# Bitrix full authorization docs: https://dev.1c-bitrix.ru/learning/course/index.php?COURSE_ID=43&LESSON_ID=2486#full_auth

# BitrixCrm class implements the access to Bitrix CRM via REST API.
class BitrixCrm:
    def __init__(self, clientID, appKey, companyName, redirectURL):
        self.clientID = clientID
        self.appKey = appKey
        self.oauthRedirectURL = redirectURL
        self.apiBaseURL = "https://" + companyName + ".bitrix24.ru/"
        self.oauth1StepURLSuffix = "oauth/authorize/"
        self.oauth2StepURL = "https://oauth.bitrix.info/oauth/token/"
        self.refreshGrant = "refresh_token"
        self.authorizationGrant = "authorization_code"
        self.apiURLSuffix = "rest/"

    def request(self, query):
        buf = bytes()
        response = io.BytesIO()
        conn = pycurl.Curl()

        conn.setopt(pycurl.URL, query)
        conn.setopt(pycurl.FOLLOWLOCATION, True)
        conn.setopt(pycurl.SSL_VERIFYPEER, False)
        conn.setopt(pycurl.SSL_VERIFYHOST, False)
        conn.setopt(pycurl.COOKIEFILE, "cookies.txt")
        conn.setopt(pycurl.WRITEDATA, response)

        conn.perform()

        url = conn.getinfo(pycurl.EFFECTIVE_URL)
        urlParsed = urlparse.urlparse(url)

        queryParsed = urlparse.parse_qs(urlParsed.query)

        conn.close()
        return queryParsed, response.getvalue().decode()

    # Makes authorization requests. Writes access token to self. Access token is valid only for one hour, so
    # every hour we need to refresh it via refresh token. RefreshToken function is needed right for this purposes.
    def Authorize(self):
        q = self.apiBaseURL +\
            self.oauth1StepURLSuffix +\
            "?client_id=" + self.clientID

        queryParsed, response = self.request(q)

        q = self.oauth2StepURL + "?" \
                                 "grant_type=" + self.authorizationGrant +\
                                 "&client_id=" + self.clientID +\
                                 "&client_secret=" + self.appKey +\
                                 "&code=" + queryParsed["code"][0]

        queryParsed, response = self.request(q)

        jsonResp = json.loads(response)
        self.access_token = jsonResp["access_token"]
        self.refresh_token = jsonResp["refresh_token"]
        print("Got the access token.\n\tNew access_token: {}\n\tNew refresh_token: {}".format(self.access_token,
                                                                                              self.refresh_token))


    # Refreshes the access token. Need to be called every one hour.
    def RefreshToken(self):
        q = self.oauth2StepURL +\
            "?grant_type=" + self.refreshGrant +\
            "&client_id=" + self.clientID +\
            "&client_secret=" + self.appKey +\
            "&refresh_token=" + self.refresh_token

        queryParsed, response = self.request(q)

        jsonResp = json.loads(response)
        self.access_token = jsonResp["access_token"]
        self.refresh_token = jsonResp["refresh_token"]
        print("Token is refreshed.\n\tNew access_token: {}\n\tNew refresh_token: {}".format(self.access_token,
                                                                                            self.refresh_token))
