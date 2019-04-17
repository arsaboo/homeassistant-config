
import { LitElement, html } from 'https://unpkg.com/@polymer/lit-element@^0.5.2/lit-element.js?module';

class AarloGlance extends LitElement {

	static get properties() {
		return {
			_hass: Object,
			_config: Object,
			_img: String,
			_stream: String,
			_video: String,
			_library: String,
			_library_base: Number,
		}
	}

	static get outerStyleTemplate() {
		return html`
		<style>
			ha-card {
				position: relative;
				min-height: 48px;
				overflow: hidden;
			}
			.box {
				white-space: var(--paper-font-common-nowrap_-_white-space); overflow: var(--paper-font-common-nowrap_-_overflow); text-overflow: var(--paper-font-common-nowrap_-_text-overflow);
				position: absolute;
				left: 0;
				right: 0;
				background-color: rgba(0, 0, 0, 0.4);
				padding: 4px 8px;
				font-size: 16px;
				line-height: 36px;
				color: white;
				display: flex;
				justify-content: space-between;
			}
			.box-top {
				top: 0;
			}
			.box-bottom {
				bottom: 0;
			}
			.box-bottom-small {
				bottom: 0;
				line-height: 30px;
			}
			.box-title {
				font-weight: 500;
				margin-left: 4px;
			}
			.box-status {
				font-weight: 500;
				margin-right: 4px;
				text-transform: capitalize;
			}
			ha-icon {
				cursor: pointer;
				padding: 2px;
				color: #a9a9a9;
			}
			ha-icon.state-update {
				color: #cccccc;
			}
			ha-icon.state-on {
				color: white;
			}
			ha-icon.state-warn {
				color: orange;
			}
			ha-icon.state-error {
				color: red;
			}
		</style>
		`;
	}

	static get innerStyleTemplate() {
		return html`
			<style>
				div.base-16x9 {
					width: 100%;
					overflow: hidden;
					margin: 0;
					padding-top: 55%;
					position: relative;
				}
				.img-16x9 {
					position: absolute;
					top: 50%;
					left: 50%;
					width: 100%;
					transform: translate(-50%, -50%);
					cursor: pointer;
				}
				.video-16x9 {
					position: absolute;
					top: 50%;
					left: 50%;
					width: 100%;
					height: auto;
					transform: translate(-50%, -50%);
				}
				.library-16x9 {
					cursor: pointer;
					width: 100%;
				}
				.lrow {
				  display: flex;
				  margin: 6px 2px 6px 2px;
				}
				.lcolumn {
				  flex: 32%;
				  padding: 2px;
				}
				.hidden {
					display: none;
				}
				#brokenImage {
					background: grey url("/static/images/image-broken.svg") center/36px
					no-repeat;
				}
			</style>
		`;
	}

    safe_state( _hass,_id,def='' ) {
        return _id in _hass.states ? _hass.states[_id] : { 'state':def,'attributes':{ 'friendly_name':'unknown' } };
    }

