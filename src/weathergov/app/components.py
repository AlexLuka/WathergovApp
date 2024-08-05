from enum import Enum, unique


@unique
class Components(str, Enum):
    GraphMap = "graph-map"

    WeatherStationInfoPanelName = "ws-info-panel-name"
    WeatherStationInfoPanelStationID = "ws-info-panel-station-id"
    WeatherStationInfoPanelElevationAboveGround = "ws-info-panel-elevation-above-round"
    WeatherStationInfoPanelStationURL = "ws-info-panel-station-url"
