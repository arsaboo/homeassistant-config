# -*- coding: utf-8 -*-

from . import exceptions
from .remote_legacy import RemoteLegacy
from .remote_websocket import RemoteWebsocket
from .key_mappings import KEYS
from .config import Config

try:
    from .remote_encrypted import RemoteEncrypted
except ImportError:
    RemoteEncrypted = None


class Remote(object):
    def __init__(self, config):
        if isinstance(config, dict):
            config = Config(**config)

        if config.method == "legacy":
            self.remote = RemoteLegacy(config)
        elif config.method == "websocket":
            self.remote = RemoteWebsocket(config)
        elif config.method == "encrypted":
            if RemoteEncrypted is None:
                raise RuntimeError(
                    'Python 2 is not currently supported '
                    'for H and J model year TV\'s'
                )

            self.remote = RemoteEncrypted(config)
        else:
            raise exceptions.ConfigUnknownMethod()

        self.config = config

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def open(self):
        self.remote.open()

    def close(self):
        return self.remote.close()

    def control(self, key):
        return self.remote.control(key)

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]

        if hasattr(self.remote, item):
            return getattr(self.remote, item)

        if item.isupper() and item in KEYS:
            def wrapper():
                KEYS[item](self)

            return wrapper

    def __setattr__(self, key, value):
        if key in ('remote', 'config'):
            object.__setattr__(self, key, value)
            return

        if key in self.remote.__class__.__dict__:
            obj = self.remote.__class__.__dict__[key]
            if hasattr(obj, 'fset'):
                obj.fset(self.remote, value)
