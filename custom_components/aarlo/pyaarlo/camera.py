
import threading
import time
import base64
import zlib

from custom_components.aarlo.pyaarlo.device import ArloChildDevice
from custom_components.aarlo.pyaarlo.util import ( now_strftime,http_get )
from custom_components.aarlo.pyaarlo.constant import( ACTIVITY_STATE_KEY,
                                BRIGHTNESS_KEY,
                                CAPTURED_TODAY_KEY,
                                CHARGER_KEY,
                                CHARGING_KEY,
                                FLIP_KEY,
                                IDLE_SNAPSHOT_URL,
                                LAST_CAPTURE_KEY,
                                LAST_IMAGE_DATA_KEY,
                                LAST_IMAGE_KEY,
                                LAST_IMAGE_SRC_KEY,
                                MEDIA_COUNT_KEY,
                                MEDIA_UPLOAD_KEYS,
                                MIRROR_KEY,
                                MOTION_SENS_KEY,
                                NOTIFY_URL,
                                POWER_SAVE_KEY,
                                PRELOAD_DAYS,
                                SNAPSHOT_KEY,
                                STREAM_SNAPSHOT_KEY,
                                STREAM_SNAPSHOT_URL,
                                STREAM_START_URL )

class ArloCamera(ArloChildDevice):

    def __init__( self,name,arlo,attrs ):
        super().__init__( name,arlo,attrs )
        self._recent = False
        self._recent_job = None
        self._cache_count = None
        self._cached_videos = None
        self._min_days_vdo_cache = PRELOAD_DAYS
        self._lock = threading.Condition()
        self._snapshot_state = 'idle'
        self._clear_snapshot_cb = None
        self._arlo._bg.run_in( self._update_media,10 )

    def _set_recent( self,timeo ):
        with self._lock:
            self._recent = True
            self._arlo._bg.cancel( self._recent_job )
            self._recent_job = self._arlo._bg.run_in( self._clear_recent,timeo )
        self._arlo.debug( 'turning recent ON for ' + self._name )
        self._do_callbacks( 'recentActivity',True )

    def _clear_recent( self ):
        with self._lock:
            self._recent = False
            self._recent_job = None
        self._arlo.debug( 'turning recent OFF for ' + self._name )
        self._do_callbacks( 'recentActivity',False )

    # media library finished. Update our counts
    def _update_media( self ):
        self._arlo.debug('reloading cache for ' + self._name)
        count,videos = self._arlo._ml.videos_for( self )
        if videos:
            captured_today = len([video for video in videos if video.created_today])
            last_captured = videos[0].created_at_pretty( self._arlo._last_format )
        else:
            captured_today = 0
            last_captured = None

        # update local copies
        with self._lock:
            self._cache_count = count
            self._cached_videos = videos

        # signal video up!
        self._save_and_do_callbacks( CAPTURED_TODAY_KEY,captured_today )
        self._save_and_do_callbacks( LAST_CAPTURE_KEY,last_captured )
        self._do_callbacks( 'mediaUploadNotification',True )

    def _clear_snapshot( self ):
        # signal to anybody waiting
        with self._lock:
            if self._snapshot_state != 'idle':
                self._arlo.debug( 'our snapshot finished, signal real state' )
                self._snapshot_state = 'idle'
                self._lock.notify_all()

        # signal real mode, safe to call multiple times
        self._save_and_do_callbacks( ACTIVITY_STATE_KEY,self._arlo._st.get( [self._device_id,ACTIVITY_STATE_KEY],'unknown' ) )

    def _update_media_and_thumbnail( self ):
        self._arlo.debug('getting media image for ' + self.name )
        self._update_media()
        url = None
        with self._lock:
            if self._cached_videos:
                url = self._cached_videos[0].thumbnail_url
        if url is not None:
            self._arlo._st.set( [self.device_id,LAST_IMAGE_KEY],url )
            self._update_last_image()

    def _update_last_image( self ):
        self._arlo.debug('getting image for ' + self.name )
        img = None
        url = self._arlo._st.get( [self.device_id,LAST_IMAGE_KEY],None )
        if url is not None:
            img = http_get( url )
        if img is None:
            self._arlo.debug('using blank image for ' + self.name )
            img = self._arlo.blank_image

        # signal up if nedeed
        self._arlo._st.set( [self.device_id,LAST_IMAGE_SRC_KEY],'capture/' + now_strftime(self._arlo._last_format) )
        self._save_and_do_callbacks( LAST_IMAGE_DATA_KEY,img )

        # handle snapshot not being handled...
        self._clear_snapshot()

    def _update_last_image_from_snapshot( self ):
        self._arlo.debug('getting image for ' + self.name )
        url = self._arlo._st.get( [self.device_id,SNAPSHOT_KEY],None )
        if url is not None:
            img = http_get( url )
            if img is not None:
                # signal up if nedeed
                self._arlo._st.set( [self.device_id,LAST_IMAGE_SRC_KEY],'snapshot/' + now_strftime(self._arlo._last_format) )
                self._save_and_do_callbacks( LAST_IMAGE_DATA_KEY,img )

        # handle snapshot finished
        self._clear_snapshot()

    def _parse_statistic( self,data,scale ):
        """Parse binary statistics returned from the history API"""
        i = 0
        for byte in bytearray(data):
            i = (i << 8) + byte

        if i == 32768:
            return None

        if scale == 0:
            return i

        return float(i) / (scale * 10)

    def _decode_sensor_data( self,properties ):
        """Decode, decompress, and parse the data from the history API"""
        b64_input = ""
        for s in properties.get('payload',[]):
            # pylint: disable=consider-using-join
            b64_input += s
        if b64_input == "":
            return None

        decoded = base64.b64decode(b64_input)
        data = zlib.decompress(decoded)
        points = []
        i = 0

        while i < len(data):
            points.append({
                'timestamp':   int(1e3 * self._parse_statistic( data[i:(i + 4)], 0)),
                'temperature': self._parse_statistic( data[(i + 8):(i + 10)], 1),
                'humidity':    self._parse_statistic( data[(i + 14):(i + 16)], 1),
                'airQuality':  self._parse_statistic( data[(i + 20):(i + 22)], 1)
            })
            i += 22

        return points[-1]

    def _event_handler( self,resource,event ):
        self._arlo.debug( self.name + ' CAMERA got one ' + resource )

        # stream has stopped or recording has stopped
        if resource == 'mediaUploadNotification':

            # look for all possible keys
            for key in MEDIA_UPLOAD_KEYS:
                value = event.get(key,None)
                if value is not None:
                    self._save_and_do_callbacks( key,value )

            # catch this one, update URL if passed in notification
            if LAST_IMAGE_KEY in event:
                self._arlo.debug( self.name + ' thumbnail changed' )
                self.update_last_image()

            # recording stopped then reload library
            if event.get('recordingStopped',False) == True:
                self._arlo.debug( 'recording stopped, updating library' )
                self._arlo._ml.queue_update( self._update_media )

            # snapshot happened?
            value = event.get(STREAM_SNAPSHOT_KEY,'')
            if '/snapshots/' in value:
                self._arlo.debug( 'our snapshot finished, downloading it' )
                self._arlo._st.set( [self.device_id,SNAPSHOT_KEY],value )
                self._arlo._bg.run_low( self._update_last_image_from_snapshot )

            # something just happened!
            self._set_recent( self._arlo._recent_time )

            return

        # no media uploads and stream stopped?
        if self._arlo._no_media_upload:
            if event.get('properties',{}).get('activityState','unknown') == 'idle' and self.is_recording:
                self._arlo.debug( 'got a stream stop' )
                self._arlo._bg.run_in( self._arlo._ml.queue_update,5,cb=self._update_media_and_thumbnail )

        # get it an update last image
        if event.get('action','') == 'fullFrameSnapshotAvailable':
            value = event.get('properties',{}).get('presignedFullFrameSnapshotUrl',None)
            if value is not None:
                self._arlo.debug( 'queing snapshot update' )
                self._arlo._st.set( [self.device_id,SNAPSHOT_KEY],value )
                self._arlo._bg.run_low( self._update_last_image_from_snapshot )

        # ambient sensors update
        if resource.endswith('/ambientSensors/history'):
            data = self._decode_sensor_data( event.get('properties',{}) )
            if data is not None:
                self._save_and_do_callbacks( 'temperature',data.get('temperature') )
                self._save_and_do_callbacks( 'humidity',data.get('humidity') )
                self._save_and_do_callbacks( 'airQuality',data.get('airQuality') )

        # pass on to lower layer
        super()._event_handler( resource,event )

    @property
    def resource_id(self):
        return 'cameras/' + self._device_id

    @property
    def last_image(self):
        return self._arlo._st.get( [self._device_id,LAST_IMAGE_KEY],None )

    # fill this out...
    @property
    def last_image_from_cache(self):
        return self._arlo._st.get( [self._device_id,LAST_IMAGE_DATA_KEY],self._arlo.blank_image )

    @property
    def last_image_source(self):
        return self._arlo._st.get( [self._device_id,LAST_IMAGE_SRC_KEY],'' )

    @property
    def last_video(self):
        with self._lock:
            if self._cached_videos:
                return self._cached_videos[0]
        return None

    def last_N_videos(self,count):
        with self._lock:
            if self._cached_videos:
                return self._cached_videos[:count]
        return []

    @property
    def last_capture(self):
        return self._arlo._st.get( [self._device_id,LAST_CAPTURE_KEY],None )

    @property
    def last_capture_date_format(self):
        return self._arlo._last_format

    @property
    def brightness(self):
        return self._arlo._st.get( [self._device_id,BRIGHTNESS_KEY],None )

    @property
    def flip_state(self):
        return self._arlo._st.get( [self._device_id,FLIP_KEY],None )

    @property
    def mirror_state(self):
        return self._arlo._st.get( [self._device_id,MIRROR_KEY],None )

    @property
    def motion_detection_sensitivity(self):
        return self._arlo._st.get( [self._device_id,MOTION_SENS_KEY],None )

    @property
    def powersave_mode(self):
        return self._arlo._st.get( [self._device_id,POWER_SAVE_KEY],None )

    @property
    def unseen_videos(self):
        return self._arlo._st.get( [self._device_id,MEDIA_COUNT_KEY],0 )

    @property
    def captured_today(self):
        return self._arlo._st.get( [self._device_id,CAPTURED_TODAY_KEY],0 )

    @property
    def min_days_vdo_cache(self):
        return self._min_days_vdo_cache

    @property
    def recent( self ):
        return self._recent

    @property
    def charging( self ):
        return self._arlo._st.get( [self._device_id,CHARGING_KEY],'off' ).lower() == 'on'

    @property
    def charger_type( self ):
        return self._arlo._st.get( [self._device_id,CHARGER_KEY],'None' )

    @property
    def wired( self ):
        return self.charger_type.lower() == 'QuickCharger'

    @property
    def wired_only( self ):
        return not self.charging and self.wired

    @min_days_vdo_cache.setter
    def min_days_vdo_cache(self, value):
        self._min_days_vdo_cache = value

    def update_media( self ):
        self._arlo.debug( 'queing media update' )
        self._arlo._bg.run_low( self._update_media )

    def update_last_image( self ):
        self._arlo.debug( 'queing image update' )
        self._arlo._bg.run_low( self._update_last_image )

    def update_ambient_sensors( self ):
        if self.model_id == 'ABC1000':
            self._arlo._bg.run( self._arlo._be.notify,
                                base=self.base_station,
                                body={"action":"get",
                                        "resource":'cameras/{}/ambientSensors/history'.format(self.device_id),
                                        "publishResponse":False} )


    def has_capability( self,cap ):
        if cap in ( 'last_capture','captured_today','recent_activity','battery_level','signal_strength' ):
            return True
        if cap in ('temperature','humidity','air_quality','airQuality') and self.model_id == 'ABC1000':
            return True
        if cap in ( 'audio','audioDetected','sound' ):
            if (self.model_id.startswith('VMC4030') or self.model_id == 'ABC1000'):
                return True
            if self.device_type.startswith('arloq'):
                return True
        return super().has_capability( cap )

    def take_streaming_snapshot( self ):
        body = {
            'xcloudId': self.xcloud_id,
            'parentId': self.parent_id,
            'deviceId': self.device_id,
            'olsonTimeZone': self.timezone,
        }
        self._save_and_do_callbacks( ACTIVITY_STATE_KEY,'fullFrameSnapshot' )
        self._arlo._bg.run( self._arlo._be.post,url=STREAM_SNAPSHOT_URL,params=body,headers={ "xcloudId":self.xcloud_id } )

    def take_idle_snapshot( self ):
        body = {
            'action': 'set',
            'from': self.web_id,
            'properties': {'activityState': 'fullFrameSnapshot'},
            'publishResponse': True,
            'resource': self.resource_id,
            'to': self.parent_id,
            'transId': self._arlo._be._gen_trans_id()
        }
        self._arlo._bg.run( self._arlo._be.post,url=IDLE_SNAPSHOT_URL,params=body,headers={ "xcloudId":self.xcloud_id } )

    def _request_snapshot( self ):
        if self._snapshot_state == 'idle':
            if self.is_streaming or self.is_recording:
                self._arlo.debug('streaming snapshot')
                self.take_streaming_snapshot()
                self._snapshot_state = 'streaming-snapshot'
            elif not self.is_taking_snapshot:
                self.take_idle_snapshot()
                self._arlo.debug('idle snapshot')
                self._snapshot_state = 'snapshot'
            self._arlo.debug( 'handle dodgy cameras' )
            self._arlo._bg.run_in( self._clear_snapshot,45 )


    def request_snapshot( self ):
        with self._lock:
            self._request_snapshot()
        
    def get_snapshot( self,timeout=30 ):
        with self._lock:
            self._request_snapshot()
            mnow = time.monotonic()
            mend = mnow + timeout
            while mnow < mend and self._snapshot_state != 'idle':
                self._lock.wait( mend - mnow )
                mnow = time.monotonic()
        return self.last_image_from_cache

    @property
    def is_taking_snapshot( self ):
        if self._snapshot_state != 'idle':
            return True
        return self._arlo._st.get( [self._device_id,ACTIVITY_STATE_KEY],'unknown' ) == 'fullFrameSnapshot'

    @property
    def is_recording( self ):
        return self._arlo._st.get( [self._device_id,ACTIVITY_STATE_KEY],'unknown' ) == 'alertStreamActive'

    @property
    def is_streaming( self ):
        return self._arlo._st.get( [self._device_id,ACTIVITY_STATE_KEY],'unknown' ) == 'userStreamActive'

    @property
    def was_recently_active( self ):
        return self._recent

    @property
    def state( self ):
        if self.is_taking_snapshot:
            return 'taking snapshot'
        if self.is_recording:
            return 'recording'
        if self.is_streaming:
            return 'streaming'
        if self.was_recently_active:
            return 'recently active'
        return super().state

    def get_stream( self ):
        body = {
            'action': 'set',
            'from': self.web_id,
            'properties': {'activityState':'startUserStream','cameraId':self.device_id },
            'publishResponse': True,
            'responseUrl':'',
            'resource': self.resource_id,
            'to': self.parent_id,
            'transId': self._arlo._be._gen_trans_id()
        }
        reply = self._arlo._be.post( STREAM_START_URL,body,headers={ "xcloudId":self.xcloud_id } )
        if reply is None:
            return None
        url = reply['url'].replace("rtsp://", "rtsps://")
        self._arlo.debug( 'url={}'.format(url) )
        return url

    def stop_activity( self ):
        self._arlo._bg.run( self._arlo._be.notify,
                                base=self.base_station,
                                body={
                                    'action': 'set',
                                    'properties': { 'activityState':'idle' },
                                    'publishResponse': True,
                                    'resource': self.resource_id,
                                } )
        return True

