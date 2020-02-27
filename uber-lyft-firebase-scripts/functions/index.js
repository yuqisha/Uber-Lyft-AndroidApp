const functions = require('firebase-functions');
const admin = require('firebase-admin');

const geolib = require('geolib');
const moment = require('moment');
var serviceAccount = require("./serviceAccountKey.json");

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
});

/*
 * This function is to check if email belongs to a user
 * Send uid if found, otherwise return None
 * Return 200 for valid, 404 for invalid
 */
exports.checkEmail = functions.https.onRequest((request, response) => {
    const data = request.body
    console.log(request.body)
    console.log(data.email)
    
    admin.auth().getUserByEmail(data.email)
    .then((userRecord) => {
        // See the UserRecord reference doc for the contents of userRecord.
        console.log('success');
        const uid = userRecord.toJSON().uid
        return response.send({uid})
    })
    .catch((error) => {
        console.log('Error fetching user data:', error);
        return response.status(404).send({uid: null})
    });
});


exports.sendData = functions.https.onRequest((request, response) => {
    const fullData = request.body
    const daily = fullData.data
    const uid = fullData.uid
    const type = fullData.type
    const date= fullData.date

    console.log(daily)
    console.log(uid)
    console.log(date)

    const daysRef = admin.firestore().collection('Users').doc(uid).collection('Days')
    const data = {}
    data[type + 'data'] = daily
    data[type] = true
    daysRef.doc(date).set(data, {merge: true}).then(() => {
        return response.status(200).send(daily)
    }).catch((err) => {
        return response.status(400).send(err)
    })
    
});

function combineBoth(data1, data2) {
    // data1 = uber
    // data2 = lyft
    let result = []
    const length = data1.length + data2.length
    let i1 = 0, i2 = 0, index = 0, data
    while (index < length) {
        if (i1 < data1.length && i2 < data2.length) {
            if (data1[i1].pickupAt < data2[i2].pickupAt) {
                data = data1[i1]
                data.type = 'uber'
                result.push(data)
                i1++
            } 
            else {
                data = data2[i2]
                data.type = 'lyft'
                result.push(data)
                i2++
            }
        }
        else if (i1 < data1.length) {
            data = data1[i1]
            data.type = 'uber'
            result.push(data)
            i1++
        }
        else if (i2 < data2.length) {
            data = data2[i2]
            data.type = 'lyft'
            result.push(data)
            i2++
        }

        index++
    }
    return result
}

async function generateEvents(data, locations) {
/* 
* data:[{
    'pickupAt': 1557563722, 
    'duration': 570, 
    'dropoffAt': 1557564292, 
    'distance': 3.05, 
    'type': 'uber'}] 
* locations: [{
    latitude,
    longitude,
    time,(seconds)
    speed}]
* return: events: [{
    eventType, (trip or inter)
    type,
    startTime,
    startLocation,
    endTime,
    endLocation,
    duration,
    distanceCompute,
    distanceReal
    }]
*/
    let events = []
    let trip
    let i = 0
    for (trip of data) {
        const startTime = trip.pickupAt
        const endTime = trip.dropoffAt
        // find trip start index
        let index = findIndex(startTime, locations, i)
        if (index < 0) {
            console.error("trip doesn't exist")
            return events
        }
        // generate event before trips
        let event = await generateEvent(i, index, null, 'inter', locations, null)
        events.push(event)
        i = index

        // find trip end index
        index = findIndex(endTime, locations, i)
        if (index < 0) {
            console.error('no end point found')
            index = locations.length-1
        }

        event = await generateEvent(i, index, trip.type, 'trip', locations, trip.distance)
        events.push(event)
        i = index
    }
    if (i < locations.length - 1) {
        let event = await generateEvent(i, locations.length - 1, null, 'inter', locations, null)
        events.push(event)
    }

    return events
}

