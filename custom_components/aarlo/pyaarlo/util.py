
import pprint
import time
from datetime import datetime
import requests

def arlotime_to_time( timestamp ):
    return timestamp/1000

def time_to_arlotime( timestamp=None ):
    if timestamp is None:
        timestamp = time.time()
    return int(timestamp*1000)

def arlotime_to_datetime( timestamp ):
    return datetime.fromtimestamp( int(timestamp/1000) )

def now_strftime( date_format='%Y-%m-%dT%H:%M:%S' ):
    return datetime.now().strftime( date_format )

def arlotime_strftime( timestamp,date_format='%Y-%m-%dT%H:%M:%S' ):
    #date_format = '%Y-%m-%dT%H:%M:%S'
    return arlotime_to_datetime(timestamp).strftime( date_format )

def http_get( url,filename=None ):
    """Download HTTP data."""
    try:
        ret = requests.get(url)
    except requests.exceptions.SSLError as error:
        return False
    except:
        return False

    if ret.status_code != 200:
        return False

    if filename is None:
        return ret.content

    with open( filename,'wb' ) as data:
        data.write(ret.content)
    return True

def http_stream(url, chunk=4096):
    """Generate stream for a given record video.

    :param chunk: chunk bytes to read per time
    :returns generator object
    """
    ret = requests.get(url, stream=True)
    ret.raise_for_status()
    for data in ret.iter_content(chunk):
        yield data
