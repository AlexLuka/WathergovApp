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

        # TODO Temporary: remove this when finish
        #   Going to stop after the first iteration to speed up the testing process
        break
    logger.info(f"Got information about {len(stations)} stations from Weather.gov API")
    logger.debug(f"get_all_stations() run within {time() - t_:.1f} seconds")
    return stations
