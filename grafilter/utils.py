from copy import copy
from datetime import datetime, timezone
from urllib.parse import quote_plus, unquote_plus

from parsedatetime import Calendar


calendar = Calendar()


def build_id(base_name, tag_dict):
    """
    Turns a metric name and a dict of tags into a canonical name for
    that series.

    base_name: "cpu_load"
    tag_dict: {'host': "foo.example.com", 'region': "us-west"}

    becomes

    "cpu_load/host:foo.example.com/region:us-west"
    """
    result = quote(base_name)
    for key in sorted(tag_dict.keys()):
        result += "/{}:{}".format(quote(key), quote(str(tag_dict[key])))
    return result


def build_reduced_ids(base_name, tag_dict):
    """
    Returns a dict mapping tag keys to metric IDs without that tag.
    """
    result = {}
    for key in tag_dict.keys():
        reduced_tag_dict = copy(tag_dict)
        del reduced_tag_dict[key]
        result[key] = build_id(base_name, reduced_tag_dict)
    return result


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


def parse_id(metric_id):
    """
    This is the reverse of build_id().
    """
    tokens = metric_id.split("/")
    base_name = unquote(tokens.pop(0))
    tags = {}
    for token in tokens:
        key, value = token.split(":", 1)
        tags[unquote(key)] = unquote(value)
    return base_name, tags


def parse_timedelta(s):
    return calendar.parseDT(
        s,
        sourceTime=datetime.now(timezone.utc),
        tzinfo=timezone.utc,
    )[0] - datetime.now(timezone.utc)


def search_string(query, candidate):
    for token in query.split():
        if token not in candidate:
            return False
    return True
