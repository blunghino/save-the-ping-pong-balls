from datetime import datetime
import os
import time

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import ASYNCHRONOUS, PointSettings

from tmp102 import TMP102


def read_sensors(tmp102: TMP102) -> Point:
    return Point("sensorReadings") \
        .time(datetime.utcnow(), WritePrecision.S) \
        .field("tmp102", tmp102.readTemperature())


def cli():
    bucket = os.getenv("INFLUXDB_V2_BUCKET")
    # https://github.com/influxdata/influxdb-client-python#via-environment-properties
    client = InfluxDBClient.from_env_properties()
    ps = PointSettings(experiment="seaside-kitchen-fridge")
    # write_api = client.write_api(write_options=ASYNCHRONOUS, point_settings=ps)
    write_api = client.write_api(point_settings=ps)
    
    _tmp102 = TMP102(units='C', address=0x48, busnum=1)
    while True:
        point = read_sensors(tmp102=_tmp102)
        # https://github.com/influxdata/influxdb-client-python#asynchronous-client
        write_api.write(bucket=bucket, record=point)
        time.sleep(1)
    client.__del__()


if __name__ == "__main__":
    cli()
