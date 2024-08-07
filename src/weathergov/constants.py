from enum import Enum, unique


"""
    This file contains static constants that must not be updated externally
"""

# This is App's name it is unique as much as possible
# We are going to use this name in:
#   1. User-Agent information when send a request to Weather.gov
APP_NAME = "Weather:a2e2dfa19d6c45d6a92860933322c847"

MISSING_VALUE = -99911999


class Environment(Enum):
    LOCAL = "Local"
    AWS = "AWS"


@unique
class Metrics(str, Enum):
    Temperature = "temperature"
    DewPoint = "dew_point"
    WindDirection = "wind_direction"
    WindSpeed = "wind_speed"
    WindGust = "wind_gust"
    BarometricPressure = "barometric_pressure"
    SeaLevelPressure = "sea_level_pressure"
    Visibility = "visibility"
    Precipitation3h = "precipitation_last_3h"
    RelativeHumidity = "relative_humidity"
    WindChill = "wind_chill"
    HeatIndex = "heat_index"
