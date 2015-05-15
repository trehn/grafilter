from datetime import timedelta

import requests


class InfluxDBBackend(object):
    def __init__(self, config):
        self._config = config

    def metrics(self):
        response = requests.get(
            self._config['INFLUXDB_URL'] + "/db/" + self._config['INFLUXDB_DB'] + "/series",
            params={
                'db': self._config['INFLUXDB_DB'],
                'q': "list series",
            },
        )
        series = [series for time, series in response.json()[0]['points']]
        try:
            series.remove("events")
        except ValueError:
            pass
        return sorted(series)

    def metric(self, metric, period=None, start=None):
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
        response = requests.get(
            self._config['INFLUXDB_URL'] + "/db/" + self._config['INFLUXDB_DB'] + "/series",
            params={
                'db': self._config['INFLUXDB_DB'],
                'q': "SELECT value from \"{metric}\" WHERE {timespec}".format(
                    metric=metric,
                    timespec=timespec,
                ),
            },
        )
        raw_points = response.json()[0]['points']
        points = []
        for time, sequence_number, value in raw_points:
            points.append((time, value))
        return points