    _render( { _hass,_config,_img,_stream,_video,_library,_library_base } ) {

        const camera = this.safe_state(_hass,this._cameraId,'unknown')
        const cameraName = _config.name ? _config.name : camera.attributes.friendly_name;

        // fake out a library
        var libraryItem = [ ]
        while( libraryItem.length < 9 ) {
            libraryItem.push( { 'hidden':'hidden','thumbnail':'/static/images/image-broken.svg','captured_at':'' } )
        }


        // default is hidden
        var streamHidden      = 'hidden';
        var videoHidden       = 'hidden';
        var libraryHidden     = 'hidden';
        var libraryPrevHidden = 'hidden';
        var libraryNextHidden = 'hidden';
        var imageHidden       = 'hidden';
        var topHidden         = 'hidden';
        var bottomHidden      = 'hidden';
        var doorStatusHidden  = 'hidden';
        var brokeHidden       = 'hidden';
        if( _stream ) {
            var streamHidden = '';
        } else if( _video ) {
            var videoHidden = '';
        } else if ( _library ) {
            var libraryHidden     = '';
            var libraryPrevHidden = _library_base > 0 ? '' : 'hidden';
            var libraryNextHidden = _library_base + 9 < _library.length ? '' : 'hidden';
            var i;
            var j;
            for( i = 0, j = _library_base; j < _library.length; i++,j++ ) {
                var captured_text = _library[j].created_at_pretty
                if ( _library[j].object && _library[j].object != '' ) {
                    captured_text += ' (' + _library[j].object.toLowerCase() + ')'
                }
                libraryItem[i] = ( { 'hidden':'',
                    'thumbnail':_library[j].thumbnail,
                    'captured_at':'captured: ' + captured_text } );
            }
        } else {
            var imageHidden   = _img != null ? '':'hidden';
            var brokeHidden   = _img == null ? '':'hidden';
            var topHidden     = this._topTitle || this._topStatus ? '':'hidden';
            var bottomHidden  = '';

            // image title
            var imageFullDate = camera.attributes.image_source ? imageFullDate = camera.attributes.image_source : '';
            var imageDate = ''
            if( imageFullDate.startsWith('capture/') ) {
                imageDate = this.safe_state(_hass,this._lastId,0).state;
                imageFullDate = 'automatically captured at ' + imageDate;
            } else if( imageFullDate.startsWith('snapshot/') ) {
                imageDate = imageFullDate.substr(9);
                imageFullDate = 'snapshot captured at ' + imageDate;
            }


            // for later use!
            this._clientWidth  = this.clientWidth
            this._clientHeight = this.clientHeight
        }

        // what are we showing?
        var show = _config.show || [];
        var batteryHidden  = show.includes('battery') || show.includes('battery_level') ? '' : 'hidden';
        var signalHidden   = show.includes('signal_strength') ? '' : 'hidden';
        var motionHidden   = show.includes('motion') ? '' : 'hidden';
        var soundHidden    = show.includes('sound') ? '' : 'hidden';
        var capturedHidden = show.includes('captured') || show.includes('captured_today') ? '' : 'hidden';
        var playHidden     = show.includes('play') ? '' : 'hidden';
        var snapshotHidden = show.includes('snapshot') ? '' : 'hidden';
        var dateHidden     = show.includes('image_date') ? '' : 'hidden';

        var doorHidden     = this._doorId == undefined ? 'hidden':''
        var doorLockHidden = this._doorLockId == undefined ? 'hidden':''
        var doorBellHidden = this._doorBellId == undefined ? 'hidden':''

        if( batteryHidden == '' ) {
            var battery      = this.safe_state(_hass,this._batteryId,0);
            var batteryText  = 'Battery Strength: ' + battery.state +'%';
            var batteryIcon  = battery.state < 10 ? 'battery-outline' :
                ( battery.state > 90 ? 'battery' : 'battery-' + Math.round(battery.state/10) +'0' );
            var batteryState = battery.state < 25 ? 'state-warn' :
                ( battery.state < 15 ? 'state-error' : 'state-update' );
        } else {
            var batteryText  = 'not-used';
            var batteryIcon  = 'not-used';
            var batteryState = 'state-update';
        }

        if( signalHidden == '' ) {
            var signal      = this.safe_state(_hass,this._signalId,0);
            var signal_text = 'Signal Strength: ' + signal.state;
            var signalIcon  = signal.state == 0 ? 'mdi:wifi-outline' : 'mdi:wifi-strength-' + signal.state;
        } else {
            var signal_text = 'not-used';
            var signalIcon  = 'mdi:wifi-strength-4';
        }

        if( motionHidden == '' ) {
            var motionOn   = this.safe_state(_hass,this._motionId,'off').state == 'on' ? 'state-on' : '';
            var motionText = 'Motion: ' + (motionOn != '' ? 'detected' : 'clear');
        } else {
            var motionOn   = 'not-used';
            var motionText = 'not-used';
        }

        if( soundHidden == '' ) {
            var soundOn    = this.safe_state(_hass,this._soundId,'off').state == 'on' ? 'state-on' : '';
            var soundText  = 'Sound: ' + (soundOn != '' ? 'detected' : 'clear');
        } else {
            var soundOn    = 'not-used'
            var soundText  = 'not-used'
        }

        if( capturedHidden == '' ) {
            var captured     = this.safe_state(_hass,this._captureId,0).state;
            var last         = this.safe_state(_hass,this._lastId,0).state;
            var capturedText = 'Captured: ' + ( captured == 0 ? 'nothing today' :
                captured + ' clips today, last at ' + last )
            var capturedIcon = _video ? 'mdi:stop' : 'mdi:file-video'
            var capturedOn   = captured != 0 ? 'state-update' : ''
        } else {
            var capturedText = 'not-used';
            var capturedOn   = ''
            var capturedIcon = 'mdi:file-video'
        }

        if( playHidden == '' ) {
            var playOn    = 'state-on';
            var playText  = 'click to live-stream'
            var playIcon  = 'mdi:play'
        } else {
            var playOn    = 'not-used'
            var playText  = 'not-used'
            var playIcon  = 'mdi:camera'
        }

        if( snapshotHidden == '' ) {
            var snapshotOn    = '';
            var snapshotText  = 'click to update image'
            var snapshotIcon  = 'mdi:camera'
        } else {
            var snapshotOn    = 'not-used'
            var snapshotText  = 'not-used'
            var snapshotIcon  = 'mdi:camera'
        }

        if( doorHidden == '' ) {
            var doorStatusHidden = '';
            var doorOn       = this.safe_state(_hass,this._doorId,'off').state == 'on' ? 'state-on' : '';
            var doorText     = 'Door: ' + (doorOn == '' ? 'closed' : 'open');
            var doorIcon     = doorOn == '' ? 'mdi:door' : 'mdi:door-open';
        } else {
            var doorOn    = 'not-used'
            var doorText  = 'not-used'
            var doorIcon  = 'not-used'
        }

        if( doorLockHidden == '' ) {
            var doorStatusHidden = '';
            var doorLockOn       = this.safe_state(_hass,this._doorLockId,'locked').state == 'locked' ? 'state-on' : 'state-warn';
            var doorLockText     = 'Lock: ' + (doorLockOn == 'state-on' ? 'locked (click to unlock)' : 'unlocked (click to lock)');
            var doorLockIcon     = doorLockOn == 'state-on' ? 'mdi:lock' : 'mdi:lock-open';
        } else {
            var doorLockOn    = 'not-used'
            var doorLockText  = 'not-used'
            var doorLockIcon  = 'not-used'
        }

        if( doorBellHidden == '' ) {
            var doorStatusHidden = '';
            var doorBellOn       = this.safe_state(_hass,this._doorBellId,'off').state == 'on' ? 'state-on' : '';
            var doorBellText     = 'Bell: ' + (doorBellOn == 'state-on' ? 'ding ding!' : 'idle');
            var doorBellIcon     = 'mdi:doorbell-video';
        } else {
            var doorBellOn    = 'not-used'
            var doorBellText  = 'not-used'
            var doorBellIcon  = 'not-used'
        }

		//type="application/x-mpegURL"
		//type="video/mp4"
		var img = html`
		    ${AarloGlance.innerStyleTemplate}
			<div id="aarlo-wrapper" class="base-16x9">
			    <video class$="${streamHidden} video-16x9"
                    id="stream-${this._cameraId}"
                    poster="${this._stream_poster}"
                    autoplay playsinline controls
                    onended="${(e) => { this.stopStream(this._cameraId); }}"
                    on-click="${(e) => { this.stopStream(this._cameraId); }}">
                        Your browser does not support the video tag.
				</video>
                <video class$="${videoHidden} video-16x9"
                    src="${this._video}" type="${this._video_type}"
                    poster="${this._video_poster}"
                    autoplay playsinline controls
                    onended="${(e) => { this.stopVideo(this._cameraId); }}"
                    on-click="${(e) => { this.stopVideo(this._cameraId); }}">
                        Your browser does not support the video tag.
				</video>
				<img class$="${imageHidden} img-16x9" id="aarlo-image" on-click="${(e) => { this.showVideoOrStream(this._cameraId); }}" src="${_img}" title="${imageFullDate}"/>
				<div class$="${libraryHidden} img-16x9" >
					<div class="lrow">
						<div class="lcolumn">
							<img class$="${libraryItem[0].hidden} library-16x9" on-click="${(e) => { this.showLibraryVideo(this._cameraId,0); }}" src="${libraryItem[0].thumbnail}" title="${libraryItem[0].captured_at}"/>
							<img class$="${libraryItem[3].hidden} library-16x9" on-click="${(e) => { this.showLibraryVideo(this._cameraId,3); }}" src="${libraryItem[3].thumbnail}" title="${libraryItem[3].captured_at}"/>
							<img class$="${libraryItem[6].hidden} library-16x9" on-click="${(e) => { this.showLibraryVideo(this._cameraId,6); }}" src="${libraryItem[6].thumbnail}" title="${libraryItem[6].captured_at}"/>
						</div>
						<div class="lcolumn">
							<img class$="${libraryItem[1].hidden} library-16x9" on-click="${(e) => { this.showLibraryVideo(this._cameraId,1); }}" src="${libraryItem[1].thumbnail}" title="${libraryItem[1].captured_at}"/>
							<img class$="${libraryItem[4].hidden} library-16x9" on-click="${(e) => { this.showLibraryVideo(this._cameraId,4); }}" src="${libraryItem[4].thumbnail}" title="${libraryItem[4].captured_at}"/>
							<img class$="${libraryItem[7].hidden} library-16x9" on-click="${(e) => { this.showLibraryVideo(this._cameraId,7); }}" src="${libraryItem[7].thumbnail}" title="${libraryItem[7].captured_at}"/>
						</div>
						<div class="lcolumn">
							<img class$="${libraryItem[2].hidden} library-16x9" on-click="${(e) => { this.showLibraryVideo(this._cameraId,2); }}" src="${libraryItem[2].thumbnail}" title="${libraryItem[2].captured_at}"/>
							<img class$="${libraryItem[5].hidden} library-16x9" on-click="${(e) => { this.showLibraryVideo(this._cameraId,5); }}" src="${libraryItem[5].thumbnail}" title="${libraryItem[5].captured_at}"/>
							<img class$="${libraryItem[8].hidden} library-16x9" on-click="${(e) => { this.showLibraryVideo(this._cameraId,8); }}" src="${libraryItem[8].thumbnail}" title="${libraryItem[8].captured_at}"/>
						</div>
					</div>
				</div>
				<div class$="${brokeHidden} img-16x9" style="height: 100px" id="brokenImage"></div>
			</div>
		`;

		var state = html`
			<div class$="box box-top ${topHidden}">
				<div class$="box-title ${this._topTitle?'':'hidden'}">
					${cameraName}
				</div>
				<div class$="box-status ${this._topDate?'':'hidden'} ${dateHidden}" title="${imageFullDate}">
					${imageDate}
				</div>
				<div class$="box-status ${this._topStatus?'':'hidden'}">
					${camera.state}
				</div>
			</div>
			<div class$="box box-bottom ${bottomHidden}">
				<div class$="box-title ${this._topTitle?'hidden':''}">
					${cameraName}
				</div>
				<div>
					<ha-icon on-click="${(e) => { this.moreInfo(this._motionId); }}" class$="${motionOn} ${motionHidden}" icon="mdi:run-fast" title="${motionText}"></ha-icon>
					<ha-icon on-click="${(e) => { this.moreInfo(this._soundId); }}" class$="${soundOn} ${soundHidden}" icon="mdi:ear-hearing" title="${soundText}"></ha-icon>
					<ha-icon on-click="${(e) => { this.showLibrary(this._cameraId,0); }}" class$="${capturedOn} ${capturedHidden}" icon="${capturedIcon}" title="${capturedText}"></ha-icon>
					<ha-icon on-click="${(e) => { this.showLiveStream(this._cameraId); }}" class$="${playOn} ${playHidden}" icon="${playIcon}" title="${playText}"></ha-icon>
					<ha-icon on-click="${(e) => { this.updateSnapshot(this._cameraId); }}" class$="${snapshotOn} ${snapshotHidden}" icon="${snapshotIcon}" title="${snapshotText}"></ha-icon>
					<ha-icon on-click="${(e) => { this.moreInfo(this._batteryId); }}" class$="${batteryState} ${batteryHidden}" icon="mdi:${batteryIcon}" title="${batteryText}"></ha-icon>
					<ha-icon on-click="${(e) => { this.moreInfo(this._signalId); }}" class$="state-update ${signalHidden}" icon="${signalIcon}" title="${signal_text}"></ha-icon>
				</div>
				<div class$="box-title ${this._topDate?'hidden':''} ${dateHidden}" title="${imageFullDate}">
					${imageDate}
				</div>
				<div class$="box-status ${doorStatusHidden}">
					<ha-icon on-click="${(e) => { this.moreInfo(this._doorId); }}" class$="${doorOn} ${doorHidden}" icon="${doorIcon}" title="${doorText}"></ha-icon>
					<ha-icon on-click="${(e) => { this.moreInfo(this._doorBellId); }}" class$="${doorBellOn} ${doorBellHidden}" icon="${doorBellIcon}" title="${doorBellText}"></ha-icon>
					<ha-icon on-click="${(e) => { this.toggleLock(this._doorLockId); }}" class$="${doorLockOn} ${doorLockHidden}" icon="${doorLockIcon}" title="${doorLockText}"></ha-icon>
				</div>
				<div class$="box-status ${this._topStatus?'hidden':''}">
					${camera.state}
				</div>
			</div>
			<div class$="box box-bottom-small ${libraryHidden}">
				<div >
					<ha-icon on-click="${(e) => { this.setLibraryBase(this._library_base - 9); }}" class$="${libraryPrevHidden} state-on" icon="mdi:chevron-left" title="previous"></ha-icon>
				</div>
				<div >
					<ha-icon on-click="${(e) => { this.stopLibrary(); }}" class="state-on" icon="mdi:close" title="close library"></ha-icon>
				</div>
				<div >
					<ha-icon on-click="${(e) => { this.setLibraryBase(this._library_base + 9); }}" class$="${libraryNextHidden} state-on" icon="mdi:chevron-right" title="next"></ha-icon>
				</div>
			</div>
		`;

		return html`
			${AarloGlance.outerStyleTemplate}
			<ha-card>
			${img}
			${state}
			</ha-card>
		`;
	}

