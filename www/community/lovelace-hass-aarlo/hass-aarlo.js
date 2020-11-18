
const LitElement = Object.getPrototypeOf(
        customElements.get("ha-panel-lovelace")
    );
const html = LitElement.prototype.html;

class AarloGlance extends LitElement {
    // To quieten down JetBrains...
    // created_at_pretty;
    // states;
    // image_click;
    // door_bell;
    // door_lock;
    // door2_bell;
    // door2_lock;
    // top_title;
    // top_date;
    // top_status;
    // videos;

    static get properties() {
        return {

            // XXX I wanted these in a Object types but litElement doesn't seem
            // to catch property changes in an object...

            // What media are showing.
            // These are changed by user input on the GUI
            _image: String,
            _video: String,
            _stream: String,
            _library: String,
            _libraryOffset: String,

            // Any time a render is needed we bump this number.
            _change: Number,
        }
    }

    parseURL(url) {
        var parser = document.createElement('a'),
            searchObject = {},
            queries, split, i;
        // Let the browser do the work
        parser.href = url;
        // Convert query string to object
        queries = parser.search.replace(/^\?/, '').split('&');
        for( i = 0; i < queries.length; i++ ) {
            split = queries[i].split('=');
            searchObject[split[0]] = split[1];
        }
        return {
            protocol: parser.protocol,
            host: parser.host,
            hostname: parser.hostname,
            port: parser.port,
            pathname: parser.pathname,
            search: parser.search,
            searchObject: searchObject,
            hash: parser.hash
        };
    }

