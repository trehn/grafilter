from datetime import datetime, timezone
import json
from urllib.parse import quote_plus, unquote_plus

from flask import Flask, render_template
from parsedatetime import Calendar

from .influxdb import InfluxDBBackend

app = Flask(__name__)
app.config.from_envvar("GRAFILTER_SETTINGS")

backend = InfluxDBBackend(app.config)

calendar = Calendar()


def quote(s):
    # https://github.com/mitsuhiko/flask/issues/900
    # http://www.leakon.com/archives/865
    return quote_plus(quote_plus(s))


def unquote(s):
    return unquote_plus(unquote_plus(s))


def parse_datetime(s):
    if s is None:
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
@app.route("/metric/<metric_urlsafe>/<period>/")
@app.route("/metric/<metric_urlsafe>/<period>/<start>/")
def metric(metric_urlsafe, period="1h", start=None):
    metric = unquote(metric_urlsafe)
    return render_template(
        "metric.html",
        metric=metric,
        metric_urlsafe=metric_urlsafe,
        start=start,
        period=period,
        values=json.dumps(backend.metric(
            metric,
            start=parse_datetime(start),
            period=parse_timedelta(period),
        )),
    )


if __name__ == "__main__":
    app.debug = True
    app.run()
