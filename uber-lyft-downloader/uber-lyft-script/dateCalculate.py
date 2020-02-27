from datetime import datetime
import requests


def calculateLyftDate(list):
    """
    Get a date list for requesting Lyft data
    :param list: date list in mm-dd-yyyy format
    :return: dateList in yyyy-mm-dd format
    """

    if len(list) is 0:
        return []

    dateList = []

    for date in list:
        dateItem = datetime.strptime(date, '%m-%d-%Y')
        dateList.append(dateItem.strftime('%Y-%m-%d'))

    return dateList


def calculateUberDate(list):
    """
    Get a date list for requesting Uber data
    :param date: starting date
    :return: dateList
    """
    if len(list) is 0:
        return []

    date = list[0]
    datetime_object = datetime.strptime(date, '%m-%d-%Y')
    dateObject = datetime(datetime_object.year, datetime_object.month, datetime_object.day)
    timeToMonday = dateObject.weekday() * 86400
    dateObjectSecond = dateObject.timestamp()

    dateMonday = dateObjectSecond - timeToMonday

    dateNow = datetime.now()
    dateToday = datetime(dateNow.year, dateNow.month, dateNow.day)

    timeToMonday = dateNow.weekday() * 86400
    dateTodaySecond = dateToday.timestamp()

    thisMonday = dateTodaySecond - timeToMonday

    dateList = []

    start = int(dateMonday)
    end = int(thisMonday)+86400 * 7

    for i in range(start,end,86400 * 7):
        dateItem = datetime.fromtimestamp(i)
        dateList.append(dateItem.strftime('%Y/%m/%d'))

    list = []
    for i in range(len(dateList)-1, -1, -1):
        list.append(i)

    return list


def calculateDate(dateList):
    """
    Get a date list for sending data to database
    :param dateList: the starting date
    :return: dateList
    """
    # recently changed, no process here
    return dateList


def getDate(uid):
    url = 'https://us-central1-lyft-uber.cloudfunctions.net/checkDate'
    data = {
        'uid': uid
    }
    headers = {
        'Content-Type': 'application/json',
    }
    result = requests.post(url, json=data, headers=headers)
    print(result.json())
    return result.json()['dateList']