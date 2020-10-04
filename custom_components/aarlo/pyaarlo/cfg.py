from .constant import (
    DEFAULT_AUTH_HOST,
    DEFAULT_HOST,
    PRELOAD_DAYS,
    TFA_CONSOLE_SOURCE,
    TFA_DEFAULT_HOST,
    TFA_EMAIL_TYPE,
)


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
    def storage_dir(self):
        return self._kw.get('storage_dir', "/config/.aarlo")

    @property
    def name(self):
        return self._kw.get('name', "aarlo")

    @property
    def username(self):
        return self._kw.get('username', "unknown")

    @property
    def password(self):
        return self._kw.get('password', "unknown")

    @property
    def host(self):
        return self._kw.get('host', DEFAULT_HOST)

    @property
    def auth_host(self):
        return self._kw.get('auth_host', DEFAULT_AUTH_HOST)

    @property
    def dump(self):
        return self._kw.get('dump', False)

    @property
    def max_days(self):
        return self._kw.get('max_days', 365)

    @property
    def db_motion_time(self):
        return self._kw.get('db_motion_time', 30)

    @property
    def db_ding_time(self):
        return self._kw.get('db_ding_time', 10)

    @property
    def request_timeout(self):
        return self._kw.get('request_timeout', 60)

    @property
    def stream_timeout(self):
        return self._kw.get('stream_timeout', 0)

    @property
    def recent_time(self):
        return self._kw.get('recent_time', 600)

    @property
    def last_format(self):
        return self._kw.get('last_format', '%m-%d %H:%M')

    @property
    def no_media_upload(self):
        return self._kw.get('no_media_upload', False)

    @property
    def media_retry(self):
        retries = self._kw.get('media_retry', [])
        if not retries and self.no_media_upload:
            retries = [ 0, 5, 10 ]
        return retries

    @property
    def snapshot_checks(self):
        checks = self._kw.get('snapshot_checks', [])
        if not checks:
            checks = [ 1, 5 ]
        return checks

    @property
    def user_agent(self):
        return self._kw.get('user_agent', "apple")

    @property
    def mode_api(self):
        return self._kw.get('mode_api', "auto")

    @property
    def refresh_devices_every(self):
        return self._kw.get('refresh_devices_every', 0) * 60 * 60

    @property
    def http_connections(self):
        return self._kw.get('http_connections', 20)

    @property
    def http_max_size(self):
        return self._kw.get('http_maz_size', 10)

    @property
    def reconnect_every(self):
        return self._kw.get('reconnect_every', 0) * 60

    @property
    def snapshot_timeout(self):
        return self._kw.get('snapshot_timeout', 45)

    @property
    def verbose(self):
        return self._kw.get('verbose_debug', False)

    @property
    def hide_deprecated_services(self):
        return self._kw.get('hide_deprecated_services', False)

    @property
    def tfa_source(self):
        return self._kw.get('tfa_source', TFA_CONSOLE_SOURCE)

    @property
    def tfa_type(self):
        return self._kw.get('tfa_type', TFA_EMAIL_TYPE).lower()

    @property
    def tfa_timeout(self):
        return self._kw.get('tfa_timeout', 3)

    @property
    def tfa_total_timeout(self):
        return self._kw.get('tfa_total_timeout', 60)

    @property
    def tfa_host(self):
        return self._kw.get('tfa_host', TFA_DEFAULT_HOST)

    @property
    def tfa_username(self):
        u = self._kw.get('tfa_username', None)
        if u is None:
            u = self.username
        return u

    @property
    def tfa_password(self):
        p = self._kw.get('tfa_password', None)
        if p is None:
            p = self.password
        return p

    @property
    def wait_for_initial_setup(self):
        return self._kw.get('wait_for_initial_setup', True)

    @property
    def save_state(self):
        return self._kw.get('save_state', True)

    @property
    def state_file(self):
        if self.save_state:
            return self.storage_dir + '/' + self.name + '.pickle'
        return None

    @property
    def dump_file(self):
        if self.dump:
            return self.storage_dir + '/' + 'packets.dump'
        return None

    @property
    def library_days(self):
        return self._kw.get('library_days', PRELOAD_DAYS)

    @property
    def synchronous_mode(self):
        return self._kw.get('synchronous_mode', False)

    @property
    def user_stream_delay(self):
        return self._kw.get('user_stream_delay', 2)

    @property
    def serial_ids(self):
        return self._kw.get('serial_ids', False)

    @property
    def stream_snapshot(self):
        return self._kw.get('stream_snapshot', False)

    @property
    def save_updates_to(self):
        return self._kw.get('save_updates_to', '')
