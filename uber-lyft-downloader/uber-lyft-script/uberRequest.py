# importing the requests library
import requests, pickle, os, dateCalculate, parsingData
from lxml import html
import json
from utils import is_frozen, frozen_temp_path


if is_frozen:
    basedir = frozen_temp_path
else:
    basedir = os.path.dirname(os.path.abspath(__file__))

resource_dir = os.path.join(basedir, 'resources')


def init():
    session_requests = requests.session()

    file_path = os.path.join(resource_dir, 'uber_session')
    exists = os.path.isfile(file_path)
    if exists:
        with open(file_path, 'rb') as f:
            #print("load session")
            session_requests.cookies = pickle.load(f)

    #for cookie in session_requests.cookies:
        #print(cookie.name, cookie.value)

    return session_requests


def checkLoggedin(session_requests):
    '''
    Try getting data to check logged in
    :param session_requests: the session requests
    :return: None if not logged in, and some data if already logged in
    '''
    url = 'https://partners.uber.com/p3/payments/weekly-earnings/'

    result = session_requests.get(
        url,
        allow_redirects=True
    )

    print(result.status_code)
    #print(result.text)

    url = "https://partners.uber.com/p3/payments/api/fetchWeeklyEarnings"
    payload = {"weekOffset": 0}
    header = {
        "Referer": "https://partners.uber.com/p3/payments/weekly-earnings/",
        "Origin": "https://partners.uber.com",
        "x-csrf-token": 'x',
    }

    result = session_requests.post(
        url,
        data=payload,
        headers=header,
    )

    if 'html' in result.headers['Content-Type']:
        return None

    uberWeeklyData = parsingData.uberWeeklyParsing(result.json())
    print(uberWeeklyData)

    return uberWeeklyData


def loginReq(session_requests):
    # auth
    login_url = "https://auth.uber.com/login/?next_url=https://partners.uber.com/p3/payments/weekly-earnings/"

    result = session_requests.get(login_url)
    #print(result.headers)
    print(result.status_code)

    while result.status_code != 200:
        result = session_requests.get(login_url)

    tree = html.fromstring(result.content)

    script = tree.xpath('//script/text()')
    object = json.loads(script[1])
    token = object['state']['bedrock']['csrfToken']
    site_key = object['state']['config']['recaptchaSiteKey']

    output = {"token": token, "site_key": site_key, "login_url": login_url}

    return output


def phone_submit(session_requests, token, phoneNum):
    payload = {
        "answer": {
            "type":"VERIFY_INPUT_MOBILE",
            "userIdentifier":{
                "mobile":{
                    "countryCode":"1",
                    "phoneNumber": phoneNum
                }
            }
        },
        "init":True
    }

    header = {
            "Origin": "https://auth.uber.com",
            "x-csrf-token": token,
            "Host": "auth.uber.com",
            "content-type": "application/json",
            "Accept": "application/json",
    }

    result = session_requests.post(
        "https://auth.uber.com/login/handleanswer",
        json = payload,
        headers = header
    )

    #print(result.headers)
    print(result.status_code)
    print(result.text)

    if result.status_code == 200:
        return 1
    elif result.status_code == 429: # recaptcha
        return 0
    else:
        return -1


def token_submit(session_requests, token, phoneNum, recaptcha_token):
    payload = {
        "answer": {
            "type":"VERIFY_INPUT_MOBILE",
            "userIdentifier":{
                "mobile":{
                    "countryCode":"1",
                    "phoneNumber": phoneNum
                }
            }
        },
        "g-recaptcha-response": recaptcha_token,
        "init":True
    }

    header = {
            "Origin": "https://auth.uber.com",
            "x-csrf-token": token,
            "Host": "auth.uber.com",
            "content-type": "application/json",
            "Accept": "application/json",
    }

    result = session_requests.post(
        "https://auth.uber.com/login/handleanswer",
        json = payload,
        headers = header
    )

    #print(result.headers)
    print(result.status_code)
    print(result.text)

    if result.status_code == 200:
        return True
    else:
        return False


def password_submit(session_requests, token, password):
    header = {
            "Origin": "https://auth.uber.com",
            "x-csrf-token": token,
            "Host": "auth.uber.com",
            "content-type": "application/json",
            "Accept": "application/json",
    }
    payload = {
        "answer":{
            "type":"VERIFY_PASSWORD",
            "password":password
        },
        "rememberMe":True
    }

    result = session_requests.post(
        "https://auth.uber.com/login/handleanswer",
        json = payload,
        headers = header
    )

    #print(result.headers)
    print(result.status_code)
    print(result.text)

    #for cookie in session_requests.cookies:
        #print(cookie.name, cookie.value)

    if result.text.find('SMS_OTP') >= 0:
        return 'SMS_OTP' #further authenticationr required
    else:
        return None


def code_submit(session_requests, token, code):
    header = {
            "Origin": "https://auth.uber.com",
            "x-csrf-token": token,
            "Host": "auth.uber.com",
            "content-type": "application/json",
            "Accept": "application/json",
    }

    payload = {
        "answer": {
            "type": "SMS_OTP",
            "smsOTP": code
        },
    }
    result = session_requests.post(
        "https://auth.uber.com/login/handleanswer",
        json=payload,
        headers=header
    )
    #print(result.headers)
    print(result.status_code)
    print(result.text)

    if result.status_code == 200:
        return True
    else:
        return False


def fetch_data(session_requests, startDate):
    dateList = dateCalculate.calculateUberDate(startDate) #last monday date

    url = 'https://partners.uber.com/p3/payments/weekly-earnings/'

    result = session_requests.get(
        url,
        allow_redirects=True
    )
    print(result.status_code)
    print(result.text)
    uberWeeklyData = {}

    for date in dateList:
        url = "https://partners.uber.com/p3/payments/api/fetchWeeklyEarnings"
        payload = {"weekOffset": date}
        header = {
            "Referer": "https://partners.uber.com/p3/payments/weekly-earnings/",
            "Origin": "https://partners.uber.com",
            "x-csrf-token": 'x',
        }

        result = session_requests.post(
            url,
            data=payload,
            headers=header,
        )

        uberWeeklyData.update(parsingData.uberWeeklyParsing(result.json()))

    print(uberWeeklyData)
    return uberWeeklyData


def save_session(session_requests):
    #for cookie in session_requests.cookies:
        #print(cookie.name, cookie.value)

    file_path = os.path.join(resource_dir, 'uber_session')
    with open(file_path, 'wb') as f:
        pickle.dump(session_requests.cookies, f)
