grafilter
=========

Dashboards like [Grafana](http://grafana.org) are awesome, but sometimes they make it hard to look at all the metrics, without first spending time to configure a dashboard. Grafilter is meant to provide lightweight and easy access to your metrics. You can still customize visuals of course, but in a way that let's you store these customizations in a versioned config management system such as [Ansible](http://www.ansible.com), [BundleWrap](http://bundlewrap.org) or [Chef](https://www.chef.io/chef/) as opposed to a database like Grafana 2 does.

Install
-------

	apt-get install python3-pip
	pip3 install grafilter

Configure
---------

Create a file with these contents anywhere:

	DEBUG = False
	INFLUXDB_URL = "http://user:pass@influxdb.example.com:8086"
	INFLUXDB_DB = "metrics"

Note that `INFLUXDB_URL` points to the HTTP API port of InfluxDB.

Run
---

	GRAFILTER_SETTINGS=/path/to/grafilter.cfg grafilter
