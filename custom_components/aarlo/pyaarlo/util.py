import time
from datetime import datetime, timezone

import requests


def arlotime_to_time(timestamp):
    return int(timestamp / 1000)


def arlotime_to_datetime(timestamp):
    return datetime.fromtimestamp(int(timestamp / 1000))


def arlotime_strftime(timestamp, date_format='%Y-%m-%dT%H:%M:%S'):
    return arlotime_to_datetime(timestamp).strftime(date_format)


def time_to_arlotime(timestamp=None):
    if timestamp is None:
        timestamp = time.time()
    return int(timestamp * 1000)


def now_strftime(date_format='%Y-%m-%dT%H:%M:%S'):
    return datetime.now().strftime(date_format)


def httptime_to_datetime(http_timestamp):
    utc_dt = datetime.strptime(http_timestamp, '%a, %d %b %Y %H:%M:%S GMT')
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


def httptime_strftime(http_timestamp, date_format='%Y-%m-%dT%H:%M:%S'):
    return httptime_to_datetime(http_timestamp).strftime(date_format)


def _http_get(url):
    """Download HTTP data."""

    if url is None:
        return None

    try:
        ret = requests.get(url)
    except requests.exceptions.SSLError:
        return None
    except Exception:
        return None

    if ret.status_code != 200:
        return None
    return ret


def http_get(url, filename=None):
    # make request
    ret = _http_get(url)
    if ret is None:
        return False

    if filename is None:
        return ret.content

    with open(filename, 'wb') as data:
        data.write(ret.content)
    return True


def http_get_img(url):
    # make request
    ret = _http_get(url)
    if ret is None:
        return None, datetime.now()

    date = ret.headers.get('Last-Modified', None)
    if date is not None:
        date = httptime_to_datetime(date)
    else:
        date = datetime.now()
    return ret.content, date


def http_stream(url, chunk=4096):
    """Generate stream for a given record video.

    :param url: url of stream to read
    :param chunk: chunk bytes to read per time
    :returns generator object
    """
    ret = requests.get(url, stream=True)
    ret.raise_for_status()
    for data in ret.iter_content(chunk):
        yield data
