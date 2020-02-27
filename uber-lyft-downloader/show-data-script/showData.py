import requests
import json


def getAllData():
    url = 'https://us-central1-lyft-uber.cloudfunctions.net/getAllData'

    result = requests.post(url)

    allUserData = result.json()

    with open('data.json', 'w') as data_file:
        json.dump(allUserData, data_file, indent=2)


getAllData()