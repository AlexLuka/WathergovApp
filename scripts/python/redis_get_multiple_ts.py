from dotenv import load_dotenv
from redis import Redis
from time import time

from weathergov.utils.redis_utils import RedisKeys, RedisInfo


load_dotenv()


redis_info = RedisInfo.load()

rc = Redis(
    host=redis_info.host,
    port=redis_info.port,
    password=redis_info.password,
    db=0
)
print(f"Successfully connected to Redis: {rc.ping()}")

station_id = "RNFM5"
ts_to = int(time() * 1000)
ts_from = ts_to - 24 * 3600 * 1000

pipe = rc.pipeline()

for data_keyword in ["temperature", "wind_direction"]:
    pipe.ts().range(
        RedisKeys.get_rt_data_key(station_id, data_keyword),
        ts_from,
        ts_to)

res = pipe.execute()

print(res)
