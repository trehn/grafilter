from datetime import datetime, timedelta

import requests

from .utils import build_id


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
        for series in response_json['series']:
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
        display_name=None,
        period=None,
        resolution=80,
        start=None,
        transform=None,
    ):
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
            tag_filter += " and {} = '{}'".format(key, value)

        response = requests.get(
            self._config['INFLUXDB_URL'] + "/query",
            params={
                'db': self._config['INFLUXDB_DB'],
                'q': "SELECT mean(value) from \"{base_name}\" "
                     "WHERE {timespec}{tag_filter} GROUP BY time({tick}s)".format(
                    base_name=base_name,
                    tag_filter=tag_filter,
                    timespec=timespec,
                    tick=int(period.total_seconds() / resolution),
                ),
            },
        )

        raw_points = response.json()['results'][0]['series'][0]['values']
        data = {
            'x': [],
            display_name: [],
        }
        for time, value in raw_points:
            data['x'].append(int(datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ").timestamp() * 1000))
            if transform is None:
                data[display_name].append(value)
            else:
                data[display_name].append(transform(value))
        return data
