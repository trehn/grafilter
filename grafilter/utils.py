from datetime import datetime, timezone
from urllib.parse import quote_plus, unquote_plus

from parsedatetime import Calendar


calendar = Calendar()


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