    _didRender(_props, _changedProps, _prevProps) {
        if ( this._stream ) {
            var video = this.shadowRoot.getElementById( 'stream-' + this._cameraId )
            if ( Hls.isSupported() ) {
                this._hls = new Hls();
                this._hls.loadSource( this._stream )
                this._hls.attachMedia(video);
                this._hls.on(Hls.Events.MANIFEST_PARSED,function() {
                    video.play();
                });
            }
            else if ( video.canPlayType('application/vnd.apple.mpegurl') ) {
                video.src = this._stream
                video.addEventListener('loadedmetadata',function() {
                    video.play();
                });
            }
        }
    }

    set hass( hass ) {
        this._hass = hass
        const camera = this.safe_state(hass,this._cameraId,'unknown')
        if ( this._old_state && this._old_state == 'taking snapshot' && camera.state == 'idle' ) {
            setTimeout( this._updateCameraImageSrc,5000 )
            setTimeout( this._updateCameraImageSrc,10000 )
            setTimeout( this._updateCameraImageSrc,15000 )
        } else {
            this._updateCameraImageSrc()
        }
        this._old_state = camera.state
    }

    setConfig(config) {

        var camera = undefined;
        if( config.entity ) {
            camera = config.entity.replace( 'camera.aarlo_','' );
        }
        if( config.camera ) {
            camera = config.camera;
        }
        if ( camera == undefined ) {
            throw new Error( 'missing a camera definition' );
        }

        if( !config.show ) {
            throw new Error( 'missing show components' );
        }

		// camera definition
        this._config = config;
		this._cameraId  = 'camera.aarlo_' + camera;
		this._motionId  = 'binary_sensor.aarlo_motion_' + camera;
		this._soundId   = 'binary_sensor.aarlo_sound_' + camera;
		this._batteryId = 'sensor.aarlo_battery_level_' + camera;
		this._signalId  = 'sensor.aarlo_signal_strength_' + camera;
		this._captureId = 'sensor.aarlo_captured_today_' + camera;
		this._lastId    = 'sensor.aarlo_last_' + camera;
		if ( this._hass && this._hass.states[this._cameraId] == undefined ) {
			throw new Error( 'unknown camera' );
		}

        // on click
        this._imageClick = config.image_click ? config.image_click : undefined

		// door definition
		this._doorId     = config.door ? config.door: undefined
		this._doorBellId = config.door_bell ? config.door_bell : undefined
		this._doorLockId = config.door_lock ? config.door_lock : undefined
		if ( this._hass && this._door && this._hass.states[this._door] == undefined ) {
			throw new Error( 'unknown door' )
		}
		if ( this._hass && this._doorBellId && this._hass.states[this._doorBellId] == undefined ) {
			throw new Error( 'unknown door bell' )
		}
		if ( this._hass && this._doorLockId && this._hass.states[this._doorLockId] == undefined ) {
			throw new Error( 'unknown door lock' )
		}

		// ui configuration
		this._topTitle  = config.top_title ? config.top_title : false
		this._topDate   = config.top_date ? config.top_date : false
		this._topStatus = config.top_status ? config.top_status : false

		this._updateCameraImageSrc()
    }