async function generateEvent(start, end, type, eventType, locations, distance) {
    let event = {}
    event['type'] = type
    event['eventType'] = eventType
    event['startTime'] = locations[start].time
    let location = {}
    location.latitude = locations[start].latitude
    location.longitude = locations[start].longitude
    event['startLocation'] = location
    event['endTime'] = locations[end].time
    // add snap to road
    const locationList = makeLocationList(start, end, locations)
    let snappedList = []
    try {
        await refinedata(locationList)
        snappedList = snapedLocationList
        console.log(snappedList)
    }
    catch (err) {
        console.log("Wrong:" + err)
    }
    console.log({snappedList: snappedList.length})
    let dist = 0
    const finalList = snappedList.length === 0 ? locationList: snappedList
    //console.log(finalList)
    event['locations'] = finalList
    let i = 0
    for (i in finalList) {
        if (Number(i) + 1 < finalList.length) {
            const loc1 = {}, loc2 = {}
            loc1["latitude"] = finalList[i].latitude
            loc1["longitude"] = finalList[i].longitude
            loc2["latitude"] = finalList[Number(i) + 1].latitude
            loc2["longitude"] = finalList[Number(i) + 1].longitude

            dist += geolib.getDistance(
                {latitude: loc1.latitude, longitude: loc1.longitude},
                {latitude: loc2.latitude, longitude: loc2.longitude}
            );
        }
    }

    dist *= 0.00062137
    event['distanceCompute'] = dist

    location = {}
    location.latitude = locations[end].latitude
    location.longitude = locations[end].longitude
    event['endLocation'] = location
    event['distanceReal'] = distance
    return event
}

function makeLocationList(start, end, locations) {
    locationList = []
    for (let i = start; i <= end; i++) {
        locationList.push(locations[i])
    }
    return locationList
}

function findIndex(startTime, locations, startIndex) {
    for (let i = startIndex; i < locations.length; i++) {
        if (locations[i].time >= startTime) {
            if (i === 0) {
                console.log(i)
                return i
            }
            const diff1 = startTime - locations[Number(i)-1].time
            const diff2 = locations[i].time - startTime
            return diff1 < diff2 ? Number(i)-1 : i
        }
    }
    return -1
}

// test function hard coding way getting data
exports.combineData = functions.https.onRequest((request, response) => {
    const uid = request.body.uid
    const date = request.body.date

    const dayRef = admin.firestore().doc('/Users/' + uid + '/Days/' + date)
    //const dayRef = admin.firestore().doc('/Users/kv0gnRUbhRaEAuquUVJ9tBqRsSB3/Days/05-21-2019')

    var transaction = admin.firestore().runTransaction(t => {
        return t.get(dayRef)
            .then(async (snapshot) => {
                const data = snapshot.data()
                // get uber/lyftdata
                
                const uberData = data.uberdata
                const lyftData = data.lyftdata
                const lyft = data.lyft
                const uber = data.uber

                /*
                const uberData = [{'pickupAt': 1557563722, 'duration': 30, 'dropoffAt': 1557563752, 'distance': 3.05}]

                const lyftData = [{'pickupAt': 1557563772, 'duration': 40, 'dropoffAt': 1557563812, 'distance': 3.05}, {'pickupAt': 1557563852, 'duration': 45, 'dropoffAt': 1557563897, 'distance': 6.07}]
                */
                /*const uberData = [{'pickupAt': 1558479504, 'duration': 51, 'dropoffAt': 1558479555, 'distance': 0.1}]

                const lyftData = []

                const lyft = true
                const uber = true
                */

                let allData = null
                if (lyft && uber) {
                    allData = combineBoth(uberData, lyftData)
                } else if (lyft) {
                    allData = lyftData
                } else if (uber) {
                    allData = uberData
                }

                console.log(allData)

                // get locations
                const locations = data.locations
                if (locations === null) {
                    console.log('no locations')
                    return response.status(400).send('no locations')
                }
                console.log('change locations time format')
                for (let i in locations) {
                    locations[i].time = locations[i].time._seconds
                }
                const events = await generateEvents(allData, locations)
                const process = true

                console.log({events, process})
                await t.update(dayRef, {events, process});

                return response.status(200).send({events, process})
            }).catch((err) => {
                return response.status(400).send(err)
            })
    
    });
});

/*
 * This function is to check the last date to get data
 * Send date if found, otherwise return None
 * Return 200 for valid, 404 for invalid
 */
