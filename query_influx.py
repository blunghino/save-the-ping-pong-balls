from datetime import date
import os
from typing import Optional

from influxdb_client import InfluxDBClient
import pandas as pd


TZ = 'America/Los_Angeles'
BUCKET = os.getenv('INFLUXDB_V2_BUCKET')


class InfluxQuery:

    client = InfluxDBClient.from_env_properties()
    query_api = client.query_api()

    def get(
        self,
        days_back: int,
        experiment: str = 'seaside-kitchen-fridge-2',
    ) -> pd.DataFrame:
        dfs: List[pd.DataFrame] = list()
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
            df = self.query_api.query_data_frame(query_str)
            dfs.extend(df)
        return pd.concat(dfs)


def get_dataset(
    days_back: int,
    save: bool = True,
    end_date: Optional[str] = None
) -> pd.DataFrame:
    if end_date is None:
        end_date = date.today().isoformat()
    file_path = os.path.join(
        'data', f'sensorReadings-{days_back}-days-thru-{end_date}.csv')
    try:
        print('Attempting to read from local file.')
        data = pd.read_csv(file_path, parse_dates=True)
    except FileNotFoundError:
        print('Querying InfluxDB.')
        query = InfluxQuery()
        data = query.get(days_back=days_back)
        data = data.drop(
            columns=['result', 'table', '_start', '_stop', '_measurement'])
        data = data.iloc[:-1, :]
        data.loc[:, '_time'] = pd.to_datetime(data.loc[:, '_time'])
        data.loc[:, '_time'] = data.loc[:, '_time'].dt.tz_convert(TZ)
        if save:
            data.to_csv(file_path, index=False)
    data = data.set_index(['_field', '_time'], drop=False)
    return data

if __name__ == '__main__':
    data = get_dataset(days_back=21, end_date='2020-11-04')
    print(data)

