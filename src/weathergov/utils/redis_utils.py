import os
import json
import logging

from redis import Redis
from datetime import datetime

logger = logging.getLogger(__name__)


class RedisInfo:
    _password = None
    _host = None
    _port = None

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value: str):
        if value is None:
            self.logger.warning(f"Redis Password is not set")
        self._password = value

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value: str):
        if value is None:
            self.logger.warning(f"Redis Host is not set")
        self._host = value

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value: int):
        if value is None:
            self.logger.warning(f"Redis port is not set")
        self._port = value

    @staticmethod
    def load():
        ri = RedisInfo()
        ri.password = os.environ.get("REDIS_PASS", None)
        ri.host = os.environ.get("REDIS_HOST", None)
        ri.port = os.environ.get("REDIS_PORT", None)
        return ri


class RedisClient:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        redis_info = RedisInfo.load()

        self.rc = Redis(
            host=redis_info.host,
            port=redis_info.port,
            password=redis_info.password,
            decode_responses=True
        )

    def create_weather_stations_queue(self):
        # Get all station IDs. There should be about 46000 of them
        station_ids = list(self.rc.smembers("weather_station:weather.gov:station_ids"))

        # Check if the queue is empty, if not, then no need to create anything again
        n = self.rc.llen("weather_station_process_queue")

        if n > 0:
            self.logger.info(f"Queue is not empty. Need to complete the previous computations first!")
            return

        # Put all of them into a list
        # If at some point we are going to deal with different data sources, then include data
        # source to a payload: include station ID and
        pipeline = self.rc.pipeline()

        for station_id in station_ids:
            payload = json.dumps({
                "station_id": station_id,
                "data_source": "weather.gov"
            })
            pipeline.lpush("weather_station_process_queue", payload)

        pipeline.execute()

    def get_station_id_from_queue(self) -> str:
        return self.rc.lpop("weather_station_process_queue")

    def get_station_data_populated_last_time_ts(self):
        ts_str = self.rc.get("weather_station:weather.gov:last_data_update_ts")

        if ts_str is None:
            # If we get None, then it have never been fetched before
            return 0

        # convert to integer
        return int(str(ts_str))

    def set_station_data_populated_last_time_ts(self, ts: int):
        self.rc.set("weather_station:weather.gov:last_data_update_ts", str(ts))

    def add_timeseries_data(self, station_id: str, data: dict):
        if 'timestamp' not in data.keys():
            self.logger.warning(f"Keyword 'timestamp' not found in the data")
            return
        ts = data['timestamp']

        # Get the timeseries connector
        rc_ts = self.rc.ts()
        rc_ts_pipe = rc_ts.pipeline()

        #
        # At this point we should have timestamp, let's go over all the possible
        # data metrics and add all of them as timeseries data to Redis
        for keyword in ["temperature",
                        "dew_point",
                        "wind_direction",
                        "wind_speed",
                        "wind_gust",
                        "barometric_pressure",
                        "sea_level_pressure",
                        "visibility",
                        "precipitation_last_3h",
                        "relative_humidity",
                        "wind_chill",
                        "heat_index"]:
            try:
                kw_data = data[keyword]
            except KeyError:
                logger.warning(f"Failed to find keyword '{keyword}' in data for station {station_id}")
                continue

            # Check if they have the same size
            if len(ts) != len(kw_data):
                logger.warning(f"Data length do not match for keyword {keyword}: "
                               f"len(kw_data)={len(kw_data)} != {len(ts)} = len(ts)")
                continue

            # Here we have the same length of ts and data and can insert it to Redis
            # First we need to convert the timestamp to unix time
            for tsi, value in zip(ts, kw_data):
                # Convert time to unix epoch timestamp in milliseconds
                tsi_unix = int(datetime.strptime(tsi, "%Y-%m-%dT%H:%M:%S%z").timestamp() * 1000)

                # Add to timeseries
                rc_ts_pipe.add(f"weather_station:weather.gov:{station_id}:data:{keyword}",
                               tsi_unix, value,
                               duplicate_policy="FIRST")
            # Execute transaction
            rc_ts_pipe.execute()
            logger.info(f"{len(ts)} new data points added to {keyword} data for station {station_id}")

        self.logger.info(f"Data for station {station_id} have been added to Redis")


# TODO Move this function to a RedisClient class
def update_observation_stations(stations: list):
    """
        Save observation stations to Redis HASH
        under "weather_station:weather.gov:ABCD23"
        where the latter is the station ID.

        In addition, create a set of all the station IDs:
            "weather_station:weather.gov:station_ids"

    :param stations:
    :return:
    """

    redis_info = RedisInfo.load()

    rc = Redis(
        host=redis_info.host,
        port=redis_info.port,
        password=redis_info.password,
        decode_responses=True
    )
    logger.info(f"Successfully connected to Redis")

    pipeline = rc.pipeline()

    for station in stations:
        station_id = station["station_id"]

        pipeline.hset(f"weather_station:weather.gov:{station_id}", mapping=station)
        pipeline.sadd("weather_station:weather.gov:station_ids", station_id)

    # TODO
    #  Update the station tracker: how many stations there were on a specific date.
    #  This is going to be a timeseries. On July 10, 2024 there were 46483 stations

    pipeline.execute()
    logger.info(f"Stations info was updated in Redis")
