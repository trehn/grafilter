grafilter
=========

Dashboards like [Grafana](http://grafana.org) are awesome, but sometimes they make it hard to look at all the metrics, without first spending time to configure a dashboard. Grafilter is meant to provide lightweight and easy access to your metrics. You can still customize visuals of course, but in a way that let's you store these customizations in a versioned config management system such as [Ansible](http://www.ansible.com), [BundleWrap](http://bundlewrap.org) or [Chef](https://www.chef.io/chef/) as opposed to a database like Grafana 2 does.

Install
-------

```
apt-get install python3-pip
pip3 install grafilter
```

Configure
---------

Create a file with these contents anywhere:

```python
DEBUG = False
CACHE_TIMEOUT = 300
CONFIG_DIR = "/var/lib/grafilter"
INFLUXDB_URL = "http://user:pass@influxdb.example.com:8086"
INFLUXDB_DB = "metrics"
```

Note that `INFLUXDB_URL` points to the HTTP API port of InfluxDB.

Run
---

```sh
GRAFILTER_SETTINGS=/path/to/grafilter.cfg grafilter
```

Customize
---------

You can customize the appearance of your individual metrics by placing files in the `metrics` subdirectory of your `CONFIG_DIR`. These files must have a `.json` extension and look like this:

```json
{
	"pattern": "\\.load$",
	"transform": "lambda x: math.floor(x)",
	"type": "area"
}
```

Note that `pattern` is a regular expression that has to match the name of the metrics you want to customize. Each metric will only be styled according to the first file with a matching `pattern`. All other options listed here are optional.

Option | Explanation
-------|------------
`transform` | a Python expression describing a function that takes a numeric value and returns another. It can be used to perform conversions and other math on your metrics. You have access to the [math module from the Python standard library](https://docs.python.org/3/library/math.html).
`type` | `area`, `area-spline`, `area-step`, `line`, `spline` or `step` (defaults to `line`)