exports.checkDate = functions.https.onRequest((request, response) => {
    const data = request.body
    console.log(request.body)
    console.log(data.uid)
    const today = moment().format("MM-DD-YYYY");
    console.log(today)
    
    const dateList = []

    admin.firestore().collection('Users')
    .doc(data.uid)
    .collection('Days')
    .orderBy('date', 'asc')
    .get()
    .then((snapshot) => {
        for (let doc of snapshot.docs) {
            const date = doc.id
            if (!doc.data().process){
                // comment next line for testing
                if (date !== today)
                    dateList.push(date)
            }
        }

        response.status(200).send({dateList})
        return 200
    })
    .catch((err) => {
        console.log(err)
        response.status(404).send({date: null});
        return 404
    })
    
});

var snaplist = []
var timelist = []
var snapedLocationList = []
const apiKey = 'AIzaSyCLB_aVHRJJVh7dTyqlTVpwEI1JoRHhApI';
const request = require('request');

function doRequest(url) {
    return new Promise((resolve, reject) => {
      request(url, (error, res, body) => {
        if (!error && res.statusCode === 200) {
          resolve(body);
        } else {
          reject(error);
        }
      });
    });
  }
  

const sendreq = async (index, pathlist, times) => {
    let cnt = 0;
    //console.log("i" + index)
    const requestUrl = 'https://roads.googleapis.com/v1/snapToRoads?path=' + pathlist[index].join('|') + '&interpolate=true&key=' + apiKey
    console.log(requestUrl)
    try {
        let response = await doRequest(requestUrl)
        
        const js = JSON.parse(response)        

        var snappoint;
        for (snappoint of js.snappedPoints) {   
            var d = { latitude: snappoint.location.latitude, longitude: snappoint.location.longitude}
            snapedLocationList.push(d)
        }

        console.log(JSON.stringify(snapedLocationList))
        console.log('finished')
        return true
    } catch (err) {
        console.log("Wrong:" + err)
        return false
    }
}

const refinedata = async (locations) => {
    var cnt = 0

    var location
    var pathValues = []
    var eachtime = []
    snapedLocationList = []
    snaplist = []
    eachloc = 0;
    //index = 0;
    for (location of locations) {
        pathValues.push(location.latitude + "," + location.longitude)
        eachtime.push(location.time)
        cnt += 1
        if (cnt === 50) {
            eachloc++;
            cnt = 0
            snaplist.push(pathValues)
            timelist.push(eachtime)
            pathValues = []
            eachtime = []
        }
    }

    if (cnt !== 0) {
        snaplist.push(pathValues)
        timelist.push(eachtime)
        eachloc++;
    }

    //console.log(pathValues);
    console.log(cnt + "," + eachloc);
    console.log(snaplist);
    //console.log(timelist)
    var index = 0;
    for (index = 0; index < snaplist.length; index++) {
        try {
            await sendreq(index, snaplist, timelist)
        }
        catch (err) {
            console.log("Wrong:" + err)
        }
    }
    return snapedLocationList
}
let allData = {}
exports.getAllData = functions.https.onRequest(async(request, response) => {
    userIds = []
    allData = {}
    await listAllUsers();
    console.log('finish getting users')
    for (let uid of userIds) {
        const daysRef = await admin.firestore().collection('Users').doc(uid).collection('Days').get()
        if (!daysRef) {
            continue
        }
        let daysData = {}
        for (let doc of daysRef.docs) {
            const dayRef = await admin.firestore().collection('Users')
                .doc(uid).collection('Days').doc(doc.id).get()
            if (!dayRef) {
                continue
            }
            if (!dayRef.data()) {
                console.log('No such document!');
            } else {
                console.log('Document data:', doc.id);
                daysData[doc.id] = dayRef.data()
            }
        }
        allData[uid] = daysData
    }
    response.send(allData)
})

let userIds = []
async function listAllUsers(nextPageToken) {
    // List batch of users, 1000 at a time.
    let listUsersResult = await admin.auth().listUsers(1000, nextPageToken)
    for (let user of listUsersResult.users) {
        userIds.push(user.uid)
    }

    if (listUsersResult.pageToken) {
        await listAllUsers(listUsersResult.pageToken);
    }
}