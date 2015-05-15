from datetime import datetime, timezone
from urllib.parse import quote_plus, unquote_plus

from flask import Flask, jsonify, render_template, request
from parsedatetime import Calendar

from .influxdb import InfluxDBBackend


DEFAULT_PERIOD = "1h"
DEFAULT_RESOLUTION = 80


app = Flask(__name__)
app.config.from_envvar("GRAFILTER_SETTINGS")

backend = InfluxDBBackend(app.config)

calendar = Calendar()


def get_request_arg(key, default):
    try:
        value = request.args[key]
    except KeyError:
        return default
    if not value:
        return default
    else:
        return value


def quote(s):
    # https://github.com/mitsuhiko/flask/issues/900
    # http://www.leakon.com/archives/865
    return quote_plus(quote_plus(s))


def unquote(s):
    return unquote_plus(unquote_plus(s))


def parse_datetime(s):
    if not s:
        return None
    return calendar.parseDT(s, sourceTime=datetime.now(timezone.utc), tzinfo=timezone.utc)[0]


def parse_timedelta(s):
    return calendar.parseDT(
        s,
        sourceTime=datetime.now(timezone.utc),
        tzinfo=timezone.utc,
    )[0] - datetime.now(timezone.utc)


@app.route("/")
def index():
    return render_template(
        "index.html",
        metrics=[(metric, quote(metric)) for metric in backend.metrics()],
    )


@app.route("/metric/<metric_urlsafe>/")
def metric(metric_urlsafe):
    return render_template(
        "metric.html",
        metric=unquote(metric_urlsafe),
        metric_urlsafe=metric_urlsafe,
        resolution=int(get_request_arg('resolution', 0)),
        start=get_request_arg('start', None),
        period=get_request_arg('period', None),
    )


@app.route("/metricdata/<metric_urlsafe>/")
def metricdata(metric_urlsafe):
    return jsonify(
        **backend.metric(
            unquote(metric_urlsafe),
            resolution=int(get_request_arg('resolution', DEFAULT_RESOLUTION)),
            start=parse_datetime(get_request_arg('start', None)),
            period=parse_timedelta(get_request_arg('period', DEFAULT_PERIOD)),
        )
    )


if __name__ == "__main__":
    app.debug = True
    app.run()
