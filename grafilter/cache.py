from collections import OrderedDict
from glob import glob
from json import loads
import math
from os.path import join
import re


def apply_metric_customizations(cache, config_dir):
    for filename in glob(join(config_dir, "metrics", "*.json")):
        with open(filename, 'r') as f:
            json = loads(f.read())
        pattern = re.compile(json['pattern'])
        cache['styles'][pattern] = json
        if cache['styles'][pattern].get('merge', None) is not None:
            cache['styles'][pattern]['merge'] = eval(
                cache['styles'][pattern]['merge'],
                {'math': math},
            )
        if cache['styles'][pattern].get('transform', None) is not None:
            cache['styles'][pattern]['transform'] = eval(
                cache['styles'][pattern]['transform'],
                {'math': math},
            )
        for metric in cache['metrics'].keys():
            if pattern.search(metric) is not None:
                cache['metrics'][metric]['styled'] = True


def build_cache(backend, config_dir):
    cache = {
        'metrics': OrderedDict(),
        'styles': {},
    }
    for metric, metric_meta in backend.metrics():
        cache['metrics'][metric] = {
            'base_name': metric_meta['base_name'],
            'tags': metric_meta['tags'],
            'styled': False,
        }
    apply_metric_customizations(cache, config_dir)
    return cache
