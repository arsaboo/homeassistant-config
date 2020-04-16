from .constant import DEFAULT_HOST


class ArloCfg(object):
    """ Helper class to get at Arlo configuration options.

    I got sick of adding in variables each time the config changed so I moved it all here. Config
    is passed in a kwarg and parsed out by the property methods.

    """

    def __init__(self, arlo, **kwargs):
        """ The constructor.

        Args:
            kwargs (kwargs): Configuration options.

        """
        self._arlo = arlo
        self._kw = kwargs
        self._arlo.debug('Cfg started')

    @property
    def storage_dir(self, default='/config/.aarlo'):
        return self._kw.get('storage_dir', default)

    @property
    def name(self, default='aarlo'):
        return self._kw.get('name', default)

    @property
    def username(self, default='unknown'):
        return self._kw.get('username', default)

    @property
    def password(self, default='unknown'):
        return self._kw.get('password', default)

    @property
    def host(self, default=DEFAULT_HOST):
        return self._kw.get('host', default)

    @property
    def dump(self, default=False):
        return self._kw.get('dump', default)

    @property
    def max_days(self, default=365):
        return self._kw.get('max_days', default)

    @property
    def db_motion_time(self, default=30):
        return self._kw.get('db_motion_time', default)

    @property
    def db_ding_time(self, default=10):
        return self._kw.get('db_ding_time', default)

    @property
    def request_timeout(self, default=60):
        return self._kw.get('request_timeout', default)

    @property
    def stream_timeout(self, default=0):
        return self._kw.get('stream_timeout', default)

    @property
    def recent_time(self, default=600):
        return self._kw.get('recent_time', default)

    @property
    def last_format(self, default='%m-%d %H:%M'):
        return self._kw.get('last_format', default)

    @property
    def no_media_upload(self, default=False):
        return self._kw.get('no_media_upload', default)

    @property
    def user_agent(self, default='apple'):
        return self._kw.get('user_agent', default)

    @property
    def mode_api(self, default='auto'):
        return self._kw.get('mode_api', default)

    @property
    def refresh_devices_every(self, default=0):
        return self._kw.get('refresh_devices_every', default) * 60 * 60

    @property
    def http_connections(self, default=20):
        return self._kw.get('http_connections', default)

    @property
    def http_max_size(self, default=10):
        return self._kw.get('http_maz_size', default)

    @property
    def reconnect_every(self, default=0):
        return self._kw.get('reconnect_every', default) * 60

    @property
    def verbose(self, default=False):
        return self._kw.get('verbose_debug', default)

    @property
    def hide_deprecated_services(self, default=False):
        return self._kw.get('hide_deprecated_services', default)
