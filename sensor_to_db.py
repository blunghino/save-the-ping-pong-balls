from datetime import datetime
import os
import time
from typing import Callable, Dict

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import ASYNCHRONOUS, PointSettings

from bme280_sensor import bme280_humidity, bme280_temperature
from reed_switch import reed_switch_is_open
from tmp117 import TMP117


def get_measurements(sensors: Dict[str, Callable]) -> Point:
    point = Point("sensorReadings").time(datetime.utcnow(), WritePrecision.S)
    for sensor_name, sensor_func in sensors.items():
        point = point.field(sensor_name, sensor_func())
    return point



if __name__ == "__main__":
    bucket = os.getenv("INFLUXDB_V2_BUCKET")
    # https://github.com/influxdata/influxdb-client-python#via-environment-properties
    client = InfluxDBClient.from_env_properties()
    ps = PointSettings(experiment="seaside-kitchen-fridge")
    # write_api = client.write_api(write_options=ASYNCHRONOUS, point_settings=ps)
    write_api = client.write_api(point_settings=ps)
    
    _tmp117 = TMP117()
    sensors = {
        'bme280_humidity': bme280_humidity,
        'bme280_temperature': bme280_temperature,
        'reed_switch_is_open': reed_switch_is_open,
        'tmp117_temperature': _tmp117.get_temperature,
    }
    while True:
        t0 = time.time()
        point = get_measurements(sensors)
        # https://github.com/influxdata/influxdb-client-python#asynchronous-client
        # write_api.write(bucket=bucket, record=point)
        t1 = time.time()
        time.sleep(1. - (t1 - t0))
        print(reed_switch_is_open())
        print(bme280_temperature())
        print(_tmp117.get_temperature())
