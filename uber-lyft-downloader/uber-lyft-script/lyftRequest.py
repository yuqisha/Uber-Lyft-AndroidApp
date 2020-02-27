# importing the requests library
import requests, pickle, os, dateCalculate, parsingData
from utils import resource_dir


def init():
    session_requests = requests.session()

    file_path = os.path.join(resource_dir, 'session')

    exists = os.path.isfile(file_path)
    if exists:
        with open(file_path, 'rb') as f:
            print('load sessions')
            session_requests = pickle.load(f)


    for cookie in session_requests.cookies:
        print(cookie.name, cookie.value)

    return session_requests


def loginReq(session_requests):
    # auth
    login_url = "https://account.lyft.com/auth"
    result = session_requests.get(login_url)

    print(result.headers)
    print(result.status_code)


    while result.status_code != 200:
        # auth
        login_url = "https://account.lyft.com/auth"
        result = session_requests.get(login_url)

        print(result.headers)
        print(result.status_code)


headers = {
    "Authorization": "Basic d0dldWh3RE5MNmNwOllicHpIdnN0Y1E2UW1NTWZlUVJ2dnI1ZUl0UTI5S1JR",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Lyft-Version": "2017-09-18",
    "X-Authorization":"Basic d0dldWh3RE5MNmNwOllicHpIdnN0Y1E2UW1NTWZlUVJ2dnI1ZUl0UTI5S1JR",
    "referer":"https://account.lyft.com/"
}


def access_token1(session_requests):
    payload = {
        "grant_type": "client_credentials"
    }

    # get access token
    access = "https://api.lyft.com/oauth2/access_token"

    result = session_requests.post(
        access,
        data = payload,
        headers = headers
    )

    print(result.headers)
    print(result.status_code)

    while result.status_code != 200:
        payload = {
            "grant_type": "client_credentials"
        }

        # get access token
        access = "https://api.lyft.com/oauth2/access_token"

        result = session_requests.post(
            access,
            data=payload,
            headers=headers
        )

        print(result.headers)
        print(result.status_code)


def phoneauth1(session_requests):
    result = session_requests.options(
        'https://api.lyft.com/v1/phoneauth',
        headers = headers
    )

    print(result.headers)
    print(result.status_code)

    while result.status_code != 200:
        result = session_requests.options(
            'https://api.lyft.com/v1/phoneauth',
            headers=headers
        )

        print(result.headers)
        print(result.status_code)


def phoneauth2(phoneNum, session_requests):
    payload = {"phone_number": "+1" + phoneNum,"extend_token_lifetime": False}
    headers = {
        "referer":"https://account.lyft.com/",
        "content-type": "application/json"
    }

    result = session_requests.post(
        'https://api.lyft.com/v1/phoneauth',
        json=payload,
        headers = headers
    )

    print(result.headers)
    print(result.text)

    if result.status_code == 202:
        return True
    else:
        return False


def access_token2(session_requests, phoneNum, code):
    headers = {
                "Authorization": "Basic d0dldWh3RE5MNmNwOllicHpIdnN0Y1E2UW1NTWZlUVJ2dnI1ZUl0UTI5S1JR",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Lyft-Version": "2017-09-18",
                "X-Authorization":"Basic d0dldWh3RE5MNmNwOllicHpIdnN0Y1E2UW1NTWZlUVJ2dnI1ZUl0UTI5S1JR",
                "referer":"https://account.lyft.com/"
            }
    payload = {
        'grant_type':'urn:lyft:oauth2:grant_type:phone',
        'phone_code': code,
        'phone_number': '+1' + phoneNum
    }

    access = "https://api.lyft.com/oauth2/access_token"

    result = session_requests.post(
        access,
        data = payload,
        headers = headers
    )

    print(result.headers)
    print(result.status_code)
    print(result.text)

    for cookie in session_requests.cookies:
        print(cookie.name, cookie.value)

    if result.status_code == 401:
        return 1
    elif result.status_code == 200:
        return 0
    else:
        return -1


def access_token3(session_requests, phoneNum, code, licenseNum):
    headers = {
        "Authorization": "Basic d0dldWh3RE5MNmNwOllicHpIdnN0Y1E2UW1NTWZlUVJ2dnI1ZUl0UTI5S1JR",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Lyft-Version": "2017-09-18",
        "X-Authorization": "Basic d0dldWh3RE5MNmNwOllicHpIdnN0Y1E2UW1NTWZlUVJ2dnI1ZUl0UTI5S1JR",
        "referer": "https://account.lyft.com/"
    }

    payload = {
        "grant_type": "urn:lyft:oauth2:grant_type:phone",
        "drivers_license_number": licenseNum,
        #"email": licenseNum,
        "phone_code": code,
        "phone_number": "+1" + phoneNum
    }

    # get access token
    access = "https://api.lyft.com/oauth2/access_token"

    result = session_requests.post(
        access,
        data = payload,
        headers = headers
    )

    print(result.json())

    if result.status_code == 200:
        return True
    else:
        return False


def save_session(session_requests):
    file_path = os.path.join(resource_dir, 'session')

    with open(file_path, 'wb') as f:
        pickle.dump(session_requests, f)

    for cookie in session_requests.cookies:
        print(cookie.name, cookie.value)


def request_daily_data(session_requests, date):
    url = "https://www.lyft.com/api/driver_earnings_summary/"+ date +"?duration=day&line_items=all&timeframe=day"

    result = session_requests.get(
        url,
        headers=dict(referer='https://www.lyft.com/api/driver_earnings_summary/' + date)
    )

    print(result.headers)
    print(result.status_code)
    print(result.content)

    data = result.json()

    return data


def request_data(session_requests, startDate):
    dateList = dateCalculate.calculateLyftDate(startDate)
    lyftWeeklyData = {}
    for date in dateList:
        dailyData = request_daily_data(session_requests, date)
        lyftDaily = parsingData.lyftDailyParsing(dailyData) #list of trip data
        lyftWeeklyData.update(lyftDaily)

    return lyftWeeklyData
