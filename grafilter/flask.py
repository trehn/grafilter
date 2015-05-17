import json

from flask import Flask, jsonify, render_template, request, Response

from .background import Cache
from .cache import build_cache
from .influxdb import InfluxDBBackend
from .utils import parse_datetime, parse_timedelta, search_string, unquote


DEFAULT_PERIOD = "1h"
DEFAULT_RESOLUTION = 80


app = Flask(__name__)
app.config.from_envvar("GRAFILTER_SETTINGS")

backend = InfluxDBBackend(app.config)
cache = Cache(
    app.config['CACHE_TIMEOUT'],
    build_cache,
    (backend, app.config['CONFIG_DIR']),
)


def get_request_arg(key, default):
    try:
        value = request.args[key]
    except KeyError:
        return default
    if not value:
        return default
    else:
        return value


@app.route("/")
def index():
    return render_template("index.html")


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
def metric_data(metric_urlsafe):
    return jsonify(
        **backend.metric(
            unquote(metric_urlsafe),
            resolution=int(get_request_arg('resolution', DEFAULT_RESOLUTION)),
            start=parse_datetime(get_request_arg('start', None)),
            period=parse_timedelta(get_request_arg('period', DEFAULT_PERIOD)),
        )
    )


@app.route("/search")
def metric_search():
    query = request.args.get("q", "")
    result = []
    with cache.lock:
        metrics = cache['metrics']
    for metric, metric_urlsafe in metrics:
        if search_string(query, metric):
            result.append({'name': metric, 'name_urlsafe': metric_urlsafe})
    return Response(json.dumps(result), mimetype="application/json")


if __name__ == "__main__":
    app.debug = True
    app.run()