    moreInfo( id ) {
        const event = new Event('hass-more-info', {
            bubbles: true,
            cancelable: false,
            composed: true,
        });
        event.detail = { entityId: id };
        this.shadowRoot.dispatchEvent(event);
        return event;
    }

    async readLibrary( id,at_most ) {
        try {
            const library = await this._hass.callWS({
                type: "aarlo_library",
                entity_id: this._cameraId,
                at_most: at_most,
            });
            return ( library.videos.length > 0 ) ? library.videos : null;
        } catch (err) {
            return null
        }
    }

    stopVideo( id ) {
        this._video = null
    }

    async showVideo( id ) {
        var video = await this.readLibrary( id,1 );
        if ( video ) {
            this._video = video[0].url;
            this._video_poster = video[0].thumbnail;
            this._video_type   = "video/mp4"
        } else {
            this._video        = null
            this._video_poster = null
            this._video_type   = null
        }
    }

    async readStream( id,at_most ) {
        try {
            const stream = await this._hass.callWS({
                type: "camera/stream",
                entity_id: this._cameraId,
            });
            return stream
        } catch (err) {
            return null
        }
    }

    stopStream( id ) {
        this._stream = null
        if ( this._hls ) {
            this._hls.stopLoad()
            this._hls.destroy()
            this._hls = null
        }
    }

