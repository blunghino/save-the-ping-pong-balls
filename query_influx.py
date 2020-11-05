from datetime import date
import os

from influxdb_client import InfluxDBClient
import pandas as pd


BUCKET = os.getenv('INFLUXDB_V2_BUCKET')


class InfluxQuery:

    client = InfluxDBClient.from_env_properties()
    query_api = client.query_api()

    def get(
        self,
        days_back: int,
        experiment: str = 'seaside-kitchen-fridge-2',
    ) -> pd.DataFrame:
        dfs = list()
        for day_back in range(days_back):
            query_str = (
                f'from(bucket: "{BUCKET}")'
                f'  |> range(start: -{day_back+1}d, stop: -{day_back}d)'
                 '  |> filter(fn: (r) => r["_measurement"] == "sensorReadings")'
                 '  |> filter(fn: (r) => r["_field"] == "reed_switch_is_open_int"'
                 ' or r["_field"] == "tmp117_temperature"'
                 ' or r["_field"] == "bme280_temperature")'
                f'  |> filter(fn: (r) => r["experiment"] == "{experiment}")'
                 '  |> aggregateWindow(every: 1s, fn: last, createEmpty: false)'
                 '  |> yield(name: "last")'
            )
            dfs.append(self.query_api.query_data_frame(query_str))
        return pd.concat(dfs)


def get_dataset(days_back: int, save: bool = True) -> pd.DataFrame:
    today = date.today().isoformat()
    file_path = os.path.join(
        'data', 
        f'sensorReadings-{days_back}-days-thru-{today}.csv'
    )
    try:
        data = pd.read_csv(file_path)
    except FileNotFoundError:
        query = InfluxQuery()
        data = query.get(days_back=days_back)
        if save:
            data.to_csv(file_path)
    return data

if __name__ == '__main__':
    data = get_dataset(days_back=2)
    print(data)

