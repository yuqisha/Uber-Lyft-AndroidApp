from datetime import datetime


def checkKey(dict, key):
    if key in dict.keys():
        return dict[key]
    else:
        return None


def lyftDailyParsing(data):
    '''
    This function is to parse lyft daily json
    :param data: data get from request
    '''
    lyft = data
    temp = checkKey(lyft, 'timeframes')
    if not temp:
        return []
    else:
        if not isinstance(temp, list):
            return []
        elif len(temp) == 0:
            return []
        else:
            temp = temp[0]
            if not temp['route_line_items']:
                return []
            else:
                temp = temp['route_line_items']

    dateObj = datetime.fromtimestamp(lyft['timeframes'][0]["start_ms"]/1000)
    date = dateObj.strftime('%m-%d-%Y')
    lyftTrips = temp
    lyftDaily = []
    for lyftTrip in lyftTrips:
        trip = {}
        trip['pickupAt'] = int(lyftTrip['created_at_ms']/1000)
        trip['duration'] = lyftTrip['metadata']['duration']
        trip['dropoffAt'] = trip['pickupAt'] + lyftTrip['metadata']['duration']
        trip['distance'] = lyftTrip['metadata']['route_distance']['value']
        lyftDaily.append(trip)
    lyftDailyList = {}
    lyftDailyList[date] = lyftDaily
    return lyftDailyList


def uberWeeklyParsing(data):
    '''
    This function is to parse uber paring weekly json
    :param data: data get from request
    '''
    uber = data
    uberTripCount = uber['data']['earnings']['tripStats']['tripCount']

    # get all uber trips in a week
    uberTrips = None
    if uberTripCount > 0:
        uberTrips = uber['data']['earnings']['trips']

    # get all uber days
    uberWeeklyRaw = uber['data']['earnings']['days']

    uberWeeklyList = {}
    for index, day in enumerate(uberWeeklyRaw):
        tripIds = day['tripUuids']
        daily = []
        for tripId in tripIds:
            trip = {}
            fullTrip = uberTrips[tripId]
            trip['pickupAt'] = fullTrip['pickupAt']
            trip['dropoffAt'] = fullTrip['dropoffAt']
            trip['duration'] = fullTrip['duration']
            trip['distance'] = fullTrip['distance']
            daily.append(trip)

        dateObj = datetime.fromtimestamp(day['summary']['startAt'])
        date = dateObj.strftime('%m-%d-%Y')
        uberWeeklyList[date] = daily

    return uberWeeklyList
