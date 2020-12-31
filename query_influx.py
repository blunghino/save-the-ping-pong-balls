from datetime import date
import os
from typing import Dict, Optional

from influxdb_client import InfluxDBClient
from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns


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


# distributions of temperature during periods when the door isn't open vs when it is open
def box_by_door_open(data_wide: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(4, 4))
    sns.boxplot(data=data_wide, y='tmp117_temperature', x='Door opened in past hour', ax=ax)
    plt.ylabel('Fridge Temperature [deg C]')
    return fig


def in_out_temp_by_door_open(data_wide: pd.DataFrame) -> plt.Figure:
    g = sns.jointplot(data=data_wide, x='bme280_temperature', edgecolors='face', alpha=0.3,
                      y='tmp117_temperature', hue='Door opened in past hour')
    g.set_axis_labels('External Temperature [deg C]', 'Fridge Temperature [deg C]')
    return g.fig
# how fast does the air temperature recover


def rolling_temp_vs_time_open(data_wide: pd.DataFrame, smooth_hrs: float) -> plt.Figure:
    smooth = data_wide.rolling(window=3600 * smooth_hrs).agg({
        'reed_switch_is_open_int': 'sum',
        'tmp117_temperature': 'mean',
    })
    g = sns.jointplot(data=smooth, x='reed_switch_is_open_int', edgecolors='face', alpha=0.3,
                      y='tmp117_temperature', marker='.')
    g.fig.suptitle(f'Rolling {smooth_hrs} hours')
    g.set_axis_labels('Total Door Open Time [s]', 'Average Fridge Temperature [deg C]')
    return g.fig


def run_analysis(data: pd.DataFrame) -> Dict[str, plt.Figure]:
    data_wide = data.pivot(index='_time', columns='_field', values='_value')
    one_hour = 3600
    count_open_hr = data_wide \
        .loc[:, 'reed_switch_is_open_int'] \
        .rolling(window=one_hour) \
        .sum()
    data_wide.loc[:, 'Door opened in past hour'] = count_open_hr > 0
    figs: Dict[str, plt.Figure] = {}
    figs['rolling_temp_vs_time_open_24'] = rolling_temp_vs_time_open(data_wide, smooth_hrs=24)
    figs['rolling_temp_vs_time_open_3'] = rolling_temp_vs_time_open(data_wide, smooth_hrs=3)
    figs['box_by_door_open'] = box_by_door_open(data_wide)
    figs['in_out_temp_by_door_open'] = in_out_temp_by_door_open(data_wide)
    return figs

if __name__ == '__main__':
    raw_data = get_dataset(days_back=21, end_date='2020-11-04', save=False)
    # data = get_dataset(days_back=30, end_date='2020-12-20')
    data = raw_data.drop_duplicates().drop(columns=['experiment'])
    figs = run_analysis(data)
    for name, fig in figs.items():
        fig.savefig(f'{name}.png', dpi=300)
    plt.show()

