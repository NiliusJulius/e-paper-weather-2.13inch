import os
import sys
import logging
import time
import requests
import json
import math
from PIL import Image, ImageFont, ImageDraw
from lib.waveshare_epd import epd2in13b_V3

sys.path.append(os.path.dirname(__file__))

weatherAPIList = ["accuWeather", "openWeatherMap"]
weatherAPI = weatherAPIList[1]

debugMode = 0
useWeatherAPI = 1

logging.basicConfig(filename="e-paper-weather.log", level=logging.DEBUG, format='%(process)d-%(levelname)s-%(message)s')
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

# Read config file
with open("config.json", "r") as config_file:
    config = json.load(config_file)

# Initiate the e-paper driver
epd = epd2in13b_V3.EPD()
# We want to use it in a vertical position, so we switch the width and height
screenHeight = epd.width
screenWidth = epd.height

# Refresh time
if weatherAPI == weatherAPIList[0]:
    refreshTime = 60 * 60
else:
    refreshTime = 60 * 15

icons_list_accu = {1: 'B', 2: 'H', 3: 'H', 4: 'H', 5: 'J', 6: 'N', 7: 'Y', 8: 'Y', 11: 'M', 12: 'Q', 13: 'Q', 14: 'Q',
                   15: 'P', 16: 'P', 17: 'P', 18: 'R', 19: 'U', 20: 'U', 21: 'U', 22: 'W', 23: 'W', 24: 'W', 25: 'W',
                   26: 'X', 29: 'X', 30: '\'', 31: '\'', 32: 'F', 33: 'C', 34: 'I', 35: 'I', 36: 'I', 37: 'K', 38: 'N',
                   39: 'Q', 40: 'Q', 41: 'P', 42: 'P', 43: 'U', 44: 'U'}
icons_list_owm = {"01d": 'B', "01n": 'C', "02d": 'H', "02n": 'I', "03d": 'N', "03n": 'N', "04d": 'Y', "04n": 'Y',
                  "09d": 'R', "09n": 'R', "10d": 'R', "10n": 'R', "11d": 'P', "11n": 'P', "13d": 'W', "13n": 'W',
                  "50d": 'M', "50n": 'M'}


def main():
    if debugMode == 1:
        logging.info("Debug Mode")

    start_time = time.time()

    while True:
        if (time.time() - start_time) > 0:
            refresh_screen()
            start_time = time.time() + refreshTime
        time.sleep(refreshTime)


def call_weather_api():
    logging.info("Ping Weather API")

    weather_response = None
    forecast_response = None

    try:
        if useWeatherAPI == 1:
            api_key = config["API"][weatherAPI]["APIKey"]

            if weatherAPI == weatherAPIList[0]:
                location_key = config["API"][weatherAPI]["locationKey"]

                weather_response = requests.get("http://dataservice.accuweather.com/currentconditions/v1/"
                                                + location_key,
                                                params={"apikey": api_key}).json()
                forecast_response = requests.get("http://dataservice.accuweather.com/forecasts/v1/daily/1day/"
                                                 + location_key,
                                                 params={"apikey": api_key, "metric": "true"}).json()
            elif weatherAPI == weatherAPIList[1]:
                lat = config["API"][weatherAPI]["lat"]
                lon = config["API"][weatherAPI]["lon"]

                weather_response = requests.get("https://api.openweathermap.org/data/2.5/onecall",
                                                params={"lat": lat, "lon": lon, "exclude": "minutely,hourly,alerts",
                                                        "units": "metric", "appid": api_key}).json()
        else:
            if weatherAPI == weatherAPIList[0]:
                with open("json/accu_current.json") as current_json:
                    weather_response = json.load(current_json)
                with open("json/accu_forecast.json") as forecast_json:
                    forecast_response = json.load(forecast_json)
            elif weatherAPI == weatherAPIList[1]:
                with open("json/openWeatherMap.json") as owm_json:
                    weather_response = json.load(owm_json)

    except Exception as error:
        logging.error("Weather API JSON Failed")
        logging.exception(error)
        time.sleep(refreshTime)

    return weather_response, forecast_response


