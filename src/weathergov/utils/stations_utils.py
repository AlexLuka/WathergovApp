import os
import requests
import logging

from time import time, sleep
from weathergov.constants import APP_NAME


logger = logging.getLogger(__name__)


def get_all_stations() -> list:
    """
        This function reads all the stations from Weather.gov
        API and returns them as a list of dictionaries.
    :return:
    """
    # Measure how long does it take to run this function
    t_ = time()
    stations = []

    weather_gov_api_url = os.environ.get('WEATHER_GOV_API_URL')
    url_station_link = f"{weather_gov_api_url}/stations"

    headers = {
        "User-Agent": APP_NAME
    }

    while True:
        response = requests.get(url_station_link, headers=headers)

        if response.status_code != 200:
            logger.warning(f"Got status code {response.status_code}")
            break

        rj = response.json()

        if 'features' not in rj.keys():
            logger.warning(f"Key 'features' not found in the response")
            break

        if len(rj['features']) == 0:
            # Reached the end of pagination
            break

        for feature in rj['features']:
            station = dict()

            try:
                station["url"] = feature['id']
            except KeyError:
                logger.warning(f"Key 'id' not found in the feature")

            try:
                feature_properties = feature['properties']
            except KeyError:
                logger.warning(f"Key 'properties' not found in the feature")
                feature_properties = dict()

            # Get the main properties
            for my_key, their_key in [('station_id', 'stationIdentifier'),
                                      ('station_name', 'name'),
                                      ('station_timezone', 'timeZone'),
                                      ('station_county_url', 'county'),
                                      ('station_type', "@type")]:
                try:
                    station[my_key] = feature_properties[their_key]
                except KeyError:
                    logger.warning(f"Key '{their_key}' not found in the feature properties")
                    station[my_key] = ""

            # Get the elevation
            try:
                elevation = feature_properties['elevation']
            except KeyError:
                logger.warning(f"Key 'elevation' not found in the feature properties")
                elevation = dict()

            for my_key, their_key in [('elevation', 'value'), ('elevation_units', 'unitCode')]:
                try:
                    station[my_key] = elevation[their_key]
                except KeyError:
                    logger.warning(f"Key '{their_key}' not found in the elevation property")
                    station[my_key] = ""

            # Get the geometry, coordinates
            try:
                geometry = feature['geometry']
            except KeyError:
                logger.warning(f"Key 'geometry' not found in the feature")
                geometry = dict()

            try:
                lon, lat = geometry['coordinates']
                station['longitude'] = lon
                station['latitude'] = lat
            except KeyError:
                logger.warning(f"Key 'coordinates' not found in the feature geometry")
                station['longitude'] = ""
                station['latitude'] = ""

            stations.append(station)

        url_station_link = rj['pagination']['next']
        sleep(2)

    logger.info(f"Got information about {len(stations)} stations from Weather.gov API")
    logger.debug(f"get_all_stations() run within {time() - t_:.1f} seconds")
    return stations


def get_station_data(station_id: str) -> dict:
    """

    :param station_id:
    :return:
    """

    t_ = time()
    data = {
        "ts": [],
        "temperature": [],
        "dew_point": [],
        "wind_direction": [],
        "wind_speed": [],
        "wind_gust": [],
        "barometric_pressure": [],
        "sea_level_pressure": [],
        "visibility": [],
        "precipitation_last_3h": [],
        "relative_humidity": [],
        "wind_chill": [],
        "heat_index": []
    }

    weather_gov_api_url = os.environ.get('WEATHER_GOV_API_URL')
    url_station_link = f"{weather_gov_api_url}/stations/{station_id}/observations"

    headers = {
        "User-Agent": APP_NAME
    }

    response = requests.get(url_station_link, headers=headers)

    if response.status_code != 200:
        logger.warning(f"Got status code {response.status_code} for station {station_id}")
        return data

    # Get response in JSON format
    rj = response.json()

    if "features" not in rj.keys():
        logger.warning(f"Failre to find 'features' key in a response for station {station_id}")

    features: list
    features = rj['features']

    for feature in features:
        properties = feature['properties']

        # Add timestamp
        data["ts"].append(properties['timestamp'])

        for my_key, their_key in [("temperature", "temperature"),
                                  ("dew_point", "dewpoint"),
                                  ("wind_direction", "windDirection"),
                                  ("wind_speed", "windSpeed"),
                                  ("wind_gust", "windGust"),
                                  ("barometric_pressure", "barometricPressure"),
                                  ("sea_level_pressure", "seaLevelPressure"),
                                  ("visibility", "visibility"),
                                  ("precipitation_last_3h", "precipitationLast3Hours"),
                                  ("relative_humidity", "relativeHumidity"),
                                  ("wind_chill", "windChill"),
                                  ("heat_index", "heatIndex")]:
            try:
                data[my_key].append(properties[their_key])
            except KeyError:
                data[my_key].append(None)
    logger.debug(f"get_station_data() run within {time() - t_:.1f} seconds")
    return data
