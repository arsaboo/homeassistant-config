# -*- coding: utf-8 -*-

import threading
import base64
import requests

# {
#                 "isLock": false,
#                 "name": "Deezer",
#                 "appType": "web_app",
#                 "position": 13,
#                 "appId": 3201608010191,
#                 "launcherType": "launcher",
#                 "action_type": null,
#                 "mbrIndex": null,
#                 "accelerators": [


#                     {
#                         "appDatas": [
#                             {
#                                 "isPlayable": 1,
#                                 "icon": "/opt/usr/home/owner/share/DownloadManager/cexr1qp97S/140696",
#                                 "subtitle": null,
#                                 "appType": "pxdb_app",
#                                 "title": "Rap Bangers",
#                                 "appId": "cexr1qp97S.Deezer",
#                                 "display_from": null,
#                                 "action_play_url": {
#                                     "picture": "http://api.deezer.com/playlist/1996494362/image",
#                                     "md5_image": "882ef931a7a428e7a2b503f530df4ed2",
#                                     "picture_medium": "http://cdn-images.deezer.com/images/playlist/882ef931a7a428e7a2b503f530df4ed2/250x250-000000-80-0-0.jpg",
#                                     "nb_tracks": 60,
#                                     "title": "Rap Bangers",
#                                     "checksum": "cad64684448e832c67aa7d103fafb63c",
#                                     "tracklist": "http://api.deezer.com/playlist/1996494362/tracks",
#                                     "creation_date": "2016-07-05 14:34:42",
#                                     "public": true,
#                                     "link": "http://www.deezer.com/playlist/1996494362",
#                                     "user": {
#                                         "tracklist": "http://api.deezer.com/user/917475151/flow",
#                                         "type": "user",
#                                         "id": 917475151,
#                                         "name": "Mehdi Rap Editor"
#                                     },
#                                     "picture_small": "http://cdn-images.deezer.com/images/playlist/882ef931a7a428e7a2b503f530df4ed2/56x56-000000-80-0-0.jpg",
#                                     "picture_xl": "http://cdn-images.deezer.com/images/playlist/882ef931a7a428e7a2b503f530df4ed2/1000x1000-000000-80-0-0.jpg",
#                                     "type": "playlist",
#                                     "id": 1996494362,
#                                     "picture_big": "http://cdn-images.deezer.com/images/playlist/882ef931a7a428e7a2b503f530df4ed2/500x500-000000-80-0-0.jpg"
#                                 },
#                                 "liveLauncherType": "",
#                                 "serviceId": "",
#                                 "launcherType": "launcher",
#                                 "action_type": "APP_LAUNCH",
#                                 "mbrIndex": -2,
#                                 "sourceTypeNum": 0,
#                                 "display_until": null,
#                                 "mbrSource": 0,
#                                 "id": 140696,
#                                 "subtitle3": "",
#                                 "subtitle2": ""
#                             },
#                             {
#                                 "isPlayable": 1,
#                                 "icon": "/opt/usr/home/owner/share/DownloadManager/cexr1qp97S/140692",
#                                 "subtitle": null,
#                                 "appType": "pxdb_app",
#                                 "title": "Best Of Rap Bangers 2018",
#                                 "appId": "cexr1qp97S.Deezer",
#                                 "display_from": null,
#                                 "action_play_url": {
#                                     "picture": "http://api.deezer.com/playlist/5171651864/image",
#                                     "md5_image": "de9dee5f90f4ebf0c9c5ba2e69f42691",
#                                     "picture_medium": "http://cdn-images.deezer.com/images/playlist/de9dee5f90f4ebf0c9c5ba2e69f42691/250x250-000000-80-0-0.jpg",
#                                     "nb_tracks": 52,
#                                     "title": "Best Of Rap Bangers 2018",
#                                     "checksum": "e7120c1c76d9dfa4fa7a4a3de4693dc3",
#                                     "tracklist": "http://api.deezer.com/playlist/5171651864/tracks",
#                                     "creation_date": "2018-12-02 16:53:54",
#                                     "public": true,
#                                     "link": "http://www.deezer.com/playlist/5171651864",
#                                     "user": {
#                                         "tracklist": "http://api.deezer.com/user/917475151/flow",
#                                         "type": "user",
#                                         "id": 917475151,
#                                         "name": "Mehdi Rap Editor"
#                                     },
#                                     "picture_small": "http://cdn-images.deezer.com/images/playlist/de9dee5f90f4ebf0c9c5ba2e69f42691/56x56-000000-80-0-0.jpg",
#                                     "picture_xl": "http://cdn-images.deezer.com/images/playlist/de9dee5f90f4ebf0c9c5ba2e69f42691/1000x1000-000000-80-0-0.jpg",
#                                     "type": "playlist",
#                                     "id": 5171651864,
#                                     "picture_big": "http://cdn-images.deezer.com/images/playlist/de9dee5f90f4ebf0c9c5ba2e69f42691/500x500-000000-80-0-0.jpg"
#                                 },
#                                 "liveLauncherType": "",
#                                 "serviceId": "",
#                                 "launcherType": "launcher",
#                                 "action_type": "APP_LAUNCH",
#                                 "mbrIndex": -2,
#                                 "sourceTypeNum": 0,
#                                 "display_until": null,
#                                 "mbrSource": 0,
#                                 "id": 140692,
#                                 "subtitle3": "",
#                                 "subtitle2": ""
#                             },
#                             {
#                                 "isPlayable": 1,
#                                 "icon": "/opt/usr/home/owner/share/DownloadManager/cexr1qp97S/140693",
#                                 "subtitle": null,
#                                 "appType": "pxdb_app",
#                                 "title": "Christmas Pop",
#                                 "appId": "cexr1qp97S.Deezer",
#                                 "display_from": null,
#                                 "action_play_url": {
#                                     "picture": "http://api.deezer.com/playlist/3833591862/image",
#                                     "md5_image": "9c27b60ecdd08c224218610126a86453",
#                                     "picture_medium": "http://cdn-images.deezer.com/images/playlist/9c27b60ecdd08c224218610126a86453/250x250-000000-80-0-0.jpg",
#                                     "nb_tracks": 60,
#                                     "title": "Christmas Pop",
#                                     "checksum": "03ba236386f9474a0227414e4f48d73c",
#                                     "tracklist": "http://api.deezer.com/playlist/3833591862/tracks",
#                                     "creation_date": "2017-11-23 15:40:17",
#                                     "public": true,
#                                     "link": "http://www.deezer.com/playlist/3833591862",
#                                     "user": {
#                                         "tracklist": "http://api.deezer.com/user/753546365/flow",
#                                         "type": "user",
#                                         "id": 753546365,
#                                         "name": "Dom - Pop Music Editor"
#                                     },
#                                     "picture_small": "http://cdn-images.deezer.com/images/playlist/9c27b60ecdd08c224218610126a86453/56x56-000000-80-0-0.jpg",
#                                     "picture_xl": "http://cdn-images.deezer.com/images/playlist/9c27b60ecdd08c224218610126a86453/1000x1000-000000-80-0-0.jpg",
#                                     "type": "playlist",
#                                     "id": 3833591862,
#                                     "picture_big": "http://cdn-images.deezer.com/images/playlist/9c27b60ecdd08c224218610126a86453/500x500-000000-80-0-0.jpg"
#                                 },
#                                 "liveLauncherType": "",
#                                 "serviceId": "",
#                                 "launcherType": "launcher",
#                                 "action_type": "APP_LAUNCH",
#                                 "mbrIndex": -2,
#                                 "sourceTypeNum": 0,
#                                 "display_until": null,
#                                 "mbrSource": 0,
#                                 "id": 140693,
#                                 "subtitle3": "",
#                                 "subtitle2": ""
#                             },
#                             {
#                                 "isPlayable": 1,
#                                 "icon": "/opt/usr/home/owner/share/DownloadManager/cexr1qp97S/140694",
#                                 "subtitle": null,
#                                 "appType": "pxdb_app",
#                                 "title": "2018's Biggest Hits",
#                                 "appId": "cexr1qp97S.Deezer",
#                                 "display_from": null,
#                                 "action_play_url": {
#                                     "picture": "http://api.deezer.com/playlist/1283499335/image",
#                                     "md5_image": "33688a8b06bf539cb5d1d07be5816fa0",
#                                     "picture_medium": "http://cdn-images.deezer.com/images/playlist/33688a8b06bf539cb5d1d07be5816fa0/250x250-000000-80-0-0.jpg",
#                                     "nb_tracks": 60,
#                                     "title": "2018's Biggest Hits",
#                                     "checksum": "8dfeeddf33931c5a66cc89931bf57f55",
#                                     "tracklist": "http://api.deezer.com/playlist/1283499335/tracks",
#                                     "creation_date": "2015-06-26 15:27:47",
#                                     "public": true,
#                                     "link": "http://www.deezer.com/playlist/1283499335",
#                                     "user": {
#                                         "tracklist": "http://api.deezer.com/user/753546365/flow",
#                                         "type": "user",
#                                         "id": 753546365,
#                                         "name": "Dom - Pop Music Editor"
#                                     },
#                                     "picture_small": "http://cdn-images.deezer.com/images/playlist/33688a8b06bf539cb5d1d07be5816fa0/56x56-000000-80-0-0.jpg",
#                                     "picture_xl": "http://cdn-images.deezer.com/images/playlist/33688a8b06bf539cb5d1d07be5816fa0/1000x1000-000000-80-0-0.jpg",
#                                     "type": "playlist",
#                                     "id": 1283499335,
#                                     "picture_big": "http://cdn-images.deezer.com/images/playlist/33688a8b06bf539cb5d1d07be5816fa0/500x500-000000-80-0-0.jpg"
#                                 },
#                                 "liveLauncherType": "",
#                                 "serviceId": "",
#                                 "launcherType": "launcher",
#                                 "action_type": "APP_LAUNCH",
#                                 "mbrIndex": -2,
#                                 "sourceTypeNum": 0,
#                                 "display_until": null,
#                                 "mbrSource": 0,
#                                 "id": 140694,
#                                 "subtitle3": "",
#                                 "subtitle2": ""
#                             },
#                             {
#                                 "isPlayable": 1,
#                                 "icon": "/opt/usr/home/owner/share/DownloadManager/cexr1qp97S/140695",
#                                 "subtitle": null,
#                                 "appType": "pxdb_app",
#                                 "title": "Hits of the Moment",
#                                 "appId": "cexr1qp97S.Deezer",
#                                 "display_from": null,
#                                 "action_play_url": {
#                                     "picture": "http://api.deezer.com/playlist/2098157264/image",
#                                     "md5_image": "b3924470ee53c1180913e06d3cfd006b",
#                                     "picture_medium": "http://cdn-images.deezer.com/images/playlist/b3924470ee53c1180913e06d3cfd006b/250x250-000000-80-0-0.jpg",
#                                     "nb_tracks": 60,
#                                     "title": "Hits of the Moment",
#                                     "checksum": "8dfe26c3e3a7f6ec8257b46901fa3a28",
#                                     "tracklist": "http://api.deezer.com/playlist/2098157264/tracks",
#                                     "creation_date": "2016-08-04 15:42:22",
#                                     "public": true,
#                                     "link": "http://www.deezer.com/playlist/2098157264",
#                                     "user": {
#                                         "tracklist": "http://api.deezer.com/user/753546365/flow",
#                                         "type": "user",
#                                         "id": 753546365,
#                                         "name": "Dom - Pop Music Editor"
#                                     },
#                                     "picture_small": "http://cdn-images.deezer.com/images/playlist/b3924470ee53c1180913e06d3cfd006b/56x56-000000-80-0-0.jpg",
#                                     "picture_xl": "http://cdn-images.deezer.com/images/playlist/b3924470ee53c1180913e06d3cfd006b/1000x1000-000000-80-0-0.jpg",
#                                     "type": "playlist",
#                                     "id": 2098157264,
#                                     "picture_big": "http://cdn-images.deezer.com/images/playlist/b3924470ee53c1180913e06d3cfd006b/500x500-000000-80-0-0.jpg"
#                                 },
#                                 "liveLauncherType": "",
#                                 "serviceId": "",
#                                 "launcherType": "launcher",
#                                 "action_type": "APP_LAUNCH",
#                                 "mbrIndex": -2,
#                                 "sourceTypeNum": 0,
#                                 "display_until": null,
#                                 "mbrSource": 0,
#                                 "id": 140695,
#                                 "subtitle3": "",
#                                 "subtitle2": ""
#                             }
#                         ],
#                         "title": "featured"
#                     }
#                 ],