    constructor() {
        super();

        this._hass = null;
        this._config = null;
        this._change = 0;
        this._hls = null;
        this._dash = null;

        this.resetStatuses();
        this.resetVisiblity();
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
                div.base-1x1 {
                    width: 100%;
                    overflow: hidden;
                    margin: 0;
                    padding-top: 100%;
                    position: relative;
                }
                .img-1x1 {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    width: 100%;
                    transform: translate(-50%, -50%);
                    cursor: pointer;
                }
                .video-1x1 {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    width: 100%;
                    height: auto;
                    transform: translate(-50%, -50%);
                }
                .library-1x1 {
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
                .slidecontainer {
                  width: 70%;
                 text-align: center;
                }
                .slider {
                  -webkit-appearance: none;
                  width: 100%;
                  height: 10px;
                  background: #d3d3d3;
                  outline: none;
                  opacity: 0.7;
                  -webkit-transition: .2s;
                  transition: opacity .2s;
                }
                .slider:hover {
                  opacity: 1;
                }
                .slider::-webkit-slider-thumb {
                  -webkit-appearance: none;
                  appearance: none;
                  width: 10px;
                  height: 10px;
                  background: #4CAF50;
                  cursor: pointer;
                }
                .slider::-moz-range-thumb {
                  width: 10px;
                  height: 10px;
                  background: #4CAF50;
                  cursor: pointer;
                }
            </style>
        `;
    }

    render() {

        return html`
            ${AarloGlance.outerStyleTemplate}
            <ha-card>
            ${AarloGlance.innerStyleTemplate}
            <div id="aarlo-wrapper" class="base-${this._v.aspectRatio}">
                <video class="${this._v.stream} video-${this._v.aspectRatio}"
                    id="stream-${this._s.cameraId}"
                    poster="${this._streamPoster}"
                    @ended="${() => { this.stopStream(); }}"
                    @mouseover="${() => { this.mouseOverVideo(); }}"
                    @click="${() => { this.clickVideo(); }}">
                        Your browser does not support the video tag.
                </video>
                <video class="${this._v.video} video-${this._v.aspectRatio}"
                    autoplay playsinline 
                    id="video-${this._s.cameraId}"
                    src="${this._video}"
                    type="${this._videoType}"
                    poster="${this._videoPoster}"
                    @ended="${() => { this.stopVideo(); }}"
                    @mouseover="${() => { this.mouseOverVideo(); }}"
                    @click="${() => { this.clickVideo(); }}">
                        Your browser does not support the video tag.
                </video>
                <img class="${this._v.image} ${this._v.cameraOn} img-${this._v.aspectRatio}"
                    id="image-${this._s.cameraId}"
                    src="${this._image}"
                    alt="${this._s.imageFullDate}"
                    title="${this._s.imageFullDate}"
                    @click="${() => { this.clickImage(); }}">
                </img>
                <div class="${this._v.library} img-${this._v.aspectRatio}" >
                    <div class="lrow">
                        <div class="lcolumn">
                            <img class="${this._s.libraryItem[0].hidden} library-${this._v.aspectRatio}" 
                                src="${this._s.libraryItem[0].thumbnail}"
                                alt="${this._s.libraryItem[0].captured_at}"
                                title="${this._s.libraryItem[0].captured_at}"
                                @click="${() => { this.showLibraryVideo(0); }}"/>
                            <img class="${this._s.libraryItem[3].hidden} library-${this._v.aspectRatio}"
                                src="${this._s.libraryItem[3].thumbnail}"
                                alt="${this._s.libraryItem[3].captured_at}"
                                title="${this._s.libraryItem[3].captured_at}"
                                @click="${() => { this.showLibraryVideo(3); }}"/>
                            <img class="${this._s.libraryItem[6].hidden} library-${this._v.aspectRatio}"
                                src="${this._s.libraryItem[6].thumbnail}"
                                alt="${this._s.libraryItem[6].captured_at}"
                                title="${this._s.libraryItem[6].captured_at}"
                                @click="${() => { this.showLibraryVideo(6); }}"/>
                        </div>
                        <div class="lcolumn">
                            <img class="${this._s.libraryItem[1].hidden} library-${this._v.aspectRatio}"
                                src="${this._s.libraryItem[1].thumbnail}"
                                alt="${this._s.libraryItem[1].captured_at}"
                                title="${this._s.libraryItem[1].captured_at}"
                                @click="${() => { this.showLibraryVideo(1); }}"/>
                            <img class="${this._s.libraryItem[4].hidden} library-${this._v.aspectRatio}"
                                src="${this._s.libraryItem[4].thumbnail}"
                                alt="${this._s.libraryItem[4].captured_at}"
                                title="${this._s.libraryItem[4].captured_at}"
                                @click="${() => { this.showLibraryVideo(4); }}"/>
                            <img class="${this._s.libraryItem[7].hidden} library-${this._v.aspectRatio}"
                                src="${this._s.libraryItem[7].thumbnail}"
                                alt="${this._s.libraryItem[7].captured_at}"
                                title="${this._s.libraryItem[7].captured_at}"
                                @click="${() => { this.showLibraryVideo(7); }}"/>
                        </div>
                        <div class="lcolumn">
                            <img class="${this._s.libraryItem[2].hidden} library-${this._v.aspectRatio}"
                                src="${this._s.libraryItem[2].thumbnail}"
                                alt="${this._s.libraryItem[2].captured_at}"
                                title="${this._s.libraryItem[2].captured_at}"
                                @click="${() => { this.showLibraryVideo(2); }}"/>
                            <img class="${this._s.libraryItem[5].hidden} library-${this._v.aspectRatio}"
                                src="${this._s.libraryItem[5].thumbnail}"
                                alt="${this._s.libraryItem[5].captured_at}"
                                title="${this._s.libraryItem[5].captured_at}"
                                @click="${() => { this.showLibraryVideo(5); }}"/>
                            <img class="${this._s.libraryItem[8].hidden} library-${this._v.aspectRatio}"
                                src="${this._s.libraryItem[8].thumbnail}"
                                alt="${this._s.libraryItem[8].captured_at}"
                                title="${this._s.libraryItem[8].captured_at}"
                                @click="${() => { this.showLibraryVideo(8); }}"/>
                        </div>
                    </div>
                </div>
                <div class="${this._v.brokeStatus} img-${this._v.aspectRatio}" style="height: 100px" id="brokenImage"></div>
            </div>
            <div class="box box-top ${this._v.topBar}">
                <div class="box-title ${this._v.topTitle}">
                    ${this._s.cameraName} 
                </div>
                <div class="box-status ${this._v.topDate} ${this._v.image_date}" title="${this._s.imageFullDate}">
                    ${this._s.imageDate}
                </div>
                <div class="box-status ${this._v.topStatus}">
                    ${this._s.cameraState}
                </div>
            </div>
            <div class="box box-bottom ${this._v.bottomBar}">
                <div class="box-title ${this._v.bottomTitle}">
                    ${this._s.cameraName} 
                </div>
                <div class="${this._v.cameraOn}">
                    <ha-icon @click="${() => { this.toggleCamera(); }}" class="${this._s.onOffOn} ${this._v.onOff}" icon="${this._s.onOffIcon}" title="${this._s.onOffText}"></ha-icon>
                    <ha-icon @click="${() => { this.moreInfo(this._s.motionId); }}" class="${this._s.motionOn} ${this._v.motion}" icon="mdi:run-fast" title="${this._s.motionText}"></ha-icon>
                    <ha-icon @click="${() => { this.moreInfo(this._s.soundId); }}" class="${this._s.soundOn} ${this._v.sound}" icon="mdi:ear-hearing" title="${this._s.soundText}"></ha-icon>
                    <ha-icon @click="${() => { this.showLibrary(0); }}" class="${this._s.capturedOn} ${this._v.captured}" icon="${this._s.capturedIcon}" title="${this._s.capturedText}"></ha-icon>
                    <ha-icon @click="${() => { this.showOrStopStream(); }}" class="${this._s.playOn} ${this._v.play}" icon="${this._s.playIcon}" title="${this._s.playText}"></ha-icon>
                    <ha-icon @click="${() => { this.wsUpdateSnapshot(); }}" class="${this._s.snapshotOn} ${this._v.snapshot}" icon="${this._s.snapshotIcon}" title="${this._s.snapshotText}"></ha-icon>
                    <ha-icon @click="${() => { this.moreInfo(this._s.batteryId); }}" class="${this._s.batteryState} ${this._v.battery}" icon="mdi:${this._s.batteryIcon}" title="${this._s.batteryText}"></ha-icon>
                    <ha-icon @click="${() => { this.moreInfo(this._s.signalId); }}" class="state-update ${this._v.signal}" icon="${this._s.signalIcon}" title="${this._s.signalText}"></ha-icon>
                    <ha-icon @click="${() => { this.toggleLight(this._s.lightId); }}" class="${this._s.lightOn} ${this._v.lightLeft}" icon="${this._s.lightIcon}" title="${this._s.lightText}"></ha-icon>
                </div>
                <div class="${this._v.cameraOff}">
                    <ha-icon @click="${() => { this.toggleCamera(); }}" class="${this._s.onOffOn} ${this._v.onOff}" icon="${this._s.onOffIcon}" title="${this._s.onOffText}"></ha-icon>
                    <ha-icon @click="${() => { this.showLibrary(0); }}" class="${this._s.capturedOn} ${this._v.captured}" icon="${this._s.capturedIcon}" title="${this._s.capturedText}"></ha-icon>
                </div>
                <div class="box-title ${this._v.bottomDate} ${this._v.image_date}" title="${this._s.imageFullDate}">
                    ${this._s.imageDate}
                </div>
                <div class="box-status ${this._v.externalsStatus}">
                    <ha-icon @click="${() => { this.moreInfo(this._s.doorId); }}" class="${this._s.doorOn} ${this._v.door}" icon="${this._s.doorIcon}" title="${this._s.doorText}"></ha-icon>
                    <ha-icon @click="${() => { this.moreInfo(this._s.doorBellId); }}" class="${this._s.doorBellOn} ${this._v.doorBell}" icon="${this._s.doorBellIcon}" title="${this._s.doorBellText}"></ha-icon>
                    <ha-icon @click="${() => { this.toggleLock(this._s.doorLockId); }}" class="${this._s.doorLockOn} ${this._v.doorLock}" icon="${this._s.doorLockIcon}" title="${this._s.doorLockText}"></ha-icon>
                    <ha-icon @click="${() => { this.moreInfo(this._s.door2Id); }}" class="${this._s.door2On} ${this._v.door2}" icon="${this._s.door2Icon}" title="${this._s.door2Text}"></ha-icon>
                    <ha-icon @click="${() => { this.moreInfo(this._s.door2BellId); }}" class="${this._s.door2BellOn} ${this._v.door2Bell}" icon="${this._s.door2BellIcon}" title="${this._s.door2BellText}"></ha-icon>
                    <ha-icon @click="${() => { this.toggleLock(this._s.door2LockId); }}" class="${this._s.door2LockOn} ${this._v.door2Lock}" icon="${this._s.door2LockIcon}" title="${this._s.door2LockText}"></ha-icon>
                    <ha-icon @click="${() => { this.toggleLight(this._s.lightId); }}" class="${this._s.lightOn} ${this._v.lightRight}" icon="${this._s.lightIcon}" title="${this._s.lightText}"></ha-icon>
                </div>
                <div class="box-status ${this._v.bottomStatus}">
                    ${this._s.cameraState}
                </div>
            </div>
            <div class="box box-bottom-small ${this._v.library}">
                <div >
                    <ha-icon @click="${() => { this.setLibraryBase(this._libraryOffset - 9); }}" class="${this._v.libraryPrev} state-on" icon="mdi:chevron-left" title="previous"></ha-icon>
                </div>
                <div >
                    <ha-icon @click="${() => { this.stopLibrary(); }}" class="state-on" icon="mdi:close" title="close library"></ha-icon>
                </div>
                <div >
                    <ha-icon @click="${() => { this.setLibraryBase(this._libraryOffset + 9); }}" class="${this._v.libraryNext} state-on" icon="mdi:chevron-right" title="next"></ha-icon>
                </div>
            </div>
            <div class="box box-bottom ${this._v.videoControls}">
                <div >
                    <ha-icon @click="${() => { this.toggleLock(this._s.doorLockId); }}" class="${this._s.doorLockOn} ${this._v.doorLock}" icon="${this._s.doorLockIcon}" title="${this._s.doorLockText}"></ha-icon>
                    <ha-icon @click="${() => { this.toggleLight(this._s.lightId); }}" class="${this._s.lightOn} ${this._v.light}" icon="${this._s.lightIcon}" title="${this._s.lightText}"></ha-icon>
                    <ha-icon @click="${() => { this.controlStopVideoOrStream(); }}" class="${this._v.videoStop}" icon="mdi:stop" title="Click to stop"></ha-icon>
                    <ha-icon @click="${() => { this.controlPlayVideo(); }}" class="${this._v.videoPlay}" icon="mdi:play" title="Click to play"></ha-icon>
                    <ha-icon @click="${() => { this.controlPauseVideo(); }}" class="${this._v.videoPause}" icon="mdi:pause" title="Click to pause"></ha-icon>
                </div>
                <div class='slidecontainer'>
                    <input type="range" id="video-seek-${this._s.cameraId}" value="0" min="1" max="100" class="slider ${this._v.videoSeek}">
                </div>
                <div >
                    <ha-icon @click="${() => { this.controlFullScreen(); }}" class="${this._v.videoFull}" icon="mdi:fullscreen" title="Click to go full screen"></ha-icon>
                </div>
            </div>
            </ha-card>
        `;
    }

    throwError( error ) {
        console.error( error );
        throw new Error( error )
    }

    changed() {
        this._change = new Date().getTime();
        return this._change;
    }

    getState(_id, default_value = '') {
        return this._hass !== null && _id in this._hass.states ?
            this._hass.states[_id] : {
                state: default_value,
                attributes: {
                    friendly_name: 'unknown',
                    wired_only: false,
                    image_source: "unknown",
                    charging: false
                }
            };
    }

    emptyLibrary() {
        this._s.libraryItem = [ ];
        while( this._s.libraryItem.length < 9 ) {
            this._s.libraryItem.push( { 'hidden':'hidden','thumbnail':'/static/images/image-broken.svg','captured_at':'' } )
        }
    }

    resetVisiblity() {
        this._v = {

            // media
            image: 'hidden',
            stream: 'hidden',
            video: 'hidden',
            library: 'hidden',
            broke: 'hidden',
            aspectRatio: '16x9',

            // camera On/Off
            cameraOn: 'hidden',
            cameraOff: 'hidden',

            // decorations
            play: 'hidden',
            snapshot: 'hidden',
            libraryPrev: 'hidden',
            libraryNext: 'hidden',
            topBar: 'hidden',
            bottomBar: 'hidden',
            externalsStatus: 'hidden',
            videoControls: 'hidden',

            // sensors
            date: 'hidden',
            battery: 'hidden',
            signal: 'hidden',
            motion: 'hidden',
            sound: 'hidden',
            captured: 'hidden',
            door: 'hidden',
            door2: 'hidden',
            doorLock: 'hidden',
            door2Lock: 'hidden',
            doorBell: 'hidden',
            door2Bell: 'hidden',

            videoPlay: 'hidden',
            videoStop: 'hidden',
            videoPause: 'hidden',
            videoSeek: 'hidden',
            videoFull: 'hidden',

            light: 'hidden',
            lightLeft: 'hidden',
            lightRight: 'hidden',
        }
    }

    resetStatuses() {
        this._s = {

            cameraName: 'unknown',
            cameraState: 'unknown',

            imageSource: 'unknown',

            playOn: 'not-used',
            playText: 'not-used',
            playIcon: 'mdi:camera',

            onOffOn: 'not-used',
            onOffText: 'not-used',
            onOffIcon: 'mdi:camera-off',

            snapshotOn: 'not-used',
            snapshotText: 'not-used',
            snapshotIcon: 'mdi:camera',

            batteryIcon:  'not-used',
            batteryState: 'state-update',
            batteryText:  'not-used',

            signalText: 'not-used',
            signalIcon: 'mdi:wifi-strength-4',

            motionOn: 'not-used',
            motionText: 'not-used',

            soundOn: 'not-used',
            soundText: 'not-used',

            capturedText: 'not-used',
            capturedOn: '',
            capturedIcon: 'mdi:file-video',

            doorOn: 'not-used',
            doorText: 'not-used',
            doorIcon: 'not-used',
            door2On: 'not-used',
            door2Text: 'not-used',
            door2Icon: 'not-used',

            doorLockOn: 'not-used',
            doorLockText: 'not-used',
            doorLockIcon: 'not-used',
            door2LockOn: 'not-used',
            door2LockText: 'not-used',
            door2LockIcon: 'not-used',

            doorBellOn: 'not-used',
            doorBellText: 'not-used',
            doorBellIcon: 'not-used',
            door2BellOn: 'not-used',
            door2BellText: 'not-used',
            door2BellIcon: 'not-used',

            lightOn: 'not-used',
            lightText: 'not-used',
            lightIcon: 'not-used',
        };

        this.emptyLibrary();
    }

    updateStatuses( oldValue ) {

        // nothing?
        if ( this._hass === null ) {
            return;
        }

        // CAMERA
        const camera = this.getState(this._s.cameraId,'unknown');

        // Initial setting? Get camera name.
        if ( oldValue === null ) {
            this._s.cameraName = this._config.name ? this._config.name : camera.attributes.friendly_name;
        }

        // See if camera has changed. Update on the off chance something useful
        // has happened.
        if ( camera.state !== this._s.cameraState ) {
            if ( this._s.cameraState === 'taking snapshot' ) {
                //console.log( 'snapshot ' + this._s.cameraName + ':' + this._s.cameraState + '-->' + camera.state );
                this.updateCameraImageSrc();
                this.updateCameraImageSourceLater(5);
                this.updateCameraImageSourceLater(10)
            } else {
                //console.log( 'updating2 ' + this._s.cameraName + ':' + this._s.cameraState + '-->' + camera.state );
                this.updateCameraImageSrc()
            }
        }

        // Save out current state for later.
        this._s.cameraState = camera.state;

        if ( this._s.imageSource !== camera.attributes.image_source ) {
            //console.log( 'updating3 ' + this._s.cameraName + ':' + this._s.imageSource + '-->' + camera.attributes.image_source );
            this._s.imageSource = camera.attributes.image_source
            this.updateCameraImageSrc()
        }

        // FUNCTIONS
        if( this._v.play === '' ) {
            this._s.playOn = 'state-on';
            if ( camera.state !== 'streaming' ) {
                this._s.playText = 'click to live-stream';
                this._s.playIcon = 'mdi:play'
            } else {
                this._s.playText = 'click to stop stream';
                this._s.playIcon = 'mdi:stop'
            }
        }

        if( this._v.onOff === '' ) {
            if ( this._s.cameraState == 'off' ) {
                this._s.onOffOn   = 'state-on';
                this._s.onOffText = 'click to turn camera on';
                this._s.onOffIcon = 'mdi:camera'
                this._v.cameraOff = ''
                this._v.cameraOn  = 'hidden'
            } else {
                this._s.onOffOn   = '';
                this._s.onOffText = 'click to turn camera off';
                this._s.onOffIcon = 'mdi:camera-off'
                this._v.cameraOff = 'hidden'
                this._v.cameraOn  = ''
            }
        } else {
            this._v.cameraOn  = ''
            this._v.cameraOff = 'hidden'
        }



        if( this._v.snapshot === '' ) {
            this._s.snapshotOn   = '';
            this._s.snapshotText = 'click to update image';
            this._s.snapshotIcon = 'mdi:camera'
        }

        // SENSORS
        if( this._v.battery === '' ) {
            if ( camera.attributes.wired_only ) {
                this._s.batteryText  = 'Plugged In';
                this._s.batteryIcon  = 'power-plug';
                this._s.batteryState = 'state-update';
            } else {
                const battery = this.getState(this._s.batteryId, 0);
                const batteryPrefix = camera.attributes.charging ? 'battery-charging' : 'battery';
                this._s.batteryText  = 'Battery Strength: ' + battery.state +'%';
                this._s.batteryIcon  = batteryPrefix + ( battery.state < 10 ? '-outline' :
                                                    ( battery.state > 90 ? '' : '-' + Math.round(battery.state/10) + '0' ) );
                this._s.batteryState = battery.state < 25 ? 'state-warn' : ( battery.state < 15 ? 'state-error' : 'state-update' );
            }
        }

        if( this._v.signal === '' ) {
            const signal = this.getState(this._s.signalId, 0);
            this._s.signalText = 'Signal Strength: ' + signal.state;
            this._s.signalIcon = signal.state === 0 ? 'mdi:wifi-outline' : 'mdi:wifi-strength-' + signal.state;
        }

        if( this._v.motion === '' ) {
            this._s.motionOn   = this.getState(this._s.motionId,'off').state === 'on' ? 'state-on' : '';
            this._s.motionText = 'Motion: ' + (this._s.motionOn !== '' ? 'detected' : 'clear');
        }

        if( this._v.sound === '' ) {
            this._s.soundOn   = this.getState(this._s.soundId,'off').state === 'on' ? 'state-on' : '';
            this._s.soundText = 'Sound: ' + (this._s.soundOn !== '' ? 'detected' : 'clear');
        }

        if( this._v.captured === '' ) {
            const captured = this.getState(this._s.captureId, 0).state;
            const last = this.getState(this._s.lastId, 0).state;
            this._s.capturedText = 'Captured: ' + ( captured === 0 ? 'nothing today' : captured + ' clips today, last at ' + last );
            this._s.capturedIcon = this._video ? 'mdi:stop' : 'mdi:file-video';
            this._s.capturedOn   = captured !== 0 ? 'state-update' : ''
        }

        // OPTIONAL DOORS
        if( this._v.door === '' ) {
            const doorState = this.getState(this._s.doorId, 'off');
            this._s.doorOn   = doorState.state === 'on' ? 'state-on' : '';
            this._s.doorText = doorState.attributes.friendly_name + ': ' + (this._s.doorOn === '' ? 'closed' : 'open');
            this._s.doorIcon = this._s.doorOn === '' ? 'mdi:door' : 'mdi:door-open';
        }
        if( this._v.door2 === '' ) {
            const door2State = this.getState(this._s.door2Id, 'off');
            this._s.door2On   = door2State.state === 'on' ? 'state-on' : '';
            this._s.door2Text = door2State.attributes.friendly_name + ': ' + (this._s.door2On === '' ? 'closed' : 'open');
            this._s.door2Icon = this._s.door2On === '' ? 'mdi:door' : 'mdi:door-open';
        }

        if( this._v.doorLock === '' ) {
            const doorLockState = this.getState(this._s.doorLockId, 'locked');
            this._s.doorLockOn   = doorLockState.state === 'locked' ? 'state-on' : 'state-warn';
            this._s.doorLockText = doorLockState.attributes.friendly_name + ': ' + (this._s.doorLockOn === 'state-on' ? 'locked (click to unlock)' : 'unlocked (click to lock)');
            this._s.doorLockIcon = this._s.doorLockOn === 'state-on' ? 'mdi:lock' : 'mdi:lock-open';
        }
        if( this._v.door2Lock === '' ) {
            const door2LockState = this.getState(this._s.door2LockId, 'locked');
            this._s.door2LockOn   = door2LockState.state === 'locked' ? 'state-on' : 'state-warn';
            this._s.door2LockText = door2LockState.attributes.friendly_name + ': ' + (this._s.door2LockOn === 'state-on' ? 'locked (click to unlock)' : 'unlocked (click to lock)');
            this._s.door2LockIcon = this._s.door2LockOn === 'state-on' ? 'mdi:lock' : 'mdi:lock-open';
        }

        if( this._v.doorBell === '' ) {
            const doorBellState = this.getState(this._s.doorBellId, 'off');
            this._s.doorBellOn   = doorBellState.state === 'on' ? 'state-on' : '';
            this._s.doorBellText = doorBellState.attributes.friendly_name + ': ' + (this._s.doorBellOn === 'state-on' ? 'ding ding!' : 'idle');
            this._s.doorBellIcon = 'mdi:doorbell-video';
        }
        if( this._v.door2Bell === '' ) {
            const door2BellState = this.getState(this._s.door2BellId, 'off');
            this._s.door2BellOn   = door2BellState.state === 'on' ? 'state-on' : '';
            this._s.door2BellText = door2BellState.attributes.friendly_name + ': ' + (this._s.door2BellOn === 'state-on' ? 'ding ding!' : 'idle');
            this._s.door2BellIcon = 'mdi:doorbell-video';
        }

        if( this._v.light === '' ) {
            const lightState = this.getState(this._s.lightId, 'off');
            this._s.lightOn   = lightState.state === 'on' ? 'state-on' : '';
            this._s.lightText = lightState.attributes.friendly_name + ': ' + (this._s.lightOn === 'state-on' ? 'on!' : 'off');
            this._s.lightIcon = 'mdi:lightbulb';
            this._v.lightLeft = this._s.lightLeft ? '' : 'hidden';
            this._v.lightRight = this._s.lightLeft ? 'hidden' : '';
        }

        this.changed();
    }

    updateMedia() {

        // reset everything...
        this._v.stream      = 'hidden';
        this._v.video       = 'hidden';
        this._v.library     = 'hidden';
        this._v.libraryPrev = 'hidden';
        this._v.libraryNext = 'hidden';
        this._v.image       = 'hidden';
        this._v.topBar      = 'hidden';
        this._v.bottomBar   = 'hidden';
        this._v.brokeStatus = 'hidden';
        this._v.videoControls = 'hidden';

        if( this._stream ) {
            this._v.stream = '';
            this._v.videoPlay = 'hidden';
            this._v.videoStop = '';
            this._v.videoPause = 'hidden';
            this._v.videoSeek = 'hidden';
            this._v.videoFull = '';
            this.showVideoControls(2);

            const video = this.shadowRoot.getElementById('stream-' + this._s.cameraId);

            if ( this._v.playDirect ) {
                // mpeg-dash support
                if (this._dash === null) {

                    const parser = this.parseURL(this._stream);
                    const et = parser.searchObject.egressToken;

                    this._dash = dashjs.MediaPlayer().create();
                    this._dash.extend("RequestModifier", function () {
                        return {
                            modifyRequestHeader: function (xhr) {
                                xhr.setRequestHeader('Egress-Token',et);
                                return xhr;
                            }
                        };
                    }, true);
                    this._dash.initialize(video, this._stream, true);
                    // this._dash.updateSettings({
                        // 'debug': {
                            // 'logLevel': dashjs.Debug.LOG_LEVEL_DEBUG
                        // }
                    // });
                }
            } else {
                // Start HLS to handle video streaming.
                if (this._hls === null) {
                    if (Hls.isSupported()) {
                        this._hls = new Hls();
                        this._hls.attachMedia(video);
                        this._hls.on(Hls.Events.MEDIA_ATTACHED, () => {
                            this._hls.loadSource(this._stream);
                            this._hls.on(Hls.Events.MANIFEST_PARSED, () => {
                                video.play();
                            });
                        })
                    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
                        video.src = this._stream;
                        video.addEventListener('loadedmetadata', function () {
                            video.play();
                        });
                    }
                }
            }

        } else if( this._video ) {
            this._v.video = '';
            this._v.videoPlay = 'hidden';
            this._v.videoStop = '';
            this._v.videoPause = '';
            this._v.videoSeek = '';
            this._v.videoFull = '';
            this._v.light = 'hidden';
            this.setUpSeekBar();
            this.showVideoControls(2);

        } else if ( this._library ) {

            this.emptyLibrary();
            this._v.library     = '';
            this._v.libraryPrev = this._libraryOffset > 0 ? '' : 'hidden';
            this._v.libraryNext = this._libraryOffset + 9 < this._library.length ? '' : 'hidden';
            let i;
            let j;
            const last = Math.min(this._libraryOffset + 9, this._library.length);
            for( i = 0, j = this._libraryOffset; j < last; i++,j++ ) {
                let captured_text = this._library[j].created_at_pretty;
                if ( this._library[j].trigger && this._library[j].trigger !== '' ) {
                    captured_text += ' (' + this._library[j].trigger.toLowerCase() + ')'
                }
                this._s.libraryItem[i] = ( { 'hidden':'',
                                    'thumbnail':this._library[j].thumbnail,
                                    'captured_at':'captured: ' + captured_text } );
            }

        } else if ( this._image ) {
            const camera = this.getState(this._s.cameraId,'unknown');

            this._v.image       = '';
            this._v.brokeStatus = 'hidden';
            this._v.topBar      = this._v.topTitle === '' || this._v.topDate === '' || this._v.topStatus === '' ? '':'hidden';
            this._v.bottomBar   = '';

            // image title
            this._s.imageFullDate = camera.attributes.image_source ? camera.attributes.image_source : '';
            this._s.imageDate = '';
            if( this._s.imageFullDate.startsWith('capture/') ) { 
                this._s.imageDate = this.getState(this._s.lastId,0).state;
                this._s.imageFullDate = 'automatically captured at ' + this._s.imageDate;
            } else if( this._s.imageFullDate.startsWith('snapshot/') ) { 
                this._s.imageDate = this._s.imageFullDate.substr(9);
                this._s.imageFullDate = 'snapshot captured at ' + this._s.imageDate;
            }


        } else {
            this._v.brokeStatus = '';
            this._v.topBar      = this._v.topTitle === '' || this._v.topDate === '' || this._v.topStatus === '' ? '':'hidden';
            this._v.bottomBar   = '';
        }

        this.changed();
    }

    updated(changedProperties) {
        changedProperties.forEach( (oldValue, propName) => {

            switch( propName ) {

                case '_image':
                case '_video':
                case '_stream':
                case '_library':
                case '_libraryOffset':
                    this.updateMedia();
                    break;

                case '_change':
                    //console.log( 'change is updated' );
                    break;
            }
        });
    }

    set hass( hass ) {
        const old = this._hass;
        this._hass = hass;
        this.updateStatuses( old )
    }

    checkConfig() {

        if ( this._hass === null ) {
            return;
        }

        if ( !(this._s.cameraId in this._hass.states) ) {
            this.throwError( 'unknown camera' );
        }
        if ( this._s.doorId && !(this._s.doorId in this._hass.states) ) {
            this.throwError( 'unknown door' )
        }
        if ( this._s.doorBellId && !(this._s.doorBellId in this._hass.states) ) {
            this.throwError( 'unknown door bell' )
        }
        if ( this._s.doorLockId && !(this._s.doorLockId in this._hass.states) ) {
            this.throwError( 'unknown door lock' )
        }
        if ( this._s.door2Id && !(this._s.door2Id in this._hass.states) ) {
            this.throwError( 'unknown door (#2)' )
        }
        if ( this._s.door2BellId && !(this._s.door2BellId in this._hass.states) ) {
            this.throwError( 'unknown door bell (#2)' )
        }
        if ( this._s.door2LockId && !(this._s.door2LockId in this._hass.states) ) {
            this.throwError( 'unknown door lock (#2)' )
        }
    }

    setConfig(config) {

        // find camera
        let camera = null;
        if( config.entity ) {
            camera = config.entity.replace( 'camera.','' );
        }
        if( config.camera ) {
            camera = config.camera;
        }
        if( camera === null ) {
            this.throwError( 'missing a camera definition' );
        }
        if( !config.show ) {
            this.throwError( 'missing show components' );
        }

        // see if aarlo prefix, remove from custom names if not present
        let prefix = "";
        if ( camera.startsWith( 'aarlo_','' ) ) {
            camera = camera.replace( 'aarlo_','' )
            prefix = "aarlo_"
        }
        if( config.prefix ) {
            prefix = config.prefix;
        }

        // save new config and reset decoration properties
        this._config = config;
        this.checkConfig();
        this.resetStatuses();

        // camera and sensors
        this._s.cameraId  = config.camera_id ? config.camera_id : 'camera.' + prefix + camera;
        this._s.motionId  = config.motion_id ? config.motion_id : 'binary_sensor.' + prefix + 'motion_' + camera;
        this._s.soundId   = config.sound_id ? config.sound_id : 'binary_sensor.' + prefix + 'sound_' + camera;
        this._s.batteryId = config.battery_id ? config.battery_id : 'sensor.' + prefix + 'battery_level_' + camera;
        this._s.signalId  = config.signal_id ? config.signal_id : 'sensor.' + prefix + 'signal_strength_' + camera;
        this._s.captureId = config.capture_id ? config.capture_id : 'sensor.' + prefix + 'captured_today_' + camera;
        this._s.lastId    = config.last_id ? config.last_id : 'sensor.' + prefix + 'last_' + camera;

        // door definition
        this._s.doorId     = config.door ? config.door: null;
        this._s.doorBellId = config.door_bell ? config.door_bell : null;
        this._s.doorLockId = config.door_lock ? config.door_lock : null;

        // door2 definition
        this._s.door2Id     = config.door2 ? config.door2: null;
        this._s.door2BellId = config.door2_bell ? config.door2_bell : null;
        this._s.door2LockId = config.door2_lock ? config.door2_lock : null;

        // light definition
        this._s.lightId     = config.light ? config.light: null;
        this._s.lightLeft     = config.light_left ? config.light_left : false;

        // what are we hiding?
        const hide = this._config.hide || [];
        const hide_title  = hide.includes('title') ? 'hidden':'';
        const hide_date   = hide.includes('date') ? 'hidden':'';
        const hide_status = hide.includes('status') ? 'hidden':'';

        // what are we showing?
        const show = this._config.show || [];

        // aspect ratio
        this._v.aspectRatio = config.aspect_ratio == 'square' ? '1x1' : '16x9';
 
        // on click
        this._v.imageClick = config.image_click ? config.image_click : false;

        // stream directly from Arlo
        this._v.playDirect = config.play_direct ? config.play_direct : false;

        // ui configuration
        this._v.topTitle     = config.top_title ? hide_title:'hidden';
        this._v.topDate      = config.top_date ? hide_date:'hidden';
        this._v.topStatus    = config.top_status ? hide_status:'hidden';
        this._v.bottomTitle  = config.top_title ? 'hidden':hide_title;
        this._v.bottomDate   = config.top_date ? 'hidden':hide_date;
        this._v.bottomStatus = config.top_status ? 'hidden':hide_status;

        this._v.play      = show.includes('play') ? '':'hidden';
        this._v.snapshot  = show.includes('snapshot') ? '':'hidden';
        this._v.onOff     = show.includes('on_off') ? '':'hidden';

        this._v.battery    = show.includes('battery') || show.includes('battery_level') ? '':'hidden';
        this._v.signal     = show.includes('signal_strength') ? '':'hidden';
        this._v.motion     = show.includes('motion') ? '':'hidden';
        this._v.sound      = show.includes('sound') ? '':'hidden';
        this._v.captured   = show.includes('captured') || show.includes('captured_today') ? '':'hidden';
        this._v.image_date = show.includes('image_date') ? '':'hidden';

        this._v.door      = this._s.doorId ? '':'hidden';
        this._v.doorLock  = this._s.doorLockId ? '':'hidden';
        this._v.doorBell  = this._s.doorBellId ? '':'hidden';
        this._v.door2     = this._s.door2Id ? '':'hidden';
        this._v.door2Lock = this._s.door2LockId ? '':'hidden';
        this._v.door2Bell = this._s.door2BellId ? '':'hidden';

        this._v.light = this._s.lightId ? '':'hidden';

        this._v.externalsStatus = ( this._v.door === '' || this._v.doorLock === '' ||
                                    this._v.doorBell === '' || this._v.door2 === '' ||
                                    this._v.door2Lock === '' || this._v.door2Bell === '' ||
                                    this._v.light === '') ? '':'hidden';

        // render changes
        this.changed();
    }

    getCardSize() {
        return 3;
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

    async wsLoadLibrary(at_most ) {
        try {
            const library = await this._hass.callWS({
                type: "aarlo_library",
                entity_id: this._s.cameraId,
                at_most: at_most,
            });
            return ( library.videos.length > 0 ) ? library.videos : null;
        } catch (err) {
            return null
        }
    }

    async wsStartStream() {
        try {
            return await this._hass.callWS({
                type: this._v.playDirect ? "aarlo_stream_url" : "camera/stream",
                entity_id: this._s.cameraId,
            })
        } catch (err) {
            return null
        }
    }

    async wsStopStream() {
        try {
            return await this._hass.callWS({
                type: "aarlo_stop_activity",
                entity_id: this._s.cameraId,
            })
        } catch (err) {
            return null
        }
    }

    async wsUpdateSnapshot() {
        try {
            return await this._hass.callWS({
                type: "aarlo_request_snapshot",
                entity_id: this._s.cameraId
            })
        } catch (err) {
            return null
        }
    }

    async updateCameraImageSrc() {
        const camera = this.getState(this._s.cameraId,'unknown');
        if ( camera != 'unknown' ) {
            this._image = camera.attributes.entity_picture + "&t=" + this.changed();
        } else {
            this._image = null;
        }
    }

    async playVideo() {
        const video = await this.wsLoadLibrary(1);
        if ( video ) {
            this._video       = video[0].url;
            this._videoPoster = video[0].thumbnail;
            this._videoType   = "video/mp4"
        } else {
            this._video       = null;
            this._videoPoster = null;
            this._videoType   = null
        }
    }

    stopVideo() {
        if ( this._video ) {
            const video = this.shadowRoot.getElementById('video-' + this._s.cameraId);
            video.pause();
            this._video = null
        }
    }

    async playStream() {
        const stream = await this.wsStartStream();
        if (stream) {
            this._stream = stream.url;
            this._streamPoster = this._image;
        } else {
            this._stream = null;
            this._streamPoster = null;
        }
    }

    async stopStream() {
        if (this._stream) {
            const stream = this.shadowRoot.getElementById('stream-' + this._s.cameraId);
            stream.pause();
            await this.wsStopStream();
            this._stream = null;
        }
        if (this._hls) {
            this._hls.stopLoad();
            this._hls.destroy();
            this._hls = null
        }
        if (this._dash) {
            this._dash.reset();
            this._dash = null;
        }
    }

    showOrStopStream() {
        const camera = this.getState(this._s.cameraId,'unknown');
        if ( camera.state === 'streaming' ) {
            this.stopStream()
        } else {
            this.playStream()
        }
    }

    async showLibrary(base) {
        this._video = null;
        this._library = await this.wsLoadLibrary(99);
        this._libraryOffset = base
    }

    showLibraryVideo(index) {
        index += this._libraryOffset;
        if (this._library && index < this._library.length) {
            this._video = this._library[index].url;
            this._videoPoster = this._library[index].thumbnail;
        } else {
            this._video = null;
            this._videoPoster = null
        }
    }

    setLibraryBase(base) {
        this._libraryOffset = base
    }

    stopLibrary() {
        this.stopVideo();
        this._library = null
    }

    clickImage() {
        if ( this._v.imageClick === 'play' ) {
            this.playStream()
        } else {
            this.playVideo()
        }
    }

    clickVideo() {
        if (this._v.videoControls === 'hidden') {
            this.showVideoControls(2)
        } else {
            this.hideVideoControls();
        }
    }

    mouseOverVideo() {
        this.showVideoControls(2)
    }

    controlStopVideoOrStream() {
        this.stopVideo();
        this.stopStream();
    }

    controlPauseVideo(  ) {
        const video = this.shadowRoot.getElementById('video-' + this._s.cameraId);
        video.pause();
        this._v.videoPlay = '';
        this._v.videoPause = 'hidden';
        this.changed()
    }

    controlPlayVideo( ) {
        const video = this.shadowRoot.getElementById('video-' + this._s.cameraId);
        video.play();
        this._v.videoPlay = 'hidden';
        this._v.videoPause = '';
        this.changed()
    }

    controlFullScreen() {
        const prefix = this._stream ? 'stream-' : 'video-';
        const video = this.shadowRoot.getElementById( prefix + this._s.cameraId);
        if (video.requestFullscreen) {
            video.requestFullscreen();
        } else if (video.mozRequestFullScreen) {
            video.mozRequestFullScreen(); // Firefox
        } else if (video.webkitRequestFullscreen) {
            video.webkitRequestFullscreen(); // Chrome and Safari
        }
    }

    toggleCamera( ) {
        if ( this._s.cameraState == 'off' ) {
            this._hass.callService( 'camera','turn_on', { entity_id: this._s.cameraId } )
        } else {
            this._hass.callService( 'camera','turn_off', { entity_id: this._s.cameraId } )
        }
    }

    toggleLock( id ) {
        if ( this.getState(id,'locked').state === 'locked' ) {
            this._hass.callService( 'lock','unlock', { entity_id:id } )
        } else {
            this._hass.callService( 'lock','lock', { entity_id:id } )
        }
    }

    toggleLight( id ) {
        if ( this.getState(id,'on').state === 'on' ) {
            this._hass.callService( 'light','turn_off', { entity_id:id } )
        } else {
            this._hass.callService( 'light','turn_on', { entity_id:id } )
        }
    }

    setUpSeekBar() {

        let video = this.shadowRoot.getElementById('video-' + this._s.cameraId);
        let seekBar = this.shadowRoot.getElementById('video-seek-' + this._s.cameraId);

        video.addEventListener("timeupdate", function() {
            seekBar.value = (100 / video.duration) * video.currentTime;
        });

        seekBar.addEventListener("change", function() {
            video.currentTime = video.duration * (seekBar.value / 100);
        });
        seekBar.addEventListener("mousedown", () => {
            this.showVideoControls(0);
            video.pause();
        });
        seekBar.addEventListener("mouseup", () => {
            video.play();
            this.hideVideoControlsLater()
        });
        this.showVideoControls(2);

    }
  
    showVideoControls(seconds = 0) {
        this._v.videoControls = '';
        this.hideVideoControlsCancel();
        if (seconds !== 0) {
            this.hideVideoControlsLater(seconds);
        }
        this.changed()
    }

    hideVideoControls() {
        this.hideVideoControlsCancel();
        this._v.videoControls = 'hidden';
        this.changed()
    }

    hideVideoControlsLater(seconds = 2) {
        this.hideVideoControlsCancel();
        this._s.controlTimeout = setTimeout(() => {
            this._s.controlTimeout = null;
            this.hideVideoControls()
        }, seconds * 1000);
    }

    hideVideoControlsCancel() {
        if ( this._s.controlTimeout !== null ) {
            clearTimeout( this._s.controlTimeout );
            this._s.controlTimeout = null
        }
    }

    updateCameraImageSourceLater(seconds = 2) {
        setTimeout(() => {
            this.updateCameraImageSrc()
        }, seconds * 1000);
    }

}

const s = document.createElement("script");
s.src = 'https://cdn.jsdelivr.net/npm/hls.js@latest';
s.onload = function() {
    const s2 = document.createElement("script");
    s2.src = 'https://cdn.dashjs.org/v3.1.1/dash.all.min.js';
    s2.onload = function() {
        customElements.define('aarlo-glance', AarloGlance);
        // const s3 = document.createElement("script");
        // s3.src = 'https://cdn.jsdelivr.net/npm/mobile-detect@1.4.3/mobile-detect.min.js';
        // s3.onload = function() {
            // customElements.define('aarlo-glance', AarloGlance);
        // }
    };
    document.head.appendChild(s2);
};
document.head.appendChild(s);

// vim: set expandtab:ts=4:sw=4
