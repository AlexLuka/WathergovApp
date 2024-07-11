import os
import logging
from redis import Redis


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


def update_observation_stations(stations: list):
    """
        Save observation stations to Redis HASH
        under "weather_station:weather.gov:SJAC2"
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

    pipeline.execute()
    logger.info(f"Stations info was updated in Redis")
