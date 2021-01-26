[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.7.3-blue)](https://www.python.org/)
# 2.13 inch e-paper weather application
A python application to show the weather on a Waveshare 2.13 inch e-paper three color (black, white, red/yellow) module connected to a raspberry pi.

This program interacts with the [accuweather API](https://developer.accuweather.com/), or the [openweathermap API](https://openweathermap.org/api) in order to retriever weather data.
It collects the current weather and the forecast for tomorrow (every hour for accuweather and every 15 minutes otherwise). This means it will work with the free plan of the supported APIs.

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

### Set config file and other configuration
In the config.json file are 2 properties which you need to fill for the API you plan on using.
Create an account on [accuweather](https://developer.accuweather.com/) or [openweathermap](https://openweathermap.org/api), a free one will do just fine.
Place your API key in the config file.
For accuweather, use their locations API to find your location key (for example by [searching for a city](https://developer.accuweather.com/accuweather-locations-api/apis/get/locations/v1/cities/search)).
For openweathermap, you need to find your lat, long info (for example by looking it up in Google Maps).

In main.py, you will find something like this
```python
weatherAPIList = ["accuWeather", "openWeatherMap"]
weatherAPI = weatherAPIList[1]
```
Change the number to the corresponding number of the API you want to use. In this case we are using openWeatherMap.

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