# {
#             "is_lock": 0,
#             "icon": "/opt/share/webappservice/apps_icon/FirstScreen/111299001912/250x250.png",
#             "app_type": 2,
#             "name": "YouTube",
#             "appId": "111299001912"
#         },

class Application(object):

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
        mbrSource=None
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

    @property
    def action_type(self):
        if self.app_type == 2:
            return 'DEEP_LINK'
        else:
            return 'NATIVE_LAUNCH'

    @property
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
    def is_lock(self):
        return bool(self._is_lock)

    def __iter__(self):
        for accelerator in self._accelerators:
            yield Accelerator(self._remote, **accelerator)

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

            def callback(data):
                data = data['imageBase64']
                if data is not None:
                    data = base64.decodestring(data)
                icon[0] = data
                event.set()

            self._remote.register_receive_callback(
                callback,
                'iconPath',
                self._icon
            )

            self._remote.send("ms.channel.emit", **params)

            event.wait(3.0)
            return icon[0]


class Accelerator(object):

    def __init__(self, remote, title, appDatas):
        self._remote = remote
        self.title = title
        self._app_datas = appDatas

    def __iter__(self):

        for app_data in self._app_datas:
            yield AppData(self._remote, **app_data)


class AppData(object):

    def __init__(
        self,
        remote,
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
        icon=None
    ):

        self._remote = remote
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

    @property
    def is_playable(self):
        return bool(self._is_playable)

    def run(self):
        if self.is_playable and self.action_type:
            params = dict(
                event='ed.apps.launch',
                to='host',
                data=dict(
                    appId=self.app_id,
                    action_type=self.action_type
                )
            )

            if self.action_play_url:
                params['data']['metaTag'] = self.action_play_url

            self._remote.send('ms.channel.emit', **params)

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

            def callback(data):
                data = data['imageBase64']
                if data is not None:
                    data = base64.decodestring(data)
                icon[0] = data
                event.set()

            self._remote.register_receive_callback(
                callback,
                'iconPath',
                self._icon
            )

            self._remote.send("ms.channel.emit", **params)

            event.wait(3.0)
            return icon[0]


