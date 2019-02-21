
import threading
import time
import uuid
import json
import requests
import pprint

from custom_components.aarlo.pyaarlo.sseclient import ( SSEClient )
from custom_components.aarlo.pyaarlo.constant import ( LOGOUT_URL,NOTIFY_URL,
                                SUBSCRIBE_URL,
                                UNSUBSCRIBE_URL,
                                TRANSID_PREFIX )

# include token and session details
class ArloBackEnd(object):

    def __init__( self,arlo,username,password,dump,storage_dir ):

        self._arlo = arlo
        self.session       = requests.Session()
        self.request_lock_ = threading.Lock()
        self.lock_         = threading.Condition()

        self._dump      = dump
        self._dump_file = storage_dir + '/' + 'packets.dump'

        self.requests_      = {}
        self.subscriptions_ = {}
        self.callbacks_     = {}

        # increase pool size
        adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
        self.session.mount('https://',adapter)

        # login
        self._connected = self.login( username,password )
        if not self._connected:
            self._arlo.warning( 'failed to log in' )
            return

        # event loop thread - started as needed
        self.ev_thread_ = None
        self._ev_start()

    def _request( self,url,method='GET',params={},headers={},stream=False,raw=False ):
        with self.request_lock_:
            if method == 'GET':
                r = self.session.get( url,params=params,headers=headers,stream=stream)
                if stream is True:
                    return r
            elif method == 'PUT':
                r = self.session.put( url,json=params,headers=headers )
            elif method == 'POST':
                r = self.session.post( url,json=params,headers=headers )
            
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
            with self.lock_:
                if device_id and device_id in self.callbacks_:
                    cbs.extend( self.callbacks_[ device_id ] )
                if 'all' in self.callbacks_:
                    cbs.extend( self.callbacks_[ 'all' ] )
            for cb in cbs:
                cb( resource,response )

    def _ev_loop( self,stream ):
        for event in stream:

                # stopped?
                if event is None:
                    with self.lock_:
                        self.ev_ok_ = False
                        self.lock_.notify_all()
                    break

                response = json.loads( event.data )
                if self._dump:
                    with open( self._dump_file,'a' ) as dump:
                        dump.write( pprint.pformat( response,indent=2 ) + '\n' )

                # logged out? signal exited
                if response.get('action') == 'logout':
                    with self.lock_:
                        self.ev_ok_ = False
                        self.lock_.notify_all()
                        self._arlo.warning( 'logged out? did you log in from elsewhere?' )
                    break

                # connected - yay!
                if response.get('status') == 'connected':
                    with self.lock_:
                        self.ev_ok_ = True
                        self.lock_.notify_all()
                    continue

                # is this from a notify?
                tid = response.get('transId')
                with self.lock_:
                    if tid and tid in self.requests_:
                        self.requests_[ tid ] = response
                        self.lock_.notify_all()
                        continue

                self._ev_dispatcher( response )


    def _ev_thread( self ):
        #try:

        while True:
            self._arlo.debug( 'starting event loop' )
            stream = SSEClient( SUBSCRIBE_URL + self.token,session=self.session )
            self._ev_loop( stream )

            # try relogging in
            with self.lock_:
                self.lock_.wait( 5 )
            self._arlo.debug( 'logging back in' )
            self._connected = self.login( self.username,self.password )
        #except:
            #print( 'connection issues' )

    def _ev_start( self ):
        self.ev_ok_ = False
        self.ev_thread_ = threading.Thread( name="EventStream",target=self._ev_thread,args=() )
        self.ev_thread_.setDaemon(True)
        self.ev_thread_.start()

        # give time to start
        with self.lock_:
            self.lock_.wait( 30 )
        if not self.ev_ok_:
            self._arlo.warning( 'event loop failed to start' )
            self.ev_thread_ = None
            return False
        return True

    def _notify( self,base,body ):
        body['to'] = base.device_id
        body['from'] = self.web_id
        body['transId'] = self._gen_trans_id()
        self.post( NOTIFY_URL + base.device_id,body,headers={ "xcloudId":base.xcloud_id } )
        return body.get('transId')

    def _notify_and_get_response( self,base,body,timeout=120 ):
        tid = self._notify( base,body )
        self.requests_[ tid ] = None
        mnow = time.monotonic()
        mend = mnow + timeout
        while not self.requests_[ tid ]:
            self.lock_.wait( mend - mnow )
            if self.requests_[ tid ]:
                return self.requests_.pop( tid )
            mnow = time.monotonic()
            if ( mnow >= mend ):
                return self.requests_.pop( tid )

    def ping( self,base ):
        with self.lock_:
            return self._notify_and_get_response( base,{ "action":"set","resource":self.sub_id,
                                                                    "publishResponse":False,"properties":{"devices":[base.device_id]} } )

    def async_ping( self,base ):
        with self.lock_:
            return self._notify( base,{ "action":"set","resource":self.sub_id,
                                                                    "publishResponse":False,"properties":{"devices":[base.device_id]} } )

    def async_on_off( self,base,device,privacy_on ):
        with self.lock_:
            return self._notify( base,{ "action":"set","resource":device.resource_id,
                                                                    "publishResponse":True,
                                                                    "properties":{"privacyActive":privacy_on} } )

    # login and set up session
    def login( self,username,password ):
        with self.lock_:

            self.username  = username
            self.password  = password
            body = self.post( 'https://arlo.netgear.com/hmsweb/login/v2', { 'email':self.username,'password':self.password } )
            if not body:
                self._arlo.debug( 'login failed' )
                return False

            # build up frequently used data
            headers = {
                'DNT': '1',
                'schemaVersion': '1',
                'Host': 'arlo.netgear.com',
                'Content-Type': 'application/json; charset=utf-8;',
                'Referer': 'https://arlo.netgear.com/',
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_1_2 like Mac OS X) AppleWebKit/604.3.5 (KHTML, like Gecko) Mobile/15B202 NETGEAR/v1 (iOS Vuezone)',
                'Authorization': body['token']
            }
            self.session.headers.update(headers)

            self.token   = body['token']
            self.user_id = body['userId']
            self.web_id  = self.user_id + '_web'
            self.sub_id  = 'subscriptions/' + self.web_id
            return True

    def is_connected( self ):
        with self.lock_:
            return self._connected

    def logout( self ):
        with self.lock_:
            self.subscriptions_ = {}
            self.requests_ = {}
            self.put( LOGOUT_URL )

    def get( self,url,params={},headers={},stream=False,raw=False ):
        return self._request( url,'GET',params,headers,stream,raw )

    def put( self,url,params={},headers={},raw=False ):
        return self._request( url,'PUT',params,headers,raw )

    def post( self,url,params={},headers={},raw=False ):
        return self._request( url,'POST',params,headers,raw )

    def notify( self,base,body ):
        with self.lock_:
            return self._notify( base,body )

    def notify_and_get_response( self,base,body,timeout=120 ):
        with self.lock_:
            return self._notify_and_get_response( base,body,timeout )

    def add_listener( self,device,callback ):
        with self.lock_:
            if device.device_id not in self.callbacks_:
                self.callbacks_[device.device_id] = []
            self.callbacks_[device.device_id].append( callback )

    def add_any_listener( self,callback ):
        with self.lock_:
            if 'all' not in self.callbacks_:
                self.callbacks_['all'] = []
            self.callbacks_['all'].append( callback )

    def del_listener( self,device,callback ):
        pass

