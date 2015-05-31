import json
from urllib.parse import quote as no_slash_quote

from flask import Flask, jsonify, render_template, request, Response

from .background import Cache
from .cache import build_cache
from .influxdb import InfluxDBBackend
from .utils import build_reduced_ids, parse_datetime, parse_id, parse_timedelta, search_string


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


@app.route("/metric/<path:metric_id>/")
def metric(metric_id):
    base_name, tags = parse_id(metric_id)
    style = get_metric_style(metric_id)
    return render_template(
        "metric.html",
        metric_id=no_slash_quote(metric_id),
        base_name=base_name,
        tags=tags,
        reduced_ids=build_reduced_ids(base_name, tags),
        period=get_request_arg('period', None),
        resolution=int(get_request_arg('resolution', 0)),
        start=get_request_arg('start', None),
        style=style,
    )


@app.route("/metricdata/<path:metric_id>/")
def metric_data(metric_id):
    base_name, tags = parse_id(metric_id)
    style = get_metric_style(metric_id)
    return jsonify(
        **backend.metric(
            base_name,
            tags,
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
    columns = set()
    for metric, metric_properties in metrics.items():
        if search_string(query, metric):
            result.append({
                'base_name': metric_properties['base_name'],
                'id': metric,
                'styled': metric_properties['styled'],
                'tags': metric_properties['tags'],
            })
            columns.update(metric_properties['tags'].keys())
    result.insert(0, sorted(columns))
    return Response(json.dumps(result), mimetype="application/json")


if __name__ == "__main__":
    app.debug = True
    app.run()
