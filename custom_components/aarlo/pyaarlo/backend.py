
import threading
import time
import uuid
import json
import requests
import pprint

#from sseclient import ( SSEClient )
from custom_components.aarlo.pyaarlo.sseclient import ( SSEClient )
from custom_components.aarlo.pyaarlo.constant import ( EVENT_STREAM_TIMEOUT,
                                LOGIN_URL,
                                LOGOUT_URL,
                                NOTIFY_URL,
                                SUBSCRIBE_URL,
                                UNSUBSCRIBE_URL,
                                TRANSID_PREFIX )

# include token and session details
class ArloBackEnd(object):

    def __init__( self,arlo,username,password,dump,storage_dir,
                        request_timeout,stream_timeout):

        self._arlo     = arlo
        self._lock     = threading.Condition()
        self._req_lock = threading.Lock()

        self._dump      = dump
        self._dump_file = storage_dir + '/' + 'packets.dump'

        self._request_timeout = request_timeout
        self._stream_timeout  = stream_timeout

        self._requests  = {}
        self._callbacks = {}

        # login
        self._session   = None
        self._connected = self.login( username,password )
        if not self._connected:
            self._arlo.warning( 'failed to log in' )
            return

        # event loop thread - started as needed
        self._ev_start()

    def _request( self,url,method='GET',params={},headers={},stream=False,raw=False,timeout=None ):
        if timeout is None:
            timeout = self._request_timeout
        with self._req_lock:
            self._arlo.debug( 'starting request=' + str(url) )
            try:
                if method == 'GET':
                    r = self._session.get( url,params=params,headers=headers,stream=stream,timeout=timeout )
                    if stream is True:
                        return r
                elif method == 'PUT':
                    r = self._session.put( url,json=params,headers=headers,timeout=timeout )
                elif method == 'POST':
                    r = self._session.post( url,json=params,headers=headers,timeout=timeout )
            except:
                self._arlo.warning( 'timeout with backend request' )
                #self._ev_stream.close()
                self._ev_stream.resp.close()
                return None

            if r.status_code != 200:
                self._arlo.warning( 'error with request' )
                return None

            body = r.json()
            if raw:
                return body
            if body['success'] == True:
                if 'data' in body:
                    return body['data']
            return None

    def _gen_trans_id( self, trans_type=TRANSID_PREFIX ):
        return trans_type + '!' + str( uuid.uuid4() )

    def _ev_dispatcher( self,response ):

        # get message type(s) and id(s)
        responses = []
        device_id = None
        resource  = response.get('resource','' )

        err  = response.get('error',None )
        if err is not None:
            self._arlo.info( 'error: code=' + str(err.get('code','xxx')) + ',message=' + str(err.get('message','XXX')) )

        # these are camera or doorbell status updates
        if resource.startswith('cameras/') or resource.startswith('doorbells/'):
            device_id = resource.split('/')[1]
            responses.append( (device_id,resource,response) )

        # this is thumbnail or media library updates
        elif resource == 'mediaUploadNotification':
            device_id = response.get('deviceId')
            responses.append( (device_id,resource,response) )

        # these we split up and pass properties to the individual component
        elif resource == 'cameras' or resource == 'doorbells':
            for props in response.get('properties',[] ):
                device_id = props.get('serialNumber')
                responses.append( (device_id,resource,props) )

        # these are base station specific
        elif resource == 'modes':
            device_id = response.get('from',None )
            responses.append( (device_id,resource,response) )

        # these are base station specific
        elif resource == 'activeAutomations':
            for device_id in response:
                if device_id != 'resource':
                    responses.append( (device_id,resource,response[device_id]) )

        # answer for async ping
        elif resource.startswith('subscriptions/'):
            self._arlo.debug( 'async ping response ' + resource )
            return

        else:
            self._arlo.debug( 'unhandled response ' + resource )
            return

        # now find something waiting for this/these
        for device_id,resource,response in responses:
            cbs = []
            self._arlo.debug( 'sending ' + resource + ' to ' + device_id )
            with self._lock:
                if device_id and device_id in self._callbacks:
                    cbs.extend( self._callbacks[ device_id ] )
                if 'all' in self._callbacks:
                    cbs.extend( self._callbacks[ 'all' ] )
            for cb in cbs:
                cb( resource,response )

    def _ev_loop( self,stream ):
        #for event in stream.events():
        for event in stream:

                # stopped?
                if event is None:
                    with self._lock:
                        self._ev_connected_ = False
                        self._lock.notify_all()
                    break

                response = json.loads( event.data )
                if self._dump:
                    with open( self._dump_file,'a' ) as dump:
                        dump.write( pprint.pformat( response,indent=2 ) + '\n' )

                # logged out? signal exited
                if response.get('action') == 'logout':
                    with self._lock:
                        self._ev_connected_ = False
                        self._lock.notify_all()
                        self._arlo.warning( 'logged out? did you log in from elsewhere?' )
                    break

                # connected - yay!
                if response.get('status') == 'connected':
                    with self._lock:
                        self._ev_connected_ = True
                        self._lock.notify_all()
                    continue

                # is this from a notify? then signal to waiting entity, also
                # pass into dispatcher
                tid = response.get('transId')
                with self._lock:
                    if tid and tid in self._requests:
                        self._requests[ tid ] = response
                        self._lock.notify_all()
                        #continue

                self._ev_dispatcher( response )


    def _ev_thread( self ):

        self._arlo.debug( 'starting event loop' )
        while True:

            # login again if not first iteration, this will also create a new session
            while not self._connected:
                with self._lock:
                    self._lock.wait( 5 )
                self._arlo.debug( 're-logging in' )
                self._connected = self.login( self.username,self.password )

            # get stream, restart after requested seconds of inactivity or forced close
            try:
                if self._stream_timeout == 0:
                    self._arlo.debug( 'starting stream with no timeout' )
                    #self._ev_stream = SSEClient( self.get( SUBSCRIBE_URL + self._token,stream=True,raw=True ) )
                    self._ev_stream = SSEClient( self._arlo,SUBSCRIBE_URL + self._token,session=self._session )
                else:
                    self._arlo.debug( 'starting stream with {} timeout'.format( self._stream_timeout ) )
                    #self._ev_stream = SSEClient( self.get( SUBSCRIBE_URL + self._token,stream=True,raw=True,timeout=self._stream_timeout ) )
                    self._ev_stream = SSEClient( self._arlo,SUBSCRIBE_URL + self._token,session=self._session,timeout=self._stream_timeout )
                self._ev_loop( self._ev_stream )
            except requests.exceptions.ConnectionError as e:
                self._arlo.warning( 'event loop timeout' )
            except AttributeError as e:
                self._arlo.warning( 'forced close' )

            # restart login...
            self._ev_stream = None
            self._connected = False

    def _ev_start( self ):
        self._ev_stream     = None
        self._ev_connected_ = False
        self._evt           = threading.Thread( name="EventStream",target=self._ev_thread,args=() )
        self._evt.setDaemon(True)
        self._evt.start()

        # give time to start
        with self._lock:
            self._lock.wait( 30 )
        if not self._ev_connected_:
            self._arlo.warning( 'event loop failed to start' )
            self._evt = None
            return False
        return True

    def _notify( self,base,body ):
        body['to'] = base.device_id
        body['from'] = self._web_id
        body['transId'] = self._gen_trans_id()
        self.post( NOTIFY_URL + base.device_id,body,headers={ "xcloudId":base.xcloud_id } )
        return body.get('transId')

    def _notify_and_get_response( self,base,body,timeout=None ):
        if timeout is None:
            timeout = self._request_timeout
        tid = self._notify( base,body )
        self._requests[ tid ] = None
        mnow = time.monotonic()
        mend = mnow + timeout
        while not self._requests[ tid ]:
            self._lock.wait( mend - mnow )
            if self._requests[ tid ]:
                return self._requests.pop( tid )
            mnow = time.monotonic()
            if ( mnow >= mend ):
                return self._requests.pop( tid )

    def ping( self,base ):
        with self._lock:
            return self._notify_and_get_response( base,{ "action":"set","resource":self._sub_id,
                                                                    "publishResponse":False,"properties":{"devices":[base.device_id]} } )

    def async_ping( self,base ):
        with self._lock:
            return self._notify( base,{ "action":"set","resource":self._sub_id,
                                                                    "publishResponse":False,"properties":{"devices":[base.device_id]} } )

    def async_on_off( self,base,device,privacy_on ):
        with self._lock:
            return self._notify( base,{ "action":"set","resource":device.resource_id,
                                                                    "publishResponse":True,
                                                                    "properties":{"privacyActive":privacy_on} } )

    # login and set up session
    def login( self,username,password ):
        with self._lock:

            # attempt login
            self.username = username
            self.password = password
            self._session = requests.Session()
            self._session.mount('https://',requests.adapters.HTTPAdapter(pool_connections=5, pool_maxsize=10) )
            body = self.post( LOGIN_URL, { 'email':self.username,'password':self.password } )
            if body is None:
                self._arlo.debug( 'login failed' )
                return False

            # save new login information
            self._token   = body['token']
            self._user_id = body['userId']
            self._web_id  = self._user_id + '_web'
            self._sub_id  = 'subscriptions/' + self._web_id

            # update sessions headers
            # XXX allow different user agent
            headers = {
                'DNT': '1',
                'schemaVersion': '1',
                'Host': 'arlo.netgear.com',
                'Content-Type': 'application/json; charset=utf-8;',
                'Referer': 'https://arlo.netgear.com/',
                'Authorization': self._token
            }
            if self._arlo._user_agent == 'apple':
                headers['User-Agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_1_2 like Mac OS X) AppleWebKit/604.3.5 (KHTML, like Gecko) Mobile/15B202 NETGEAR/v1 (iOS Vuezone)'
            else:
                headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36'

            self._session.headers.update(headers)
            return True

    def is_connected( self ):
        with self._lock:
            return self._connected

    def logout( self ):
        with self._lock:
            self._requests = {}
            self.put( LOGOUT_URL )

    def get( self,url,params={},headers={},stream=False,raw=False,timeout=None ):
        return self._request( url,'GET',params,headers,stream,raw,timeout )

    def put( self,url,params={},headers={},raw=False,timeout=None ):
        return self._request( url,'PUT',params,headers,False,raw,timeout )

    def post( self,url,params={},headers={},raw=False,timeout=None ):
        return self._request( url,'POST',params,headers,False,raw,timeout )

    def notify( self,base,body ):
        with self._lock:
            return self._notify( base,body )

    def notify_and_get_response( self,base,body,timeout=None ):
        with self._lock:
            return self._notify_and_get_response( base,body,timeout )

    def add_listener( self,device,callback ):
        with self._lock:
            if device.device_id not in self._callbacks:
                self._callbacks[device.device_id] = []
            self._callbacks[device.device_id].append( callback )

    def add_any_listener( self,callback ):
        with self._lock:
            if 'all' not in self._callbacks:
                self._callbacks['all'] = []
            self._callbacks['all'].append( callback )

    def del_listener( self,device,callback ):
        pass

