# -*- coding: utf-8 -*-
import threading
import base64
import requests
from .utils import LogIt, LogItWithReturn


class Application(object):

    @LogIt
    def __init__(
        self,
        remote,
        name,
        isLock=None,
        is_lock=None,
        appType=None,
        app_type=None,
        position=None,
        appId=None,
        launcherType=None,
        action_type=None,
        mbrIndex=None,
        accelerators=None,
        sourceTypeNum=None,
        icon=None,
        id=None,
        mbrSource=None,
        **kwargs
    ):
        self._remote = remote
        self._is_lock = isLock
        self.name = name
        self.app_type = app_type
        self.position = position
        self.app_id = appId
        self.launcher_type = launcherType
        self.mbr_index = mbrIndex
        if accelerators is not None:
            self._accelerators = accelerators
        else:
            self._accelerators = []
        self.source_type_num = sourceTypeNum
        self._icon = icon
        self.id = id
        self.mbr_source = mbrSource

        self._kwargs = kwargs

    def __getitem__(self, item):
        if item in self._kwargs:
            return self._kwargs[item]

        raise KeyError(item)

    @property
    @LogItWithReturn
    def action_type(self):
        if self.app_type == 2:
            return 'DEEP_LINK'
        else:
            return 'NATIVE_LAUNCH'

    @property
    @LogItWithReturn
    def version(self):
        url = 'http://{0}:8001/api/v2/applications/{1}'.format(
            self._remote.config['host'],
            self.app_id
        )

        response = requests.get(url)
        try:
            response = response.json()
        except:
            return 'Unknown'

        if 'version' not in response:
            return 'Unknown'

        return response['version']

    @property
    @LogItWithReturn
    def is_visible(self):
        url = 'http://{0}:8001/api/v2/applications/{1}'.format(
            self._remote.config['host'],
            self.app_id
        )

        response = requests.get(url)
        try:
            response = response.json()
        except:
            return None

        if 'visible' not in response:
            return None

        return response['visible']

    @property
    @LogItWithReturn
    def is_running(self):
        url = 'http://{0}:8001/api/v2/applications/{1}'.format(
            self._remote.config['host'],
            self.app_id
        )

        response = requests.get(url)
        try:
            response = response.json()
        except:
            return None

        if 'running' not in response:
            return None

        return response['running']

    def get_category(self, title):
        for group in self:
            if group.title.encode() == title.encode():
                return group

    @LogIt
    def run(self, meta_tag=None):
        params = dict(
            event='ed.apps.launch',
            to='host',
            data=dict(
                appId=self.app_id,
                action_type=self.action_type
            )
        )

        if meta_tag is not None:
            params['data']['metaTag'] = meta_tag

        self._remote.send('ms.channel.emit', **params)

    @property
    @LogItWithReturn
    def is_lock(self):
        return bool(self._is_lock)

    def __iter__(self):
        accelerators = dict(
            (accelerator['title'], accelerator)
            for accelerator in self._accelerators
            if accelerator['title'] is not None
        )

        for accelerator_name in sorted(list(accelerators.keys())):
            yield Accelerator(self, **accelerators[accelerator_name])

    @property
    @LogIt
    def icon(self):
        if self._icon:
            params = dict(
                event="ed.apps.icon",
                to="host",
                data=dict(iconPath=self._icon)

            )

            icon = [None]
            event = threading.Event()

            @LogIt
            def app_icon_callback(data):
                data = data['imageBase64']
                if data is not None:
                    data = base64.decodebytes(data)
                icon[0] = data
                event.set()

            self._remote.register_receive_callback(
                app_icon_callback,
                'event',
                'ed.apps.icon'
            )

            self._remote.send("ms.channel.emit", **params)

            event.wait(3.0)
            return icon[0]


class Accelerator(object):

    @LogIt
    def __init__(self, application, title, appDatas, **kwargs):
        self.application = application
        self.title = title
        self._app_datas = appDatas
        self._kwargs = kwargs

    def __getitem__(self, item):
        if item in self._kwargs:
            return self._kwargs[item]

        raise KeyError(item)

    def get_content(self, title):
        for content in self:
            if content.title.encode() == title.encode():
                return content

    def __iter__(self):
        content = dict(
            (app_data['title'], app_data) for app_data in self._app_datas
            if app_data['title'] is not None
        )

        for content_name in sorted(list(content.keys())):
            yield AppData(self.application, **content[content_name])


class AppData(object):

    @LogIt
    def __init__(
        self,
        application,
        isPlayable=None,
        subtitle=None,
        appType=None,
        title=None,
        mbrIndex=None,
        liveLauncherType=None,
        action_play_url=None,
        serviceId=None,
        launcherType=None,
        sourceTypeNum=None,
        action_type=None,
        appId=None,
        subtitle2=None,
        display_from=None,
        display_until=None,
        mbrSource=0,
        id=None,
        subtitle3=None,
        icon=None,
        **kwargs
    ):

        self.application = application
        self._is_playable = isPlayable
        self.subtitle = subtitle
        self.app_type = appType
        self.title = title
        self.mbr_index = mbrIndex
        self.live_launcher_type = liveLauncherType
        self.action_play_url = action_play_url
        self.service_id = serviceId
        self.launcher_type = launcherType
        self.source_type_num = sourceTypeNum
        self.action_type = action_type
        self.app_id = appId
        self.subtitle2 = subtitle2
        self.display_from = display_from
        self.display_until = display_until
        self.mbr_source = mbrSource
        self.id = id
        self.subtitle3 = subtitle3
        self._icon = icon
        self._kwargs = kwargs

    @property
    @LogItWithReturn
    def is_playable(self):
        return bool(self._is_playable)

    def __getitem__(self, item):
        if item in self._kwargs:
            return self._kwargs[item]

        raise KeyError(item)

    @LogIt
    def run(self):
        if self.is_playable:

            if self.action_play_url:
                if isinstance(self.action_play_url, dict):
                    meta_tag = json.dumps(self.action_play_url)
                else:
                    meta_tag = self.action_play_url
            else:
                meta_tag = None

            self.application.run(meta_tag)

    @property
    def icon(self):
        if self._icon:
            params = dict(
                event="ed.apps.icon",
                to="host",
                data=dict(iconPath=self._icon)

            )
            icon = [None]
            event = threading.Event()

            @LogIt
            def content_icon_callback(data):
                data = data['imageBase64']
                if data is not None:
                    data = base64.decodestring(data)
                icon[0] = data
                event.set()

            self.application._remote.register_receive_callback(
                content_icon_callback,
                'event',
                'ed.apps.icon'
            )

            self.application._remote.send("ms.channel.emit", **params)

            event.wait(3.0)
            return icon[0]


