import os
import random

from redis import Redis
from dotenv import load_dotenv


load_dotenv()

redis_password = os.environ.get("REDIS_PASS", None)

if redis_password is None:
    print(f"Failed to load REDIS_PASS variable")
    exit(1)

rc = Redis(
    host="localhost",
    port=6379,
    password=redis_password,
    decode_responses=True
)

print(f"redis connection successful: {rc.ping()}")

# Get all the stations:
station_ids = rc.smembers("weather_station:weather.gov:station_ids")

station_id = random.choice(list(station_ids))
print(f"There are {len(station_ids)} stations. Example: {station_id}")

station_data = rc.hgetall(f"weather_station:weather.gov:{station_id}")
print(f"Station data: {station_data}")
