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

    def metric(self, metric, timeframe="1h"):
        response = requests.get(
            self._config['INFLUXDB_URL'] + "/db/" + self._config['INFLUXDB_DB'] + "/series",
            params={
                'db': self._config['INFLUXDB_DB'],
                'q': "SELECT value from \"{metric}\" WHERE time > now() - {timeframe}".format(
                    metric=metric,
                    timeframe=timeframe,
                ),
            },
        )
        raw_points = response.json()[0]['points']
        points = []
        for time, sequence_number, value in raw_points:
            points.append((time, value))
        return points
