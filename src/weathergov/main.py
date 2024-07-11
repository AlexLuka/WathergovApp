import argparse

from weathergov.scripts.loaders import (observation_station_loader,
                                        historical_data_loader,
                                        rt_data_loader)

"""
    Depending on type of a selected script we are going to run the corresponding 
    functionality:
    - ObservationStationsLoader
    - HistoricalDataLoader
    - RTDataLoader 
"""


def main(script_name: str):
    if script_name == "ObservationStationsLoader":
        print(f"ObservationStationsLoader is running")
        observation_station_loader()
    elif script_name == "HistoricalDataLoader":
        print(f"HistoricalDataLoader is running")
        historical_data_loader()
    elif script_name == "RTDataLoader":
        print(f"RTDataLoader is running")
        rt_data_loader()
    else:
        print(f"Unknown script {script_name}. Exiting...")
        exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Weather Puller',
        description='It periodically pulls the data from Weather API',
        epilog='How can I help you?')

    parser.add_argument("-s", "--script", default="NotSelected")
    args = parser.parse_args()

    main(args.script)