def refresh_screen():
    logging.info("General Refresh")

    if debugMode == 0:
        epd.init()

    # Font which uses weather icons
    font_weather_icons = ImageFont.truetype("fonts/meteocons-webfont.ttf", 45)
    # Bitmap font which displays correctly without anti-aliasing, size should be multiples of 16
    font_weather = ImageFont.truetype("fonts/Minecraft.ttf", 16)

    # Create empty image to store the black color on
    black_image = Image.new("1", (screenWidth, screenHeight), 255)
    draw_black = ImageDraw.Draw(black_image)

    # Create empty image to store the red color on
    color_image = Image.new("1", (screenWidth, screenHeight), 255)
    draw_color = ImageDraw.Draw(color_image)

    # Call the weather API and grab relevant info
    weather_response, forecast_response = call_weather_api()
    if weatherAPI == weatherAPIList[0]:
        icons_list = icons_list_accu
        current_icon = weather_response[0]["WeatherIcon"]
        current_temp = weather_response[0]["Temperature"]["Metric"]["Value"]
        forecast_icon = forecast_response["DailyForecasts"][0]["Day"]["Icon"]
        forecast_temp_min = forecast_response["DailyForecasts"][0]["Temperature"]["Minimum"]["Value"]
        forecast_temp_max = forecast_response["DailyForecasts"][0]["Temperature"]["Maximum"]["Value"]
    else:
        icons_list = icons_list_owm
        current_icon = weather_response["current"]["weather"][0]["icon"]
        current_temp = round(weather_response["current"]["temp"], 1)
        forecast_icon = weather_response["daily"][0]["weather"][0]["icon"]
        forecast_temp_min = round(weather_response["daily"][0]["temp"]["min"], 1)
        forecast_temp_max = round(weather_response["daily"][0]["temp"]["max"], 1)

    logging.debug("Icons needed: " + str(current_icon) + " and " + str(forecast_icon))

    # Create string for temperatures
    current_temp_str = str(current_temp) + "C"
    forecast_temp_divider = " / "
    forecast_temp_min_max = str(forecast_temp_min) + "C" + forecast_temp_divider + str(forecast_temp_max) + "C"
    forecast_temp_min_str = str(forecast_temp_min) + "C"
    forecast_temp_max_str = str(forecast_temp_max) + "C"

    # Determine which image to draw the temperature on (temperatures above 20 will go to the colored image)
    draw_current_temp = draw_black if current_temp < 20 else draw_color
    draw_forecast_temp_min = draw_black if forecast_temp_min < 20 else draw_color
    draw_forecast_temp_max = draw_black if forecast_temp_max < 20 else draw_color

    # Determines widths and heights for all image objects which is used to position them correctly later on
    w_weather_icon, h_weather_icon = font_weather_icons.getsize(icons_list[current_icon])
    w_current_temp, h_current_temp = font_weather.getsize(current_temp_str)
    arrow_half_height = 4
    arrow_body_width = 8
    arrow_head_width = 8
    arrow_spacing = 5
    w_forecast_temp_min_max, h_forecast_temp_min_max = font_weather.getsize(forecast_temp_min_max)
    w_forecast_temp_min, h_forecast_temp_min = font_weather.getsize(forecast_temp_min_str)
    w_forecast_temp_divider, h_forecast_temp_divider = font_weather.getsize(forecast_temp_divider)
    if w_weather_icon > w_current_temp:
        w_current = w_weather_icon
    else:
        w_current = w_current_temp

    # Offset between the weather icon and the temperature
    icon_temp_height_offset = 1

    # Determines the total width and offset to center the image
    total_width = w_current + arrow_spacing + arrow_body_width + arrow_head_width + arrow_spacing \
        + w_forecast_temp_min_max
    width_offset = (screenWidth - total_width) / 2

    # Determines the total height and offset to center the image
    total_height = h_weather_icon + 2 * icon_temp_height_offset + h_current_temp
    height_offset = math.floor((screenHeight - total_height) / 2)

    # Determines where to place the current weather icon
    x_current_icon = width_offset + w_current / 2 - w_weather_icon / 2
    y_weather_icon = height_offset

    # Determines where to place the current weather temperature
    x_current_temp = width_offset + w_current / 2 - w_current_temp / 2
    y_temp = screenHeight - height_offset - h_current_temp

    # Determines where to place the arrow icon
    x_arrow_symbol = x_current_temp + w_current_temp + arrow_spacing  # Location of the arrow to be displayed
    y_arrow_symbol = y_weather_icon + h_weather_icon + icon_temp_height_offset

    # Determines where to place the forecast weather icon, minimum and maximum temperature
    x_forecast_temp_min = x_arrow_symbol + arrow_body_width + arrow_head_width + arrow_spacing
    x_forecast_temp_divider = x_forecast_temp_min + w_forecast_temp_min
    x_forecast_temp_max = x_forecast_temp_divider + w_forecast_temp_divider
    x_forecast_icon = x_forecast_temp_min + w_forecast_temp_min_max / 2 - w_weather_icon / 2

    # Draw the current weather icon
    draw_black.text((x_current_icon, y_weather_icon), icons_list[current_icon], font=font_weather_icons, fill=0)

    # Draw the current temperature
    draw_current_temp.text((x_current_temp, y_temp), current_temp_str, font=font_weather, fill=0)

    # Draw the arrow
    draw_black.rectangle((x_arrow_symbol, y_arrow_symbol - arrow_half_height, x_arrow_symbol + arrow_body_width,
                          y_arrow_symbol + arrow_half_height), fill=0)
    draw_black.polygon([x_arrow_symbol + arrow_body_width, y_arrow_symbol - 2 * arrow_half_height,
                        x_arrow_symbol + arrow_body_width + arrow_head_width, y_arrow_symbol,
                        x_arrow_symbol + arrow_body_width, y_arrow_symbol + 2 * arrow_half_height],
                       fill=0)

    # Draw the forecast weather icon
    draw_black.text((x_forecast_icon, y_weather_icon), icons_list[forecast_icon], font=font_weather_icons, fill=0)

    # Draw the forecast minimum and maximum temperature
    draw_forecast_temp_min.text((x_forecast_temp_min, y_temp), forecast_temp_min_str, font=font_weather, fill=0)
    draw_black.text((x_forecast_temp_divider, y_temp), forecast_temp_divider, font=font_weather, fill=0)
    draw_forecast_temp_max.text((x_forecast_temp_max, y_temp), forecast_temp_max_str, font=font_weather, fill=0)

    if debugMode == 1:
        logging.info("Saving images to drive")
        black_image.save("Black.bmp")
        color_image.save("Red.bmp")
    else:
        logging.info("Writing to the e-paper")
        epd.display(epd.getbuffer(black_image), epd.getbuffer(color_image))
        logging.info("e-paper entering sleep mode")
        epd.sleep()

    logging.info("Done")


if __name__ == '__main__':
    try:
        main()

    except Exception as e:
        logging.exception(e)

    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        if debugMode == 0:
            epd.Dev_exit()
        exit()
