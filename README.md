grafilter
=========

Dashboards like [Grafana](http://grafana.org) are awesome, but sometimes they make it hard to look at all the metrics, without first spending time to configure a dashboard. Grafilter is meant to provide lightweight and easy access to your metrics. You can still customize visuals of course, but in a way that let's you store these customizations in a versioned config management system such as [Ansible](http://www.ansible.com), [BundleWrap](http://bundlewrap.org) or [Chef](https://www.chef.io/chef/) as opposed to a database like Grafana 2 does.

Grafilter supports InfluxDB 0.9.0 and onwards.

![PyPI downloads](http://img.shields.io/pypi/dm/grafilter.svg) &nbsp; ![PyPI version](http://img.shields.io/pypi/v/grafilter.svg) &nbsp; ![Python 3.x](http://img.shields.io/badge/Python-3.4-green.svg) &nbsp; ![License](http://img.shields.io/badge/License-GPLv3-red.svg)

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
CACHE_TIMEOUT = 300
CONFIG_DIR = "/var/lib/grafilter"
DEBUG = False
IGNORED_TAGS = ["_key"]
INFLUXDB_DB = "metrics"
INFLUXDB_URL = "http://user:pass@influxdb.example.com:8086"
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
	"pattern": "^load/",
	"transform": "lambda x: math.floor(x)",
	"type": "area"
}
```

Note that `pattern` is a regular expression that has to match the name of the metrics you want to customize. The name is formatted like this: `measurement/tag1:value1/tag2:value2`. Each metric will only be styled according to the first file with a matching `pattern`. All other options listed here are optional.

Option | Explanation
-------|------------
`max` | force highest value on y axis (int or float)
`merge` | a Python expression describing a function that takes two numeric values and the time interval between them and returns one numeric value. It can be used to calculate the difference between two sequential datapoints and use the result in your graph (useful for ever increasing counters, e.g. `lambda x, y, t: (y - x) / t`). You have access to the [math module from the Python standard library](https://docs.python.org/3/library/math.html). Applied before `transform`.
`min` | force lowest value on y axis (int or float)
`short_name` | a cosmetic name for this metric, e.g. "Load Average"
`stack` | set this to `true` if you want to stack values when selecting multiple metrics
`transform` | a Python expression describing a function that takes a numeric value and returns another. It can be used to perform conversions and other math on your metrics. You have access to the [math module from the Python standard library](https://docs.python.org/3/library/math.html). Applied after `merge`.
`type` | chart type: `area`, `area-spline`, `area-step`, `line`, `spline` or `step` (defaults to `line`)
`unit_format` | a [d3 format specifier](https://github.com/mbostock/d3/wiki/Formatting#d3_format) for your y axis (e.g. "s" to turn "1000" into "1K" and "1000000" into "1M")
`unit` | any string you want to be displayed next to your y axis
