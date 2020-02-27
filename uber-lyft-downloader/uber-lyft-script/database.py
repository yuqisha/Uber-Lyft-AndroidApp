import requests
import dateCalculate


def check_email(email):
    """
    check email if valid
    :param email: email to check
    :return: uid if exists, otherwise return -1
    """
    url = 'https://us-central1-lyft-uber.cloudfunctions.net/checkEmail'
    data = {
        'email': email
    }
    headers = {
        'Content-Type': 'application/json',
    }
    result = requests.post(url, json=data, headers=headers)

    return result.json()['uid']


# weeklyData = {"type": type, "data": data}
def send_data(uid, date, weeklyData):
    data = weeklyData['data']
    data_type = weeklyData['type']

    date_list = dateCalculate.calculateDate(date)

    for date in date_list:
        send_one_day(uid, data_type, date, data[date])


def send_one_day(uid, data_type, date, dailyData):
    url = 'https://us-central1-lyft-uber.cloudfunctions.net/sendData'

    headers = {
        'Content-Type': 'application/json',
    }
    data = {'data': dailyData, 'uid': uid, 'date': date, 'type': data_type}
    result = requests.post(url, json=data, headers=headers)

    print(result.text)


def combine_data(uid, date):
    date_list = dateCalculate.calculateDate(date)
    # date_list = ['05-23-2019']
    for index, date in enumerate(date_list):
        combine_one_day(uid, date)


def combine_one_day(uid, date):
    url = 'https://us-central1-lyft-uber.cloudfunctions.net/combineData'
    headers = {
        'Content-Type': 'application/json',
    }
    data = {'uid': uid, 'date': date}
    _ = requests.post(url, json=data, headers=headers)
