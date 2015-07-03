from datetime import datetime, timedelta

import requests

from .utils import build_id, simplify_keys


class InfluxDBBackend(object):
    def __init__(self, config):
        self._config = config

    def metrics(self):
        response = requests.get(
            self._config['INFLUXDB_URL'] + "/query",
            params={
                'db': self._config['INFLUXDB_DB'],
                'q': "SHOW SERIES",
            },
        )
        result = []
        response_json = response.json()['results'][0]
        for series in response_json.get('series', []):
            for tag_values in series['values']:
                tag_dict = dict(zip(series['columns'], tag_values))
                for ignored_tag in self._config['IGNORED_TAGS']:
                    try:
                        del tag_dict[ignored_tag]
                    except KeyError:
                        pass
                result.append((
                    build_id(series['name'], tag_dict),
                    {
                        'base_name': series['name'],
                        'tags': tag_dict,
                    },
                ))
        return sorted(result)

    def metric(
        self,
        base_name,
        tags,
        period=None,
        resolution=80,
        start=None,
        merge=None,
        transform=None,
    ):
        if merge is not None:
            resolution += 1
        if period is None:
            period = timedelta(3600)
        if start is not None:
            end = start + period
            timespec = "time > '{start}' AND time < '{end}'".format(
                end=end.strftime("%Y-%m-%d %H:%M:%S"),
                start=start.strftime("%Y-%m-%d %H:%M:%S"),
            )
        else:
            timespec = "time > now() - {}s".format(int(period.total_seconds()))

        tag_filter = ""
        for key, value in tags.items():
            tag_filter += " and \"{}\" = '{}'".format(key, value)

        tick = int(period.total_seconds() / resolution)

        response = requests.get(
            self._config['INFLUXDB_URL'] + "/query",
            params={
                'db': self._config['INFLUXDB_DB'],
                'q': "SELECT mean(value) from \"{base_name}\" "
                     "WHERE {timespec}{tag_filter} GROUP BY time({tick}s), *".format(
                    base_name=base_name,
                    tag_filter=tag_filter,
                    timespec=timespec,
                    tick=tick,
                ),
            },
        )
        series_list = response.json()['results'][0]['series']
        data = {}

        for series in series_list:
            series_id = build_id(series['name'], series.get('tags', {}))
            data[series_id] = []
            prev_value = None
            for time, value in series['values']:
                if merge is not None and value is not None:
                    if prev_value is None:
                        prev_value = value
                        continue
                    prev_value, value = value, merge(prev_value, value, tick)
                if transform is None or value is None:
                    data[series_id].append(value)
                else:
                    data[series_id].append(transform(value))

        simplify_keys(data)

        data['x'] = [
            int(datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ").timestamp() * 1000)
            for time, value in series_list[0]['values']
        ]

        return data
