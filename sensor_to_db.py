from datetime import datetime
import os
import time
from typing import Callable

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import ASYNCHRONOUS, PointSettings

from reed_switch import reed_switch_is_open
from tmp102 import TMP102


def get_measurements(sensors: Dict[str, Callable]) -> Point:
    point = Point("sensorReadings").time(datetime.utcnow(), WritePrecision.S)
    for sensor_name, sensor_func in sensors.items():
        point = point.field(sensor_name, sensor_func())
    return point


def cli():
    bucket = os.getenv("INFLUXDB_V2_BUCKET")
    # https://github.com/influxdata/influxdb-client-python#via-environment-properties
    client = InfluxDBClient.from_env_properties()
    ps = PointSettings(experiment="seaside-kitchen-fridge")
    # write_api = client.write_api(write_options=ASYNCHRONOUS, point_settings=ps)
    write_api = client.write_api(point_settings=ps)
    
    # _tmp102 = TMP102(units='C', address=0x48, busnum=1)
    sensors = {
        # 'tmp102': _tmp102.readTemperature,
        'reed_switch_is_open': reed_switch_is_open,
    }
    while True:
        point = get_measurements(sensors)
        # https://github.com/influxdata/influxdb-client-python#asynchronous-client
        # write_api.write(bucket=bucket, record=point)
        time.sleep(1)
        print(reed_switch_is_open())
    client.__del__()


if __name__ == "__main__":
    cli()
