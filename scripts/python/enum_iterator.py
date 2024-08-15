import itertools
from weathergov.constants import Metrics


stations = ["AN901", "89234", "PPK89", "ABTYO"]


for station_id, metric in itertools.product(stations, Metrics):
    print(f"key={station_id}:{metric}")
