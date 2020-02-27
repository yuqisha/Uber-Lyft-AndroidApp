# ECS193-Script

## Execuatbles are on google drive.
https://drive.google.com/drive/u/0/folders/1mYmQMXH-_7NsKbNdJbQoGBw1556M_G_W

## Run
Put web.app(Mac) / web(Windows) in resources/browser for uber-lyft.py to run

## Pyinstaller
pip install pyinstaller

### Web-browser
Inside Web-browser folder, web.py contains very simple PyQt5 browser with PyQtWebEngine.

Inside web-browser folder  
Pyinstaller -w -F web.py (Windows)

Before using the .spec, change path to current path. 
Pyinstaller web.spec (Mac)

### Uber-Lyft Script
Inside Uber-Lyft Script  
uber-lyft.py: main script  
database.py: calling functions to modifty or get info from database  
dataCalculate.py: dealing with get datelist and format into different format for database and making requests. 
lyftRequest.py: dealing with lyft requests  
uberRequest.py: dealing with uber requests, but only getting data part is used  
openBrowser.py: dealing with uber login by opening the browser and loading cookies from the browser  
parsingData.py: parsing uber/lyft into same format  
utils.py: code to deal with packaging application  

lyftData.json: sample lyft data  
uberData.json: sample uber data. 

Before using the .spec, change path to current path  
Pyinstaller uber-lyft-windows.spec (Windows)  
Pyinstaller uber-lyft.spec (Mac)

### Show-data Script
Have two extra scripts:  
showData.py can pull whole database data into data.json file. (data.json is an example data file)  
dayData.py can visualize one user with uid and its one day data on a map. (map.html is an example map file)


