import json

from flask import Flask, jsonify, render_template, request, Response

from .background import Cache
from .cache import build_cache
from .influxdb import InfluxDBBackend
from .utils import parse_datetime, parse_timedelta, quote, search_string, unquote


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


def get_metric_style(metric):
    with cache.lock:
        styles = cache['styles']
    style = {}
    for pattern, style_candidate in styles.items():
        if pattern.search(metric) is not None:
            style = style_candidate
            break
    return style


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/metric/<metric_urlsafe>/")
def metric(metric_urlsafe):
    metric = unquote(metric_urlsafe)
    # one level of quoting got removed by Flask
    metric_urlsafe = quote(metric)
    style = get_metric_style(metric)
    return render_template(
        "metric.html",
        metric=metric,
        metric_urlsafe=metric_urlsafe,
        period=get_request_arg('period', None),
        resolution=int(get_request_arg('resolution', 0)),
        start=get_request_arg('start', None),
        style=style,
    )


@app.route("/metricdata/<metric_urlsafe>/")
def metric_data(metric_urlsafe):
    metric = unquote(metric_urlsafe)
    style = get_metric_style(metric)
    return jsonify(
        **backend.metric(
            metric,
            display_name=style.get('short_name', metric),
            period=parse_timedelta(get_request_arg('period', DEFAULT_PERIOD)),
            resolution=int(get_request_arg('resolution', DEFAULT_RESOLUTION)),
            start=parse_datetime(get_request_arg('start', None)),
            transform=style.get('transform', None),
        )
    )


@app.route("/search")
def metric_search():
    query = request.args.get("q", "")
    result = []
    with cache.lock:
        metrics = cache['metrics']
    for metric, metric_properties in metrics.items():
        if search_string(query, metric):
            result.append({
                'name': metric,
                'name_urlsafe': metric_properties['name_urlsafe'],
                'styled': metric_properties['styled'],
            })
    return Response(json.dumps(result), mimetype="application/json")


if __name__ == "__main__":
    app.debug = True
    app.run()
