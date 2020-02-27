import json, webbrowser, os
import folium

with open('data.json', 'r') as data_file:
    allUserData = json.load(data_file)

user = allUserData["1Di5ZlKvb8VkuO0mtDrIvw973xY2"]

day = user["05-23-2019"]

events = day['events']

init = True

color = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen'
    , 'cadetblue', 'darkpurple', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray']

colorInd = 0

my_map4 = folium.Map(location=[0, 0],
                     zoom_start=10)

for event in events:
    locs = []
    for loc in event['locations']:
        if init:
            my_map4 = folium.Map(location=[loc['latitude'], loc['longitude']],
                                 zoom_start=10)
            init = False
        locs.append((loc['latitude'], loc['longitude']))
        folium.CircleMarker((loc['latitude'], loc['longitude']), radius = 1, color = color[colorInd]).add_to(my_map4)

    folium.PolyLine(locations=locs, line_opacity=0.5, color=color[colorInd]).add_to(my_map4)

    if colorInd + 1 < len(color):
        colorInd += 1
    else:
        colorInd = 0


# Add a line to the map by using line method .
# it connect both coordiates by the line
# line_opacity implies intensity of the line


my_map4.save("map.html")

webbrowser.open_new('file://'+ os.path.realpath("map.html"))
