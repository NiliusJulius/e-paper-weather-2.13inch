[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.7.3-blue)](https://www.python.org/)
# 2.13 inch e-paper weather application
A python application to show the weather on a Waveshare 2.13 inch e-paper three color (black, white, red/yellow) module connected to a raspberry pi.

This program interacts with the [accuweather API](https://developer.accuweather.com/) in order to retriever weather data.
It collects the current weather and the forecast for tomorrow every hour. This means it makes 48 API calls a day, and the free tier allows for 50 calls a day.

## Setup

### Prerequisites
* This was written on Python 3.7.3, but should probably work on any newer version as well.
* pip

Clone the repository
```
git clone https://github.com/NiliusJulius/e-paper-weather-2.13inch.git
```

### Install  python packages
```
pip install -r requirements.txt
```

### Set config file
In the config.json file are 2 properties which you need to fill.
Create an account on [accuweather](https://developer.accuweather.com/), a free one will do just fine.
Place your API key in the config file and use their locations API to find your location key (for example by [searching for a city](https://developer.accuweather.com/accuweather-locations-api/apis/get/locations/v1/cities/search))

## Test 
In order to test  whether the program is working, it can be configured to not pull from the API, but from a json file.
Open main.py and near the top you should see
```python
useWeatherAPI = 1
```
Change the 1 to a 0, and it will not call the accuweather API which is very useful on the free tier.

Another option you can set is 
```python
debugMode = 0
```
With debugMode set to 1, it will not try to write to the e-paper screen, but instead create two .bmp files called black.bmp and red.bpm.
These will contain what would normally be written to the screen in black and red (or yellow if you have a white, black and yellow screen) respectively.
For example:



Now you can run the program by simply calling
```
python main.py
```