    async showLiveStream( id ) {
        var stream = await this.readStream( id,1 );
        if ( stream ) {
            this._stream = stream.url;
            this._stream_poster = this._img
            this._stream_type   = 'application/x-mpegURL'
        } else {
            this._stream = null
            this._stream_poster = null
            this._stream_type   = null
        }
    }

    async showVideoOrStream( id ) {
        // on click
        if ( this._imageClick && this._imageClick == 'play' ) {
            this.showLiveStream(id)
        } else {
            this.showVideo(id)
        }
    }


    async showLibrary( id,base ) {
        this._video = null
        this._library = await this.readLibrary( id,99 )
        this._library_base = base
    }

    async showLibraryVideo( id,index ) {
        index += this._library_base
        if ( this._library && index < this._library.length ) {
            this._video = this._library[index].url;
            this._video_poster = this._library[index].thumbnail;
        } else {
            this._video = null
            this._video_poster = null
        }
    }

    setLibraryBase( base ) {
        this._library_base = base
    }

    stopLibrary( ) {
        this._video = null
        this._library = null
    }

    updateSnapshot( id ) {
        this._hass.callService( 'camera','aarlo_request_snapshot', { entity_id:id } )
    }

    async _updateCameraImageSrc() {
        try {
            const { content_type: contentType, content } = await this._hass.callWS({
                type: "camera_thumbnail",
                entity_id: this._cameraId,
            });
            this._img = `data:${contentType};base64, ${content}`;
        } catch (err) {
            this._img = null
        }
    }

    toggleLock( id ) {
        if ( this.safe_state(this._hass,id,'locked').state == 'locked' ) {
            this._hass.callService( 'lock','unlock', { entity_id:id } )
        } else {
            this._hass.callService( 'lock','lock', { entity_id:id } )
        }
    }

    getCardSize() {
        return 3;
    }
}

var s = document.createElement("script");
s.src = 'https://cdn.jsdelivr.net/npm/hls.js@latest'
s.onload = function(e) {
	customElements.define('aarlo-glance', AarloGlance);
};
document.head.appendChild(s);
