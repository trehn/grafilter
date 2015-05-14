import json
from urllib.parse import quote_plus, unquote_plus

from flask import Flask, render_template

from influxdb import InfluxDBBackend

app = Flask(__name__)
app.config.from_pyfile("grafilter.cfg")

backend = InfluxDBBackend(app.config)


def quote(s):
    # https://github.com/mitsuhiko/flask/issues/900
    # http://www.leakon.com/archives/865
    return quote_plus(quote_plus(s))


def unquote(s):
    return unquote_plus(unquote_plus(s))


@app.route("/")
def index():
    return render_template(
        "index.html",
        metrics=[(metric, quote(metric)) for metric in backend.metrics()],
    )


@app.route("/metric/<metric_urlsafe>/")
def metric(metric_urlsafe):
    metric = unquote(metric_urlsafe)
    return render_template(
        "metric.html",
        metric=metric,
        values=json.dumps(backend.metric(metric)),
    )


if __name__ == "__main__":
    app.debug = True
    app.run()
