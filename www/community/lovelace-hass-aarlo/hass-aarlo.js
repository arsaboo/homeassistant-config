/**
 * @module Lovelace class for accessing Arlo camera through the AArlo
 * module.
 *
 * Startup Notes:
 * - hass(); called at startup; set initial internal status and then updates
 *   image element data
 * - setConfig(); called at startup; we read out config data and store inside
 *   `?c` variables.
 * - render(); called at startup; we start initialSetup() and return the
 *   skeleton HTML for the card.
 * - initialSetup(); loops until HTML is in place then set up which individual
 *   elements are present (eg, motion sensor if asked for) and then displays
 *   the image card.
 *
 * Running Notes:
 * - hass(); called when state changes; update internal status and then updates
 *   image element data
 *
 * Controlling what's on screen:
 * - setup(Image|library|Video|Stream)View; one off, set visibility that doesn't
 *   change
 * - update(Image|Video|Stream)View; set up text, alt, state and visibility that
 *   do change
 * - show(Image|Video|Stream)View; show layers for this card
 * - hide(Image|Video|Stream)View; don't show layers for this card
 *
 * What's what:
 * - this._gc; global configuration
 * - this._gs; global state
 * - this._cc; all cameras configurations
 * - this._cs; all camara states
 * - this._lc; all library configurations
 * - this._ls; all library states
 */


const LitElement = Object.getPrototypeOf(
        customElements.get("ha-panel-lovelace")
    );
const html = LitElement.prototype.html;

function _real(value) {
    return value !== undefined && value !== null
}
function _array( config, value = [] ) {
    if( !config ) {
        return value
    }
    if( typeof config === "string" ) {
        return config.includes("|") ? config.split("|") : config.split(",")
    }
    if( typeof config === "number" ) {
        return [ config ]
    }
    return config
}
function _pushIf( array, value, cond ) {
    if(cond) {
        array.push(value)
    }
}
function _value( config, value = null ) {
    return config ? config : value
}
function _value_int( config, value = 0 ) {
    return parseInt( _value( config, value ) )
}
function _value_float( config, value = 0 ) {
    return parseFloat( _value( config, value ) )
}
function _includes( config, item, value = false ) {
    return config ? config.includes(item) : value
}
/**
 * Replace all of `from` with `to` and return the new string.
 *
 * @param old_string string we are converting
 * @param from what to replace
 * @param to what to replace it with
 * @returns {*} the new string
 * @private
 */
function _replaceAll( old_string, from, to ) {
    while( true ) {
        const new_string = old_string.replace( from,to )
        if( new_string === old_string ) {
            return new_string
        }
        old_string = new_string
    }
}
function _mergeArrays( left, right ) {
    let merged = Object.assign( {}, left )
    return Object.assign( merged, right )
}
function _tsi(title, state, icon ) {
    return {
        title: title,
        state: state,
        icon:  icon
    }
}

// function _either_or( config, item, true_value = true, false_value = false ) {
//     if (config && item in config) {
//         return config[item] ? true_value : false_value
//     }
//     return false_value
// }

// noinspection JSUnresolvedVariable,CssUnknownTarget,CssUnresolvedCustomProperty,HtmlRequiredAltAttribute,RequiredAttributes,JSFileReferences
class AarloGlance extends LitElement {

    constructor() {
        super();

        // State and config.
        this._ready = false
        this._hass = null;
        this._config = null;
        this._version = "0.2.0b5"

        // Internationalisation.
        this._i = null

        // Maybe gs should be cs/ls; think about multiple videos going...
        this._gc = {}
        this._gs = {}
        this._cc = {}
        this._cs = {}
        this._lc = {}
        this._ls = {}
        this._cameraIndex = 0
    }

    static get styleTemplate() {
        return html`
            <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
            <style>
                ha-card {
                    position: relative;
                    min-height: 48px;
                    overflow: hidden;
                }
                .box {
                    white-space: var(--paper-font-common-nowrap_-_white-space);
                    overflow: var(--paper-font-common-nowrap_-_overflow);
                    text-overflow: var(--paper-font-common-nowrap_-_text-overflow);
                    position: absolute;
                    left: 0;
                    right: 0;
                    background-color: rgba(0, 0, 0, 0.4);
                    padding: 4px 8px;
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
                .box-align-left {
                    margin-left: 4px;
                }
                .box-align-right {
                    margin-right: 4px;
                }
                .camera-name {
                    font-weight: 500;
                }
                .camera-status {
                    font-weight: 500;
                    text-transform: capitalize;
                }
                .camera-date {
                    font-weight: 500;
                    text-transform: capitalize;
                }
                ha-icon {
                    cursor: pointer;
                    padding: 2px;
                    color: #a9a9a9;
                }
                div.aarlo-aspect-16x9 {
                    padding-top: 55%;
                }
                div.aarlo-aspect-1x1 {
                    padding-top: 100%;
                }
                div.aarlo-base {
                    margin: 0;
                    overflow: hidden;
                    position: relative;
                    width: 100%;
                }
                div.aarlo-modal-base {
                    margin: 0 auto;
                    position: relative;
                }
                .aarlo-image {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    width: 100%;
                    transform: translate(-50%, -50%);
                    cursor: pointer;
                }
                .aarlo-video {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    width: 100%;
                    height: auto;
                    transform: translate(-50%, -50%);
                }
                .aarlo-modal-video-wrapper {
                    overflow: hidden;
                    position: absolute;
                    top: 0;
                    left: 0;
                }
                .aarlo-modal-video {
                    position: absolute;
                    top: -8px;
                    left: 0;
                }
                .aarlo-modal-video-background {
                    position: absolute;
                    top: 0;
                    left: 0;
                    background-color: darkgrey;
                }
                .aarlo-library {
                    width: 100%;
                    cursor: pointer;
                }
                .aarlo-library-row {
                    display: flex;
                    margin: 6px 2px 6px 2px;
                }
                .aarlo-library-column {
                    flex: 32%;
                    padding: 2px;
                }
                .aarlo-text-medium {
                    font-size: 16px;
                    line-height: 26px;
                }
                .aarlo-text-small {
                    font-size: 14px;
                    line-height: 24px;
                }
                .aarlo-text-tiny {
                    font-size: 12px;
                    line-height: 22px;
                }
                .aarlo-icon-medium {
                }
                .aarlo-icon-small {
                    --mdc-icon-size: 18px;
                    height: 18px;
                    width: 18px;
                }
                .aarlo-icon-tiny {
                    --mdc-icon-size: 14px;
                    height: 14px;
                    width: 14px;
                }
                .aarlo-broken-image {
                    background: grey url("/static/images/image-broken.svg") center/36px
                    no-repeat;
                }
                .slidecontainer {
                    text-align: center;
                    width: 70%;
                }
                .slider {
                    -webkit-appearance: none;
                    background: #d3d3d3;
                    outline: none;
                    opacity: 0.7;
                    width: 100%;
                    height: 10px;
                    -webkit-transition: .2s;
                    transition: opacity .2s;
                }
                .slider:hover {
                    opacity: 1;
                }
                .slider::-webkit-slider-thumb {
                    -webkit-appearance: none;
                    appearance: none;
                    background: #4CAF50;
                    width: 10px;
                    height: 10px;
                    cursor: pointer;
                }
                .slider::-moz-range-thumb {
                    background: #4CAF50;
                    width: 10px;
                    height: 10px;
                    cursor: pointer;
                }
            </style>
        `;
    }

    render() {
        this.initialSetup()
        return html`
            ${AarloGlance.styleTemplate}
            <div class="w3-modal"
                 id="${this._id('modal-viewer')}"
                 style="display:none">
                <div class="w3-modal-content w3-animate-opacity aarlo-modal-base"
                     id="${this._id('modal-content')}">
                    <div class="aarlo-modal-video-wrapper"
                         id="${this._id('modal-video-wrapper')}">
                        <div class="aarlo-modal-video-background"
                             id="${this._id('modal-video-background')}">
                        </div>
                        <video class="aarlo-modal-video"
                               id="${this._id('modal-video-player')}"
                               style="display:none" playsinline muted>
                            Your browser does not support the video tag.
                        </video>
                        <div class="box box-bottom"
                               id="${this._id('modal-video-controls')}">
                            <div>
                                <ha-icon id="${this._id('modal-video-door-lock')}"
                                         @click="${() => { this.toggleLock(this.cc.doorLockId); }}">
                                </ha-icon>
                                <ha-icon id="${this._id('modal-video-light-on')}"
                                         @click="${() => { this.toggleLight(this.cc.lightId); }}">
                                </ha-icon>
                                <ha-icon id="${this._id('modal-video-toggle-sound')}"
                                         @click="${() => { this.controlToggleSound(); }}">
                                </ha-icon>
                                <ha-icon id="${this._id('modal-video-stop')}"
                                         @click="${() => { this.controlStop(); }}">
                                </ha-icon>
                                <ha-icon id="${this._id('modal-video-play-pause')}"
                                         @click="${() => { this.controlPlayPause(); }}">
                                </ha-icon>
                            </div>
                            <div class='slidecontainer'>
                                <input class="slider"
                                       id="${this._id('modal-video-seek')}"
                                       type="range" value="0" min="1" max="100">
                            </div>
                            <div>
                                <ha-icon id="${this._id('modal-video-full-screen')}"
                                         @click="${() => { this.controlFullScreen(); }}">
                                </ha-icon>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <ha-card>
                <div class="aarlo-base aarlo-aspect-${this.gc.aspectRatio}"
                     id="${this._id('aarlo-wrapper')}">
                    <video class="aarlo-video"
                           id="${this._id('video-player')}"
                           style="display:none" playsinline muted>
                        Your browser does not support the video tag.
                    </video>
                    <img class="aarlo-image"
                         id="${this._id('camera-viewer')}"
                         style="display:none"
                         @click="${() => { this.imageClicked(); }}">
                    <div class="aarlo-image"
                         id="${this._id('library-viewer')}"
                         style="display:none">
                    </div>
                    <div class="aarlo-image aarlo-broken-image" 
                         id="${this._id('broken-image')}"
                         style="height: 100px">
                    </div>
                </div>
                <div class="box box-top"
                     id="${this._id('top-bar')}"
                     style="display:none">
                </div>
                <div class="box box-bottom"
                     id="${this._id('bottom-bar')}"
                     style="display:none">
                </div>
                <div class="box box-bottom"
                     id="${this._id('library-controls')}"
                     style="display:none">
                    <div>
                        <ha-icon id="${this._id('library-control-first')}"
                                 class="aarlo-icon-${this._sizeSuffix()}"
                                 @click="${() => { this.firstLibraryPage(); }}">
                        </ha-icon>
                        <ha-icon id="${this._id('library-control-previous')}"
                                 class="aarlo-icon-${this._sizeSuffix()}"
                                 @click="${() => { this.previousLibraryPage(); }}">
                        </ha-icon>
                    </div>
                    <div style="margin-left: auto; margin-right: auto">
                        <ha-icon id="${this._id('library-control-resize')}"
                                 class="aarlo-icon-${this._sizeSuffix()}"
                                 @click="${() => { this.resizeLibrary() }}">
                        </ha-icon>
                        <ha-icon id="${this._id('library-control-close')}"
                                 class="aarlo-icon-${this._sizeSuffix()}"
                                 @click="${() => { this.closeLibrary() }}">
                        </ha-icon>
                    </div>
                    <div>
                        <ha-icon id="${this._id('library-control-next')}"
                                 class="aarlo-icon-${this._sizeSuffix()}"
                                 @click="${() => { this.nextLibraryPage() }}">
                        </ha-icon>
                        <ha-icon id="${this._id('library-control-last')}"
                                 class="aarlo-icon-${this._sizeSuffix()}"
                                 @click="${() => { this.lastLibraryPage(); }}">
                        </ha-icon>
                    </div>
                </div>
                <div class="box box-bottom"
                     id="${this._id('video-controls')}"
                     style="display:none">
                    <div>
                        <ha-icon id="${this._id('video-door-lock')}"
                                 @click="${() => { this.toggleLock(this.cc.doorLockId); }}">
                        </ha-icon>
                        <ha-icon id="${this._id('video-light-on')}"
                                 @click="${() => { this.toggleLight(this.cc.lightId); }}">
                        </ha-icon>
                        <ha-icon id="${this._id('video-toggle-sound')}"
                                 @click="${() => { this.controlToggleSound(); }}">
                        </ha-icon>
                        <ha-icon id="${this._id('video-stop')}"
                                 @click="${() => { this.controlStop(); }}">
                        </ha-icon>
                        <ha-icon id="${this._id('video-play-pause')}"
                                 @click="${() => { this.controlPlayPause(); }}">
                        </ha-icon>
                    </div>
                    <div class='slidecontainer'>
                        <input class="slider"
                               id="${this._id('video-seek')}"
                               type="range" value="0" min="1" max="100">
                    </div>
                    <div>
                        <ha-icon 
                                 id="${this._id('video-full-screen')}"
                                 @click="${() => { this.controlFullScreen(); }}">
                        </ha-icon>
                    </div>
                </div>
            </ha-card>`
    }

    static get properties() {
        return {
            // All handle internally
        }
    }

    updated(_changedProperties) {
        // All handle internally
    }

    set hass( hass ) {
        this._hass = hass;
        if ( this._ready ) {
            this.updateView()
        }
    }

    getCardSize() {
        return this.gc.cardSize
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

    throwError( error ) {
        console.error( error );
        throw new Error( error )
    }

    _log( msg ) {
        if( this.gc.log ) {
            console.log( `${this.cc.id}: ${msg}` )
        }
    }

    _id( id ) {
        return `${id}-${this.gc.idSuffix}`
    }

    _mid( id ) {
        return (this.gs.viewer === "modal" ? "modal-" : "") + this._id(id)
    }

    /**
     * Look for card element in shadow dom.
     *
     * @param id The element or `null`
    */
    _element( id ) {
        return this.shadowRoot.getElementById( this._id(id) )
    }

    /**
     * Look for modal card element in shadow dom.
     *
     * Automatically chooses modal name if modal window open.
     *
     * @param id The element or `null`
    */
    _melement( id ) {
        return this.shadowRoot.getElementById( this._mid(id) )
    }

    __show( element, show ) {
        if ( element ) { element.style.display = show ? '' : 'none' }
    }
    _show( id, show = true ) {
        this.__show( this._element(id), show )
    }
    _mshow( id, show = true ) {
        this.__show( this._melement(id), show )
    }

    __hide( element ) {
        if ( element ) { element.style.display = 'none' }
    }
    _hide( id ) {
        this.__hide( this._element(id) )
    }
    _mhide( id ) {
        this.__hide( this._melement(id) )
    }

    __isHidden( element ) {
        return element && element.style.display === 'none'
    }
    _misHidden( id ) {
        return this.__isHidden( this._melement(id) )
    }

    __title( element, title ) {
        if ( element ) { element.title = title }
    }
    __text( element, text ) {
        if ( element ) { element.innerText = text }
    }
    __alt( element, alt ) {
        if ( element ) { element.alt = alt }
    }
    __src( element, src ) {
        if ( element ) { element.src = src }
    }
    __poster( element, poster ) {
        if ( element ) { element.poster = poster }
    }
    __icon( element, icon ) {
        if ( element ) { element.icon = icon }
    }
    __state( element, state ) {
        let color = ""
        switch( state ) {
            case "on":
            case "state-on":
                color = "white"
                break
            case "warn":
            case "state-warn":
                color = "orange"
                break
            case "error":
            case "state-error":
                color = "red"
                break
            case "update":
            case "state-update":
                color = "#cccccc"
                break
            case "off":
            case "state-off":
                color = "#505050"
                break
        }
        if ( element ) {
            element.style.color = color
        }
    }

    /**
     * Set a variety of element values.
     *
     * It gets called a lot.
     */
    __set( element, title, text, icon, state, src, alt, poster ) {
        if (_real(title))  { this.__title( element, title ) }
        if (_real(text))   { this.__text ( element, text ) }
        if (_real(icon))   { this.__icon ( element, icon ) }
        if (_real(state))  { this.__state( element, state ) }
        if (_real(src))    { this.__src( element, src ) }
        if (_real(alt))    { this.__alt( element, alt ) }
        if (_real(poster)) { this.__poster( element, poster ) }
    }

    /**
     * Set a variety pieces of element data.
     *
     * @param id - ID of element to change
     * @param dictionary - Object containing changes. Not all entries need to
     *     be set.
     */
    _set( id, { title, text, icon, state, src, alt, poster } = {} ) {
        this.__set( this._element(id), title, text, icon, state, src, alt, poster )
    }
    /**
     * Set a variety pieces of element data.
     *
     * This uses the modal version when a modal window is open.
     *
     * @param id - ID of element to change
     * @param dictionary - Object containing changes. Not all entries need to
     *     be set.
     */
    _mset( id, { title, text, icon, state, src, alt, poster } = {} ) {
        this.__set( this._melement(id), title, text, icon, state, src, alt, poster )
    }

    _widthHeight(id, width, height, width_suffix = '' ) {
        let element = this._element(id)
        if ( element ) {
            if ( width !== null ) {
                element.style.setProperty("width",`${width}px`,width_suffix)
            }
            if ( height !== null ) {
                element.style.height = `${height}px`
            }
        }
    }

    _sizeSuffix() {
        if( this.gc.small ) {
            return "small"
        }
        else if( this.gc.tiny ) {
            return "tiny"
        }
        return "medium"
    }

    _paddingTop( id, top ) {
        let element = this._element(id)
        if ( element ) {
            if ( top !== null ) {
                element.style.paddingTop=`${top}px`
            }
        }
    }

    _findEgressToken( url ) {
        let parser = document.createElement('a');
        parser.href = url;
        let queries = parser.search.replace(/^\?/, '').split('&');
        for( let i = 0; i < queries.length; i++ ) {
            const split = queries[i].split('=');
            if( split[0] === 'egressToken' ) {
                return split[1]
            }
        }
        return 'unknown'
    }

    get gc() {
        return this._gc
    }
    set gc( value ) {
        this._gc = value
    }
    get gs() {
        return this._gs
    }
    set gs( value ) {
        this._gs = value
    }
    get cc() {
        if( !(`${this._cameraIndex}` in this._cc) ) {
            this._cc[`${this._cameraIndex}`] = {}
        }
        return this._cc[`${this._cameraIndex}`]
    }
    set cc( value ) {
        this._cc[`${this._cameraIndex}`] = value
    }
    get cs() {
        if( !(`${this._cameraIndex}` in this._cs) ) {
            this._cs[`${this._cameraIndex}`] = {}
        }
        return this._cs[this._cameraIndex]
    }
    set cs( value ) {
        this._cs[this._cameraIndex] = value
    }
    get lc() {
        if( !(`${this._cameraIndex}` in this._lc) ) {
            this._lc[`${this._cameraIndex}`] = {}
        }
        return this._lc[this.gc.blendedMode ? this._cameraCount : this._cameraIndex]
    }
    set lc( value ) {
        this._lc[this._cameraIndex] = value
    }
    get ls() {
        if( !(`${this._cameraIndex}` in this._ls) ) {
            this._ls[`${this._cameraIndex}`] = {}
        }
        return this._ls[this.gc.blendedMode ? this._cameraCount : this._cameraIndex]
    }
    set ls( value ) {
        this._ls[this._cameraIndex] = value
    }

    /**
     * Find `what` in `section` of language pack.
     *
     * The code removes punctuation and replaces spaces with underscores
     * in `what`.
     * @param section - the section of `this._i` to look at
     * @param what - what to look for
     * @returns {*}
     * @private
     */
    _tr(section, what) {
        const new_what = what.replace(/[^\w\s]|_/g, "")
                .replace(/\s+/g, " ")
                .replace(/\s/g, "_")
                .toLowerCase()
        return new_what in this._i[section] ? this._i[section][new_what] : what
    }
    _getState(_id, default_value = '') {
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

    _updateStatuses() {

        // CAMERA
        const camera = this._getState(this.cc.id,'unknown');

        // Set the camera name now. We have to wait until now to ensure `_hass`
        // is set and we can get to the camera state.
        if ( this.cc.name === null ) {
            this.cc.name = camera.attributes.friendly_name
        }

        // Camera state has changed. Update the image URL so we update the
        // view. If we've moved from "taking snapshot" to anything else then
        // queue up some image update requests.
        if ( camera.state !== this.cs.state ) {
            this._log( `state-update: ${this.cs.state} --> ${camera.state}` )
            if( camera.state !== 'off' ) {
                this.generateImageURL()
            } else {
                this.cs.image = camera.attributes.last_thumbnail
            }
            if ( this.cs.state === 'taking snapshot' ) {
                this.cc.snapshotTimeouts.forEach( (seconds) => {
                    this.generateImageURLLater( seconds )
                })
            }
            this.gc.lastActive = this._cameraIndex
            this.cs.state = camera.state
            this.cs.details.status = { text: this._tr("state",this.cs.state) }
        }

        // Entity picture has changed. This means there is a new auth key
        // attached. Update the image URL so we update the view.
        if ( this.cs.imageBase !== camera.attributes.entity_picture ) {
            this._log( `auth-update: ${this.cs.imageBase} --> ${camera.attributes.entity_picture}` )
            this.generateImageURL()
        }

        // Image source has changed. This means it was from a new capture or
        // snapshot. Update the image URL so we update the view.
        if ( this.cs.imageSource !== camera.attributes.image_source ) {
            this._log( `source-update: ${this.cs.imageSource} --> ${camera.attributes.image_source}` )
            this.generateImageURL()
            this.gc.lastActive = this._cameraIndex
            this.cs.imageSource = camera.attributes.image_source
        }

        // Update status details.
        if( this.cs.image !== null ) {
            let date = ""
            let full_date = this.cs.imageSource ? this.cs.imageSource : ''
            if( full_date.startsWith('capture/') ) { 
                date      = full_date.substr(8);
                full_date = `${this._i.image.automatic_capture} ${date}`
            } else if( full_date.startsWith('snapshot/') ) { 
                date      = full_date.substr(9);
                full_date = `${this._i.image.snapshot_capture} ${date}`
            }
            this.cs.details.viewer = {title: full_date, alt: full_date, src: this.cs.image}
            this.cs.details.date = {title: full_date, text: date}
        } else {
            this.cs.details.viewer = {title: "", alt: "", src: null}
            this.cs.details.date = {title: "", text: ""}
        }

        // LIBRARY
        // Check for video update. We can go from:
        // - having no recordings to having one or more
        // - having one or more recordings to none
        // - having new recordings
        if( "last_video" in camera.attributes ) {
            if( this.cs.lastRecording !== camera.attributes.last_video ) {
                this._log( `video-changed: updating library` )
                this.asyncLoadLibrary( this._cameraIndex ).then( () => {
                    this.mergeLibraries()
                    this._updateLibraryView()
                })
                this.cs.lastRecording = camera.attributes.last_video
            }
        } else {
            if( this.cs.lastRecording !== null ) {
                this._log( `no-videos: clearing library` )
                this.ls.recordings    = []
                this.cs.lastRecording = null
            }
        }

        // IMAGE 
        // FUNCTIONS
        if (this.cs.state === 'off') {
            this.cs.details.stream = _tsi(this._i.image.feature_disabled, 'off', 'mdi:play')
        } else if(this.cs.state !== 'streaming') {
            this.cs.details.stream = _tsi(this._i.image.start_stream, 'on', 'mdi:play')
        } else {
            this.cs.details.stream = _tsi(this._i.image.stop_stream, 'on', 'mdi:stop')
        }

        if ( this.cs.state === 'off' ) {
            this.cs.details.onoff = _tsi(this._i.image.turn_camera_on, 'state-on', 'mdi:camera')
        } else {
            this.cs.details.onoff = _tsi(this._i.image.turn_camera_off, '', 'mdi:camera-off')
        }

        if(this.cs.state !== 'off') {
            this.cs.details.snapshot = _tsi(this._i.image.take_a_snapshot, '', 'mdi:camera-enhance')
        } else {
            this.cs.details.snapshot = _tsi(this._i.image.feature_disabled, 'off', 'mdi:camera-off')
        }

        // SENSORS
        if ( camera.attributes.wired_only ) {
            this.cs.details.battery = _tsi( this._i.status.plugged_in, 'state-update', 'mdi:power-plug')
        } else {
            const battery = this._getState(this.cc.batteryId, 0);
            const prefix = camera.attributes.charging ? 'battery-charging' : 'battery';
            this.cs.details.battery = _tsi(
                `${this._i.status.battery_strength}: ${battery.state}%`,
                battery.state < 25 ? 'state-warn' : ( battery.state < 15 ? 'state-error' : 'state-update' ),
                `mdi:${prefix}` + (battery.state < 10 ? '-outline' :
                            (battery.state > 90 ? '' : '-' + Math.round(battery.state/10) + '0' ))
            )
        }

        const signal = this._getState(this.cc.signalId, 0);
        this.cs.details.signal = _tsi(
            `${this._i.status.signal_strength}: ${signal.state}`,
            '',
            signal.state === "0" ? 'mdi:wifi-outline' : `mdi:wifi-strength-${signal.state}`
        )

        if ( this.cs.state !== 'off' ) {
            const has_motion = this._getState(this.cc.motionId,'off').state === 'on'
            this.cs.details.motion = _tsi(
                `${this._i.status.motion}: ${has_motion ? this._i.status.detected : this._i.status.clear}`,
                has_motion ? 'on' : '',
                has_motion ? "mdi:run" : "mdi:walk",
            )
        } else {
            this.cs.details.motion = _tsi(this._i.image.feature_disabled, 'off', "mdi:walk")
        }

        if ( this.cs.state !== 'off' ) {
            const has_sound = this._getState(this.cc.soundId,'off').state === 'on'
            this.cs.details.sound = _tsi(
                `${this._i.status.sound}: ${has_sound ? this._i.status.detected : this._i.status.clear}`,
                has_sound ? 'state-on' : '',
                "mdi:ear-hearing"
            )
        } else {
            this.cs.details.sound = _tsi(this._i.image.feature_disabled, 'off', "mdi:ear-hearing-off")
        }

        // We always save this, used by library code to check for updates
        const captured = this._getState(this.cc.capturedTodayId, "0").state;
        const last = this._getState(this.cc.lastCaptureId, "0").state;
        if( this.ls.recordings && this.ls.recordings.length > 0 ) {
            this.cs.details.library = _tsi(
                `${this._i.status.library}: ` +
                        ( captured === "0" ? "" : `${captured} ${this._i.status.captured_something} ${last}, ` ) +
                        this._i.status.library_open,
                captured !== "0" ? 'on' : '',
                this.cc.numericView ? 'mdi:numeric-' + (captured > 9 ? "9-plus" : captured) + '-box' : 'mdi:file-video'
            )
        } else {
            this.cs.details.library = _tsi(
                `${this._i.status.library}: ${this._i.status.library_empty}`,
                'off',
                this.cc.numericView ? 'mdi:numeric-0-box' : 'mdi:file-video-outline'
            )
        }

        // OPTIONAL DOORS
        if(this.cc.doorId) {
            const doorState = this._getState(this.cc.doorId, 'off')
            const is_open   = doorState.state === 'on'
            this.cs.details.door = _tsi(
                `${doorState.attributes.friendly_name}: ${is_open ? this._i.status.door_open : this._i.status.door_closed}`,
                is_open ? 'on' : '',
                is_open ? 'mdi:door-open' : 'mdi:door',
            )
        }
        if(this.cc.door2Id) {
            const doorState = this._getState(this.cc.door2Id, 'off')
            const is_open   = doorState.state === 'on'
            this.cs.details.door2 = _tsi(
                `${doorState.attributes.friendly_name}: ${is_open ? this._i.status.door2_open : this._i.status.door2_closed}`,
                is_open ? 'on' : '',
                is_open ? 'mdi:door-open' : 'mdi:door',
            )
        }

        if(this.cc.doorLockId) {
            const doorLockState = this._getState(this.cc.doorLockId, 'locked');
            const is_locked     = doorLockState.state === 'locked'
            this.cs.details.lock = _tsi(
                `${doorLockState.attributes.friendly_name}: ${is_locked ? this._i.status.lock_locked : this._i.status.lock_unlocked}`,
                is_locked ? 'state-on' : 'state-warn',
                is_locked ? 'mdi:lock' : 'mdi:lock-open',
            )
        }
        if(this.cc.door2LockId) {
            const door2LockState = this._getState(this.cc.door2LockId, 'locked')
            const is_locked      = doorLockState.state === 'locked'
            this.cs.details.lock2 = _tsi(
                `${door2LockState.attributes.friendly_name}: ${is_locked ? this._i.status.lock_locked : this._i.status.lock_unlocked}`,
                is_locked ? 'state-on' : 'state-warn',
                is_locked ? 'mdi:lock' : 'mdi:lock-open',
            )
        }

        if(this.cc.doorBellId) {
            const bell = this._getState(this.cc.doorBellId, 'off');
            const name = bell.attributes.friendly_name
            const mute = bell.attributes.chimes_silenced || bell.attributes.calls_silenced
            const muteable = !!this.cc.doorBellMuteId
            if ( bell.state === 'on' ) {
                this.cs.details.bell = _tsi(`${name}: ${this._i.status.doorbell_pressed}`, 'on', 'mdi:bell-ring')
            } else if( muteable ) {
                if ( mute ) {
                    this.cs.details.bell = _tsi(`${name}: ${this._i.status.doorbell_muted}`, 'warn', 'mdi:bell-off')
                } else {
                    this.cs.details.bell = _tsi(`${name}: ${this._i.status.doorbell_mute}`, '', 'mdi:bell')
                }
            } else {
                this.cs.details.bell = _tsi(`${name}: ${this._i.status.doorbell_idle}`, '', 'mdi:bell')
            }
        }

        if(this.cc.door2BellId) {
            const bell = this._getState(this.cc.door2BellId, 'off');
            const name = bell.attributes.friendly_name
            const mute = bell.attributes.chimes_silenced || bell.attributes.calls_silenced
            const muteable = !!this.cc.door2BellMuteId
            if ( bell.state === 'on' ) {
                this.cs.details.bell2 = _tsi(`${name}: ${this._i.status.doorbell_pressed}`, 'on', 'mdi:bell-ring')
            } else if( muteable ) {
                if ( mute ) {
                    this.cs.details.bell2 = _tsi(`${name}: ${this._i.status.doorbell_muted}`, 'warn', 'mdi:bell-off')
                } else {
                    this.cs.details.bell2 = _tsi(`${name}: ${this._i.status.doorbell_mute}`, '', 'mdi:bell')
                }
            } else {
                this.cs.details.bell = _tsi(`${name}: ${this._i.status.doorbell_idle}`, '', 'mdi:bell')
            }
        }

        if(this.cc.lightId) {
            const lightState = this._getState(this.cc.lightId, 'off');
            const is_on = lightState.state === 'on'
            this.cs.details.light = _tsi(
                `${lightState.attributes.friendly_name}: ` + (is_on ?  this._i.status.light_on : this._i.status.light_off),
                is_on ? 'on' : '',
                'mdi:lightbulb'
            )
        }
        if(this.cc.light2Id) {
            const lightState = this._getState(this.cc.light2Id, 'off');
            const is_on = lightState.state === 'on'
            this.cs.details.light2 = _tsi(
                `${lightState.attributes.friendly_name}: ` + (is_on ?  this._i.status.light_on : this._i.status.light_off),
                is_on ? 'on' : '',
                'mdi:lightbulb'
            )
        }
    }

    updateStatuses() {

        this.gc.lastActive = -1
        const index = this._cameraIndex
        for( this._cameraIndex = 0; this._cameraIndex < this._cameraCount; this._cameraIndex++ ) {
            this._updateStatuses()
        }
        this._cameraIndex = index

        if( this.gc.activeView ) {
            if( this.gc.lastActive !== -1 && this.gc.lastActive !== index ) {
                this.setCameraImage( this.gc.lastActive )
            }
        }
    }

    checkConfig() {

        if ( this._hass === null ) {
            return;
        }

        if ( !(this.cc.id in this._hass.states) ) {
            this.throwError( 'unknown camera' );
        }
        if ( this.cc.doorId && !(this.cc.doorId in this._hass.states) ) {
            this.throwError( 'unknown door' )
        }
        if ( this.cc.doorBellId && !(this.cc.doorBellId in this._hass.states) ) {
            this.throwError( 'unknown door bell' )
        }
        if ( this.cc.doorLockId && !(this.cc.doorLockId in this._hass.states) ) {
            this.throwError( 'unknown door lock' )
        }
        if ( this.cc.door2Id && !(this.cc.door2Id in this._hass.states) ) {
            this.throwError( 'unknown door (#2)' )
        }
        if ( this.cc.door2BellId && !(this.cc.door2BellId in this._hass.states) ) {
            this.throwError( 'unknown door bell (#2)' )
        }
        if ( this.cc.door2LockId && !(this.cc.door2LockId in this._hass.states) ) {
            this.throwError( 'unknown door lock (#2)' )
        }
    }

    getGlobalConfig( config ) {

        return {
            // GLOBAL config
            // Mobile? see here: https://developer.mozilla.org/en-US/docs/Web/HTTP/Browser_detection_using_the_user_agent
            isMobile: navigator.userAgent.includes("Mobi"),
            // HA App
            isHAApp: navigator.userAgent.includes("HomeAssistant"),

            // Language override?
            lang: config.lang,

            // active camera mode
            activeView: (_includes( config.global, "active" ) ||
                        _includes( config.image_view, "active" )),

            // initial state is muted
            isMuted: _includes( config.global, "muted" ),

            // aspect ratio
            aspectRatio: (_includes(config.global, 'square') ||
                        _includes(config.image_view, 'square')) ? '1x1' : '16x9',
            aspectRatioMultiplier: (_includes(config.global, 'square') ||
                        _includes(config.image_view, 'square')) ? 1 : 0.5625,

            // size
            small: _includes(config.global,'small'),
            tiny: _includes(config.global,'tiny'),

            // blended library
            blendedMode: _includes(config.global, 'blended') ||
                        _includes( config.library_view, "blended" ),

            // modal window multiplier
            modalMultiplier: _value_float( config.modal_multiplier, 0.8 ),

            // lovelace card size
            cardSize: _value_int( config.card_size, 3 ),

            // swipe threshold
            swipeThreshold: _value_int( config.swipe_threshold, 150 ),

            // logging?
            log: _value( config.logging, false ),
        }
    }

    getGlobalState( _config ) {
        return {
            dash: null,
            hls: null,
            libraryCamera: -1,
            isMuted: this.gc.isMuted,
            poster: '',
            recording: null,
            stream: null,
        }
    }

    convertOldLayout(config,cc) {
        if( config.image_top || config.image_bottom ) {
            return
        }

        const items = ["on_off","motion","sound","library","captured","captured_today",
                        "play","snapshot","battery","battery_level","signal_strength"]

        let image_top = []
        _pushIf(image_top, "name", config.top_title)
        _pushIf(image_top, "date", config.top_date)
        _pushIf(image_top, "status", config.top_status)

        let image_bottom = []
        let image_bottom_left = []
        items.forEach( (item) => {
            _pushIf(image_bottom_left, item, config.show.includes(item))
        })
        _pushIf(image_bottom, image_bottom_left.join(","), image_bottom_left)

        let image_bottom_right = []
        _pushIf(image_bottom_right, "door", cc.doorId)
        _pushIf(image_bottom_right, "bell", cc.doorBellId)
        _pushIf(image_bottom_right, "lock", cc.doorLockId)
        _pushIf(image_bottom_right, "door2", cc.door2Id)
        _pushIf(image_bottom_right, "bell2", cc.door2BellId)
        _pushIf(image_bottom_right, "lock2", cc.door2LockId)
        _pushIf(image_bottom_right, "light", cc.lightId)
        _pushIf(image_bottom_right, "next", this._config.entities)
        _pushIf(image_bottom, image_bottom_right.join(","), image_bottom_right)
        
        image_bottom = _replaceAll(image_bottom.join("|"), "on_off", "onoff")
        image_bottom = _replaceAll(image_bottom, "battery_level", "battery")
        image_bottom = _replaceAll(image_bottom, "captured_today", "library")
        image_bottom = _replaceAll(image_bottom, "captured", "library")
        image_bottom = _replaceAll(image_bottom, "signal_strength", "signal")

        config.image_top = image_top.join("|")
        config.image_bottom = image_bottom
    }

    getCameraConfigOld( global, local ) {
        const config = _mergeArrays( global, local )

        // find camera
        let camera = ""
        if( config.entity ) {
            camera = config.entity.replace( 'camera.','' );
        }
        if( config.camera ) {
            camera = config.camera
        }
        if( camera === "" ) {
            this.throwError( 'missing a camera definition' )
            return
        }
        if( !config.show ) {
            this.throwError( 'missing show components' );
            return
        }

        // see if aarlo prefix, remove from custom names if not present
        let prefix = "";
        if ( camera.startsWith( 'aarlo_' ) ) {
            camera = camera.replace( 'aarlo_','' )
            prefix = "aarlo_"
        }
        if( config.prefix ) {
            prefix = config.prefix;
        }

        let cc = {}

        // Grab name if there
        cc.name = config.name ? config.name : null

        // What happens when we click on image
        const image_click = config.image_click ? config.image_click : ""
        cc.directPlay    = image_click.includes("direct") || _value( config.play_direct, false )
        cc.modalPlayer   = image_click.includes("modal")
        cc.smartPlayer   = image_click.includes("smart")
        cc.autoPlay      = image_click.includes("autoplay") || _value( config.auto_play, false )

        cc.playStream    = image_click.includes("live") ||
                    image_click.includes("play") ||
                    image_click.includes("stream")

        // snapshot updates
        cc.snapshotTimeouts = config.snapshot_retry ? config.snapshot_retry : [ 2, 5 ]

        // stream directly from Arlo
        cc.playDirectFromArlo = config.play_direct ? config.play_direct : false;

        // camera and sensors
        cc.id              = config.camera_id ? config.camera_id : 'camera.' + prefix + camera;
        cc.motionId        = config.motion_id ? config.motion_id : 'binary_sensor.' + prefix + 'motion_' + camera;
        cc.soundId         = config.sound_id ? config.sound_id : 'binary_sensor.' + prefix + 'sound_' + camera;
        cc.batteryId       = config.battery_id ? config.battery_id : 'sensor.' + prefix + 'battery_level_' + camera;
        cc.signalId        = config.signal_id ? config.signal_id : 'sensor.' + prefix + 'signal_strength_' + camera;
        cc.capturedTodayId = config.capture_id ? config.capture_id : 'sensor.' + prefix + 'captured_today_' + camera;
        cc.lastCaptureId   = config.last_id ? config.last_id : 'sensor.' + prefix + 'last_' + camera;

        // door definition
        cc.doorId         = config.door ? config.door: null;
        cc.doorBellId     = config.door_bell ? config.door_bell : null;
        cc.doorBellMuteId = config.door_bell_mute ? config.door_bell_mute : null;
        cc.doorLockId     = config.door_lock ? config.door_lock : null;

        // door2 definition
        cc.door2Id         = config.door2 ? config.door2: null;
        cc.door2BellId     = config.door2_bell ? config.door2_bell : null;
        cc.door2BellMuteId = config.door2_bell_mute ? config.door2_bell_mute : null;
        cc.door2LockId     = config.door2_lock ? config.door2_lock : null;

        // light definition
        cc.lightId     = config.light ? config.light: null;

        this.convertOldLayout(config,cc)
        cc.image_top = config.image_top
        cc.image_bottom = config.image_bottom

        return cc
    }

    getCameraConfigNew( global, local ) {
        const config = _mergeArrays( global, local )

        // Find entity and determine camera name.
        const entity = config.entity
        if ( !entity.startsWith( 'camera.aarlo_' ) ) {
            this.throwError( "new config only works with aarlo entity names" )
            return
        }
        const camera = entity.replace( 'camera.aarlo_','' )

        let cc = {}

        // Grab name if there
        cc.name = _value( config.name, null )

        // Save layout
        cc.image_top = config.image_top
        cc.image_bottom = config.image_bottom

        // How do we display recordings or stream?
        cc.directPlay        = _includes(config.image_view, "direct")
        cc.modalPlayer       = _includes(config.image_view, "modal")
        cc.numericView       = _includes(config.image_view, 'numeric')
        cc.smartPlayer       = _includes(config.image_view, "smart")
        cc.autoPlay          = _includes(config.image_view, 'start-stream')
        cc.autoPlayRecording = _includes(config.image_view, 'start-recording')

        // Does clicking show the live stream or last recording?
        cc.playStream = _includes( config.image_click, "stream")

        // snapshot updates
        cc.snapshotTimeouts = _array( config.snapshot_retry, [ 2, 5 ] )

        // camera and sensors
        cc.id              = _value(config.camera_id,  `camera.aarlo_${camera}`)
        cc.motionId        = _value(config.motion_id,  `binary_sensor.aarlo_motion_${camera}`)
        cc.soundId         = _value(config.sound_id,   `binary_sensor.aarlo_sound_${camera}`)
        cc.batteryId       = _value(config.battery_id, `sensor.aarlo_battery_level_${camera}`)
        cc.signalId        = _value(config.signal_id,  `sensor.aarlo_signal_strength_${camera}`)
        cc.capturedTodayId = _value(config.capture_id, `sensor.aarlo_captured_today_${camera}`)
        cc.lastCaptureId   = _value(config.last_id,    `sensor.aarlo_last_${camera}`)

        // door definition
        cc.doorId         = _value(config.door)
        cc.doorBellId     = _value(config.door_bell)
        cc.doorBellMuteId = _value(config.door_bell_mute)
        cc.doorLockId     = _value(config.door_lock)

        // door2 definition
        cc.door2Id         = _value(config.door2)
        cc.door2BellId     = _value(config.door2_bell)
        cc.door2BellMuteId = _value(config.door2_bell_mute)
        cc.door2LockId     = _value(config.door2_lock)

        // light definitions
        cc.lightId  = _value(config.light)
        cc.light2Id = _value(config.light2)

        return cc
    }

    getCameraConfig( global, local ) {
        if( "show" in global ) {
            return this.getCameraConfigOld( global, local )
        } else {
            return this.getCameraConfigNew( global, local )
        }
    }

    getCameraState( config ) {
        return {
            autoPlay:      config.autoPlay,
            autoPlayTimer: null,
            details:       {},
            lastRecording: null,
            image:         null,
            imageBase:     null,
        }
    }

    getLibraryConfig( global, local ) {

        const config = _mergeArrays( global, local )
        const sizes = _array( config.library_sizes, [ 3 ] )

        return {
            // What to when video clicked
            download:          _includes(config.library_view, "download"),
            duration:          _includes(config.library_view, "duration"),
            modalPlayer:       _includes(config.library_view, "modal"),
            smartPlayer:       _includes(config.library_view, "smart"),
            autoPlayRecording: _includes(config.library_view, 'start-recording'),

            // How many recordings to show
            sizes:      sizes,
            recordings: _value_int( config.max_recordings, 99 ),

            // Highlight motion triggers?
            regions: _array( config.library_regions, sizes ),
            colors:  {
                "Animal":  _value( config.library_animal, 'orangered' ),
                "Vehicle": _value( config.library_vehicle, 'yellow' ),
                "Person":  _value( config.library_person, 'lime' ),
                "Package":  _value( config.library_package, 'cyan' ),
            },
        }
    }

    getLibraryState( _config ) {
        return {
            gridCount:  -1,
            lastOffset: -1,
            offset:     0,
            recordings: null,
            size:       -1,
            sizeIndex:  0,

        }
    }

    setConfig(config) {

        // save then check new config
        // this._config = _mergeArrays(config, {})
        this._config = config

        this.gc = this.getGlobalConfig( config )
        this.gs = this.getGlobalState( config )

        if( "entities" in this._config ) {
            let ci = 0
            this._config.entities.forEach( (local_config) => {
                this._cc[ci] = this.getCameraConfig( config, local_config )
                this._cs[ci] = this.getCameraState( this._cc[ci] )
                this._lc[ci] = this.getLibraryConfig( config, local_config )
                this._ls[ci] = this.getLibraryState( this._lc[ci] )
                ci++
            })

            // For blended we fake a library at the end.
            if( this.gc.blendedMode ) {
                this._lc[ci] = this.getLibraryConfig( config, {} )
                this._ls[ci] = this.getLibraryState( this._lc[ci] )
            }

            // Use the first camera.
            this._cameraCount = ci
            this._cameraIndex = 0

        } else {
            // Single camera. Much simpler.
            this._cc[0] = this.getCameraConfig( config, {} )
            this._cs[0] = this.getCameraState( this._cc[0] )
            this._lc[0] = this.getLibraryConfig( config, {} )
            this._ls[0] = this.getLibraryState( this._lc[0] )

            // Use the first camera.
            this._cameraCount = 1
            this._cameraIndex = 0
        }
 
        //this.checkConfig()

        // web item id suffix
        this.gc.idSuffix = _replaceAll( this.cc.id,'.','-' )
        this.gc.idSuffix = _replaceAll( this.gc.idSuffix,'_','-' )
    }

    getModalDimensions() {
        let width  = window.innerWidth * this.gc.modalMultiplier
        let height = window.innerHeight * this.gc.modalMultiplier
        const ratio = this.gc.aspectRatioMultiplier
        if( height / width > ratio ) {
            height = width * ratio
        } else if( height / width < ratio ) {
            width = height * (1/ratio)
        }
        this.cs.modalWidth = Math.round(width)
        this.cs.modalHeight = Math.round(height)

        let topOffset = window.pageYOffset
        if( topOffset !== 0 ) {
            this.cs.modalTop = Math.round( topOffset + ( (window.innerHeight - height) / 2 ) )
        } else {
            this.cs.modalTop = null
        }
    }

    repositionModal() {
        this.getModalDimensions()
        this._paddingTop( "modal-viewer", this.cs.modalTop )
    }

    setModalElementData() {
        this.getModalDimensions()
        this._paddingTop( "modal-viewer", this.cs.modalTop )
        this._widthHeight("modal-content", this.cs.modalWidth - 16, null, "important")
        this._widthHeight("modal-video-wrapper", this.cs.modalWidth, this.cs.modalHeight - 16)
        this._widthHeight("modal-video-background", this.cs.modalWidth, this.cs.modalHeight)
        this._widthHeight("modal-video-player", this.cs.modalWidth, this.cs.modalHeight)
    }

    showModal( show = true ) {
        if( this.gs.viewer === "modal" ) {
            this.setModalElementData()
            this._element('modal-viewer').style.display =  show ? 'block' : 'none'
        }
    }

    hideModal() {
        this._element('modal-viewer').style.display = 'none'
    }

    imageIconClicked(evt) {
        const id = evt.target.id
        const modified = evt.ctrlKey || evt.shiftKey

        if(id.startsWith("camera-motion")) {
            this.moreInfo(this.cc.motionId)
        } else if(id.startsWith("camera-sound")) {
            this.moreInfo(this.cc.soundId)
        } else if(id.startsWith("camera-battery")) {
            this.moreInfo(this.cc.batteryId)
        } else if(id.startsWith("camera-signal")) {
            this.moreInfo(this.cc.signalId)

        } else if(id.startsWith("camera-onoff")) {
            this.toggleCamera()
        } else if(id.startsWith("camera-library")) {
            this.openLibrary()
        } else if(id.startsWith("camera-stream")) {
            this.showOrStopStream()
        } else if(id.startsWith("camera-snapshot")) {
            this.updateSnapshot()

        } else if(id.startsWith("camera-door2")) {
            this.moreInfo(this.cc.door2Id)
        } else if(id.startsWith("camera-lock2")) {
            if(modified) {
                this.moreInfo(this.cc.door2LockId)
            } else {
                this.toggleLock(this.cc.door2LockId)
            }
        } else if(id.startsWith("camera-bell2")) {
            if (!this.cc.door2BellMuteId || modified) {
                this.moreInfo(this.cc.door2BellId)
            } else {
                this.toggleSwitch(this.cc.door2BellMuteId)
            }
        } else if(id.startsWith("camera-door")) {
            this.moreInfo(this.cc.doorId)
        } else if(id.startsWith("camera-lock")) {
            if(modified) {
                this.moreInfo(this.cc.doorLockId)
            } else {
                this.toggleLock(this.cc.doorLockId)
            }
        } else if(id.startsWith("camera-bell")) {
            if (!this.cc.doorBellMuteId || modified) {
                this.moreInfo(this.cc.doorBellId)
            } else {
                this.toggleSwitch(this.cc.doorBellMuteId)
            }
        } else if(id.startsWith("camera-light2")) {
            if(modified) {
                this.moreInfo(this.cc.light2Id)
            } else {
                this.toggleLight(this.cc.light2Id)
            }
        } else if(id.startsWith("camera-light")) {
            if(modified) {
                this.moreInfo(this.cc.lightId)
            } else {
                this.toggleLight(this.cc.lightId)
            }

        } else if(id.startsWith("camera-previous")) {
            this.previousCameraImage()
        } else if(id.startsWith("camera-next")) {
            this.nextCameraImage()
        } else {
            this._log("something clicked")
        }
    }

    buildImageRow(element, sections) {
        let text_items = ["name","date","status"]
        element.innerHTML = ''
        _array(sections).forEach((section,index,array) => {
            let div = document.createElement("div")
            _array(section).forEach((item) => {
                let elem
                if(item === '' ){
                    elem = document.createElement("span")
                    elem.innerHTML = "&nbsp"
                } else if(text_items.includes(item)) {
                    elem = document.createElement("span")
                    elem.classList.add(`camera-${item}`)
                    elem.classList.add(`aarlo-text-${this._sizeSuffix()}`)
                } else {
                    elem = document.createElement("ha-icon")
                    elem.classList.add(`aarlo-icon-${this._sizeSuffix()}`)
                    elem.addEventListener('click', (evt) => {
                        this.imageIconClicked(evt)
                    })
                }
                elem.id = this._id(`camera-${item}`)
                div.appendChild(elem)
            })

            // Set div alignment
            if( index === 0 ) {
                div.classList.add(`box-align-left`)
            } else if(index === array.length - 1) {
                div.classList.add(`box-align-right`)
            }
            element.appendChild(div)
        })
    }

    buildImageLayout(config) {
        if( config.image_top ) {
            this.buildImageRow(this._element('top-bar'), config.image_top)
        }
        if( config.image_bottom ) {
            this.buildImageRow(this._element('bottom-bar'), config.image_bottom)
        }
    }

    setupImageView() {
        this.buildImageLayout(this.cc)
        this._set("camera-name", {text: this.cc.name})
        if( this.gc.isMobile ) {
            this._hide("camera-previous")
            this._hide("camera-next")
        } else {
            this._set("camera-previous", {title: this._i.status.previous_camera, icon: "mdi:chevron-left", state: "on"})
            this._set("camera-next", {title: this._i.status.next_camera, icon: "mdi:chevron-right", state: "on"})
        }
    }

    setupImageHandlers() {

        const viewer = this._element("camera-viewer")

        viewer.addEventListener('error', () => {
            this.imageFailed();
        })

        if( this.gc.isMobile ) {
            viewer.addEventListener('touchstart', (e) => {
                this.ls.xDown = e.touches[0].clientX
                this.ls.xUp = null
            }, { passive: true })

            viewer.addEventListener('touchmove', (e) => {
                this.ls.xUp = e.touches[0].clientX
            }, { passive: true })

            viewer.addEventListener('touchend', () => {
                if( this.ls.xDown && this.ls.xUp ) {
                    const xDiff = this.ls.xDown - this.ls.xUp;
                    if( xDiff > this.gc.swipeThreshold ) {
                        this.nextCameraImage()
                    } else if( xDiff < (0 - this.gc.swipeThreshold) ) {
                        this.previousCameraImage()
                    }
                }
            }, { passive: true })
        }
    }

    updateImageView() {

        // Set up entries.
        for(const item in this.cs.details) {
            // noinspection JSUnfilteredForInLoop
            this._set(`camera-${item}`, this.cs.details[item] )
        }

    }

    /**
     * Generate a new image URL.
     *
     * This is done when Arlo changes the image or Home Assistance changes
     * the authentication token. We always add the current time to the end to
     * force the browser to reload.
     *
     * It makes no attempt to reload the image.
     */
    generateImageURL() {
        const camera = this._getState(this.cc.id,'unknown');
        this.cs.image = camera.attributes.entity_picture + "&t=" + new Date().getTime()
        this.cs.imageBase = camera.attributes.entity_picture
    }

    generateImageURLLater(seconds = 2) {
        setTimeout(() => {
            this.generateImageURL()
            this.updateImageView()
        }, seconds * 1000);
    }

    showImageView() {
        if( this.cs.image !== null ) {
            this._show("camera-viewer")
            this._hide("broken-image")
        } else {
            this._show("broken-image")
            this._hide("camera-viewer")
        }
        this._show('top-bar', !!this.cc.image_top)
        this._show('bottom-bar', !!this.cc.image_bottom)
        this.hideRecordingView()
        this.hideStreamView()
        this.hideLibraryView()
        this.hideModal()
    }

    hideImageView() {
        this._hide("camera-viewer")
        this._hide("broken-image")
        this._hide('top-bar')
        this._hide('bottom-bar')
    }

    setupLibraryView() {
        this._show("library-control-first" )
        this._show("library-control-previous" )
        this._show("library-control-next" )
        this._show("library-control-last" )
        this._show('library-control-resize',this.lc.sizes.length > 1 )
        this._set("library-control-resize",{ state: "on"} )
        this._set("library-control-close",{ state: "on"} )
    }

    setupLibraryHandlers() {
        // rudimentary swipe support
        const viewer = this._element("library-viewer")

        if( this.gc.isMobile ) {
            viewer.addEventListener('touchstart', (e) => {
                this.ls.xDown = e.touches[0].clientX
                this.ls.xUp = null
            }, { passive: true })

            viewer.addEventListener('touchmove', (e) => {
                this.ls.xUp = e.touches[0].clientX
            }, { passive: true })

            viewer.addEventListener('touchend', () => {
                if( this.ls.xDown && this.ls.xUp ) {
                    const xDiff = this.ls.xDown - this.ls.xUp;
                    if( xDiff > this.gc.swipeThreshold ) {
                        this.nextLibraryPage()
                    } else if( xDiff < (0 - this.gc.swipeThreshold) ) {
                        this.previousLibraryPage()
                    }
                }
            }, { passive: true })
        }
    }

    _updateLibraryHTML() {

        // update library state to reflect the new layout
        this.gs.librarySize = this.lc.sizes[this.ls.sizeIndex]
        this.ls.gridCount = this.gs.librarySize * this.gs.librarySize

        let grid = document.createElement("div")
        grid.style.display = "grid"
        grid.style['grid-template-columns'] = `repeat(${this.gs.librarySize},1fr)`
        grid.style['grid-template-rows'] = `repeat(${this.gs.librarySize},1fr)`
        grid.style['grid-gap'] = '1px'
        grid.style.padding= '2px'

        for( let i = 0; i < this.gs.librarySize * this.gs.librarySize; ++i ) {

            // The thumbnail element.
            let img = document.createElement("img")
            img.id = this._id(`library-${i}`)
            img.style.width = "100%"
            img.style.height = "100%"
            img.style.objectFit = "cover"
            img.addEventListener("click", () => { this.playRecording(i) } )
            img.addEventListener("mouseover", () => { this.showDownloadIcon(i) } )
            img.addEventListener("mouseout", () => { this.hideDownloadIcon(i) } )

            // The region highlight element
            let box = document.createElement("div")
            box.id = this._id(`library-box-${i}`)
            box.style.width = "100%"
            box.style.height = "100%"
            box.style.position = "absolute"
            box.style.top = "0"
            box.addEventListener("click", () => { this.playRecording(i) } )
            box.addEventListener("mouseover", () => { this.showDownloadIcon(i) } )
            box.addEventListener("mouseout", () => { this.hideDownloadIcon(i) } )

            // The download icon
            let a = document.createElement("a")
            a.id = this._id(`library-a-${i}`)
            a.style.position = "absolute"
            a.style.left = `2%`
            a.style.top  = `5%`
            a.setAttribute("download","")
            a.innerHTML = `<ha-icon class="aarlo-icon-small" icon="mdi:download" style="color: white;"></ha-icon>`

            const column = Math.floor((i % this.gs.librarySize) + 1)
            const row = Math.floor((i / this.gs.librarySize) + 1)
            let div = document.createElement("div")
            div.style.position= 'relative'
            div.style.gridColumn = `${column}`
            div.style.gridRow    = `${row}`
            div.appendChild(img)
            div.appendChild(box)
            div.appendChild(a)
            grid.appendChild(div)
        }

        // replace.
        let container = this._element('library-viewer')
        container.innerHTML = ''
        container.appendChild(grid)
    }

    _updateLibraryView() {
   
        // Massage offset so it fits in library.
        if( this.ls.offset + this.ls.gridCount > this.ls.recordings.length ) {
            this.ls.offset = Math.max(this.ls.recordings.length - this.ls.gridCount, 0)
        } else if( this.ls.offset < 0 ) {
            this.ls.offset = 0
        }

        let i = 0;
        let j= this.ls.offset;
        const show_triggers = this.lc.regions.includes(this.gs.librarySize)
        const last = Math.min(j + this.ls.gridCount, this.ls.recordings.length)
        for( ; j < last; i++, j++ ) {
            const id = `library-${i}`
            const bid = `library-box-${i}`
            const video = this.ls.recordings[j]
            let captured_text = `${this._i.library.captured}: ${video.created_at_pretty}`
            if( this.lc.duration ) {
                const minutes = Math.floor(video.duration / 60)
                const seconds = video.duration % 60
                captured_text += `\n${this._i.library.duration}: ${minutes}:${seconds.toString().padStart(2,'0')}`
            }
            if ( video.trigger && video.trigger !== '' ) {
                captured_text += `\n${this._i.library.reason}: ${this._i.trigger[video.trigger.toLowerCase()]}`
            }
            this._set( id,{title: captured_text, alt: captured_text, src: video.thumbnail} )
            this._show( id )

            // highlight is on at this level and we have something?
            if( show_triggers && video.trigger !== null ) {
                const coords = video.trigger_region.split(",")

                let box = this._element( bid )
                box.style.left = `${parseFloat(coords[0]) * 100}%`
                box.style.top = `${parseFloat(coords[1]) * 100}%`
                box.style.width = `${(parseFloat(coords[2]) - parseFloat(coords[0])) * 100}%`
                box.style.height = `${(parseFloat(coords[3]) - parseFloat(coords[1])) * 100}%`
                box.style.borderStyle = "solid"
                box.style.borderWidth = "thin"
                box.style.borderColor = video.trigger in this.lc.colors ?
                                               this.lc.colors[video.trigger] : "cyan"
                this._set( bid,{title: captured_text, alt: captured_text } )
                this._show( bid )
            } else {
                this._hide( bid )
            }

            // download icon
            const aid = `library-a-${i}`
            this._element( aid ).href = video.url
            this._hide( aid )

        }
        for( ; i < this.ls.gridCount; i++ ) {
            this._hide(`library-${i}`)
            this._hide(`library-box-${i}`)
            this._hide(`library-a-${i}`)
        }

        // save state
        this.ls.lastOffset = this.ls.offset
        this.gs.libraryCamera = this._cameraIndex

        const not_at_start = this.ls.offset !== 0
        this._set( "library-control-first",{
            title: not_at_start ? this._i.library.first_page : "",
            icon: 'mdi:page-first',
            state: not_at_start ? "on" : "off"
        })
        this._set( "library-control-previous",{
            title: not_at_start ? this._i.library.previous_page : "",
            icon: 'mdi:chevron-left',
            state: not_at_start ? "on" : "off"
        })

        this._set( "library-control-resize",{ title: this._i.library.next_size, icon: 'mdi:resize', state: "on" })
        this._set( "library-control-close",{ title: this._i.library.close, icon: 'mdi:close', state: "on" })

        const not_at_end = this.ls.offset + this.ls.gridCount < this.ls.recordings.length
        this._set( "library-control-next",{
            title: not_at_end ? this._i.library.next_page : "",
            icon: 'mdi:chevron-right',
            state: not_at_end ? "on" : "off"
        })
        this._set( "library-control-last",{
            title: not_at_end ? this._i.library.last_page : "",
            icon: 'mdi:page-last',
            state: not_at_end ? "on" : "off"
        })
    }

    updateLibraryView() {

        // If camera index has changed then load library
        if ( this.gs.libraryCamera !== this._cameraIndex ) {
            this._log( `library-camera-change` )
            this._updateLibraryHTML()
            this._updateLibraryView()

        // Resized? Rebuild grid and force reload of images.
        } else if ( this.gs.librarySize !== this.lc.sizes[this.ls.sizeIndex] ) {
            this._log( `library-size-change` )
            this._updateLibraryHTML()
            this._updateLibraryView()

        // If offset has changed then reload images
        } else if ( this.ls.lastOffset !== this.ls.offset ) {
            this._log( `library-view-update` )
            this._updateLibraryView()
        } 
    }

    showLibraryView() {
        this._show("library-viewer")
        this._show("library-controls")
        this.hideRecordingView()
        this.hideStreamView()
        this.hideImageView()
        this.hideModal()
    }

    hideLibraryView() {
        this._hide("library-viewer")
        this._hide("library-controls")
    }

    // RECORDING VIEW

    setupRecordingView() {
        this._show("video-stop")
        this._show("video-full-screen")
        this._show("modal-video-stop")
        this._show("modal-video-full-screen")
        this._show("modal-video-door-lock", this.cc.doorLockId )
        this._show("modal-video-light-on", this.cc.lightId )

        this._set ("video-stop", {title: this._i.video.stop, icon: "mdi:stop"} )
        this._set ("video-full-screen", {title: this._i.video.fullscreen, icon: "mdi:fullscreen"} )

        this._set ("modal-video-stop", {title: this._i.video.stop, icon: "mdi:stop"} )
        this._set ("modal-video-full-screen", {title: this._i.video.fullscreen, icon: "mdi:fullscreen"} )
    }

    setupRecordingPlayer() {
        this._mset( 'video-player',{src: this.gs.recording, poster: this.gs.poster} )
        this._mshow("video-seek")
        this._mshow("video-play-pause")
        this._mhide("video-door-lock")
        this._mhide("video-light-on")
    }

    setupRecordingHandlers() {
        [ this._element( "video-player" ), this._element( "modal-video-player" )]
            .forEach( (player) => {
                player.addEventListener( 'ended', (evt) => {
                    this.videoEnded()
                })
                player.addEventListener( 'click', (evt) => {
                    this.videoClicked()
                })
                player.addEventListener( 'mouseover', (evt) => {
                    this.videoMouseEvent()
                })
                player.addEventListener( 'mousemove', (evt) => {
                    this.videoMouseEvent()
                })
                player.addEventListener( 'loadedmetadata', (evt) => {
                    this.setUpSeekBar();
                    this.startVideo( evt.target )
                    this.showVideoControls(4);
                })
            })
    }

    updateRecordingView() {

        let video = this._melement( 'video-player' )
        if( video.paused ) {
            this._mset("video-play-pause", {title: this._i.video.play, icon:"mdi:play"})
        } else {
            this._mset("video-play-pause", {title: this._i.video.pause, icon:"mdi:pause"})
        }
        if( video.muted ) {
            this._mset("video-toggle-sound", {icon:"mdi:volume-off"})
        } else {
            this._mset("video-toggle-sound", {icon:"mdi:volume-high"})
        }
    }

    showRecordingView() {
        this.hideStreamView()
        this._mshow("video-player")
        this._mshow("video-controls")
        this.showModal()
        this.hideLibraryView()
        this.hideImageView()
    }

    hideRecordingView() {
        this._mhide("video-player")
        this._mhide("video-controls")
        this.hideModal()
    }

    showRecording() {
        this.setupRecordingPlayer()
        this.updateRecordingView()
        this.showRecordingView()
    }
 
    setMPEGStreamElementData() {
        const video = this._melement('video-player')
        const et = this._findEgressToken( this.gs.stream );

        this.gs.dash = dashjs.MediaPlayer().create();
        this.gs.dash.extend("RequestModifier", () => {
            return {
                modifyRequestHeader: function (xhr) {
                    xhr.setRequestHeader('Egress-Token',et);
                    return xhr;
                }
            };
        }, true);
        this.gs.dash.initialize( video, this.gs.stream, true )
    }

    destroyMPEGStream() {
        if(this.gs.hls) {
            this.gs.hls.stopLoad();
            this.gs.hls.destroy();
            this.gs.hls = null
        }
    }

    setHLSStreamElementData() {
        const video = this._melement('video-player')

        if (Hls.isSupported()) {
            this.gs.hls = new Hls();
            this.gs.hls.attachMedia(video);
            this.gs.hls.on(Hls.Events.MEDIA_ATTACHED, () => {
                this.gs.hls.loadSource(this.gs.stream);
                this.gs.hls.on(Hls.Events.MANIFEST_PARSED, () => {
                    video.play();
                });
            })
        } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
            video.src = this.gs.stream;
            video.addEventListener('loadedmetadata', () => {
                video.play();
            });
        }
    }

    destroyHLSStream() {
        if(this.gs.dash) {
            this.gs.dash.reset();
            this.gs.dash = null;
        }
    }

    // Handled in setupRecordingView
    setupStreamView() {
    }

    setupStreamPlayer() {

        if ( this.gs.stream.includes('egressToken') ) {
            this.setMPEGStreamElementData()
        } else {
            this.setHLSStreamElementData()
        }

        this._mhide("video-play-pause")
        this._mhide("video-seek")
        this.showVideoControls(4);

        this._mset('video-player', {poster: this.gs.poster})
    }

    updateStreamView() {

        // Autostart?
        if ( this.gs.stream === null ) {
            if( this.cs.autoPlay && this.cs.autoPlayTimer === null ) {
                this.cs.autoPlayTimer = setTimeout( () => {
                    this.playStream()
                },5 * 1000 )
            }
            return
        }

        this._mset( "video-door-lock", {title: this.cs.doorLockText, icon: this.cs.doorLockIcon, state: this.cs.doorLockState} )
        this._mset( "video-light-on", {title: this.cs.lightText, icon: this.cs.lightIcon, state: this.cs.lightState} )

        if( this._melement( 'video-player' ).muted ) {
            this._mset("video-toggle-sound", {icon:"mdi:volume-off"})
        } else {
            this._mset("video-toggle-sound", {icon:"mdi:volume-high"})
        }
    }

    showStreamView() {
        this.hideRecordingView()
        this._mshow("video-player")
        this._mshow("video-controls")
        this.showModal()
        this.hideLibraryView()
        this.hideImageView()
    }

    hideStreamView() {
        this._mhide("video-player")
        this._mhide("video-controls")
        this.hideModal()
    }

    showStream() {
        this.setupStreamPlayer()
        this.updateStreamView()
        this.showStreamView()
    }

    updateView() {
        this.updateStatuses()
        this.updateImageView()
        this.updateLibraryView()
        this.updateRecordingView()
        this.updateStreamView()
    }

    updateVideoOrStreamView() {
        if( this.gs.stream !== null ) {
            this.updateStreamView()
        } else if( this.gs.recording !== null ) {
            this.updateRecordingView()
        }
    }

    /**
     * Get every ready.
     *
     * Run when render() is called. The function will keep calling
     * itself until initialisation is complete. What is does:
     *  - load the card's language pack
     *  - load the camera libraries
     *  - wait for the render to be added to the DOM
     *  - set up static view configuration
     *  - open initial view
     *
     * @param lang_loaded true if language is loaded
     * @param lib_loaded true if libraries are loaded
     */
    initialSetup( lang_loaded = false, lib_loaded = 0 ) {

        // Load language pack
        if( !lang_loaded ) {
            this.asyncLoadLanguage().then( () => {
                this.initialSetup( true, false )
            })
            return
        }

        // Now load the libraries.
        if( !lib_loaded ) {
            this.asyncLoadLibraries().then( () => {
                this.initialSetup( true, true )
            })
            return
        }

        // Now wait for the elements to be added to the shadow DOM.
        if( this._element("camera-viewer") === null ) {
            this._log( 'waiting for an element ' )
            setTimeout( () => {
                this.initialSetup( lang, index )
            }, 100);
            return
        }

        // If we are here:
        //  - language packs are in
        //  - library are loaded
        //  - DOM is ready
        this._ready = true

        // Set initial state
        this.updateStatuses()

        // Install the static stuff.
        this.setupImageView()
        this.setupLibraryView()
        this.setupRecordingView()
        this.setupStreamView()

        this.setupImageHandlers()
        this.setupLibraryHandlers()
        this.setupRecordingHandlers()

        // And go...
        this.updateImageView()
        this.updateLibraryView()
        this.showImageView()
    }

    resetView() {
        if ( this.ls.showing ) {
            this.showLibraryView()
        } else {
            this.showImageView()
        }
    }

    async wsLoadLibrary( index ) {
        try {
            const library = await this._hass.callWS({
                type: "aarlo_library",
                entity_id: this._cc[index].id,
                at_most: this._lc[index].recordings,
            });
            return ( library.videos.length > 0 ) ? library.videos : [];
        } catch (err) {
            throw `wsLoadLibrary failed ${err}`
        }
    }

    async wsStartStream() {
        try {
            return await this._hass.callWS({
                type: this.cc.directPlay ? "aarlo_stream_url" : "camera/stream",
                entity_id: this.cc.id,
            })
        } catch (err) {
            throw `wsStartStream failed ${err}`
        }
    }

    async wsStopStream() {
        try {
            return await this._hass.callWS({
                type: "aarlo_stop_activity",
                entity_id: this.cc.id,
            })
        } catch (err) {
            throw `wsStopStream failed ${err}`
        }
        
    }

    async wsUpdateSnapshot() {
        try {
            return await this._hass.callWS({
                type: "aarlo_request_snapshot",
                entity_id: this.cc.id
            })
        } catch (err) {
            throw `wsUpdateSnapshot failed ${err}`
        }
    }

    updateSnapshot() {
        this.wsUpdateSnapshot()
            .then()
            .catch( (e) => {
                this._log( e )
            })
    }

    pauseVideo( video ) {
        video.pause()
        this.updateVideoOrStreamView()
    }

    startVideo( video ) {
        let promise = video.play()
        if( promise !== undefined ) {
            promise.then( () => {
                this.updateVideoOrStreamView()
            }).catch( () => {
                this.updateVideoOrStreamView()
            })
        } else {
            this.updateVideoOrStreamView()
        }
    }

    getViewType( c ) {
        if( c.smartPlayer ) {
            return this.gc.isMobile ? "" : "modal"
        } else if( c.modalPlayer ) {
            return "modal"
        } 
        return ""
    }
                                
    playStream( ) {
        this.cs.autoPlayTimer = null
        if ( this.gs.stream === null ) {
            if( this.cc.autoPlay ) {
                this.cs.autoPlay = this.cc.autoPlay
            }
            this._melement('video-player').muted = this.gs.isMuted
            this.wsStartStream()
                .then( (stream) => {
                    this.gs.viewer = this.getViewType( this.cc )
                    this.gs.stream = stream.url;
                    this.gs.poster = this.cs.image;
                    this.showStream()
                })
                .catch( (e) => {
                    this._log( e )
                })
        } else {
            this.showStream()
        }
    }

    stopStream() {
        this.resetView()
        this._melement('video-player' ).pause()
        this.cs.autoPlay = false
        this.gs.stream = null;
        this.destroyMPEGStream()
        this.destroyHLSStream()
        this.wsStopStream()
            .then()
            .catch( (e) => {
                this._log( e )
            })
    }

    showOrStopStream() {
        const camera = this._getState(this.cc.id,'unknown');
        if ( camera.state === 'streaming' ) {
            this.stopStream()
        } else {
            this.gs.viewer = this.getViewType( this.cc )
            this.playStream()
        }
    }

    async asyncLoadLanguage() {
        let lang = this.gc.lang ? this.gc.lang : this._hass.language

        // Load language pack. Try less specific before reverting to en.
        // testing: import(`https://twrecked.github.io/lang/${lang}.js?t=${lang_date}`)
        // final: import(`https://cdn.jsdelivr.net/gh/twrecked/lovelace-hass-aarlo@master/lang/${lang}.js`)
        let module = null
        while( !module ) {
            this._log( `importing ${lang} language` )
            try {
                module = await import(`https://twrecked.github.io/lang/${lang.toLowerCase()}.js?t=${new Date().getTime()}`)
                this._i = module.messages
            } catch( error ) {
                this._log( `failed to load language pack: ${lang}` )
                const lang_pieces = lang.split('-')
                lang = lang_pieces.length > 1 ? lang_pieces[0] : "en"
            }
        }
    }

    /**
     * Asynchronously load a camera's library.
     *
     * Because this operates in the background we save the camera index
     * and operate on the library state (_ls) directly.
     *
     * @param index camera to index to use
     * @returns {Promise<void>}
     */
    async asyncLoadLibrary( index ) {
        try {
            this._ls[index].recordings = await this.wsLoadLibrary( index )
        } catch(err) {
            this._log(err)
            this._ls[index].recordings = []
        }
    }

    async asyncLoadLibraries( ) {
        for( let i = 0; i < this._cameraCount; i++ ) {
            await this.asyncLoadLibrary(i)
        }
        this.mergeLibraries()
    }

    mergeLibraries() {
        if( !this.gc.blendedMode ) {
            return
        }
        let recordings = this._ls[0].recordings.slice()
        for( let i = 1; i < this._cameraCount; i++ ) {
            let j = 0
            let k = 0
            while( k < this._ls[i].recordings.length ) {
                if( j === recordings.length ) {
                    recordings.push( this._ls[i].recordings[k] )
                    k++
                } else if( recordings[j].created_at < this._ls[i].recordings[k].created_at ) {
                    recordings.splice( j, 0, this._ls[i].recordings[k] )
                    k++
                }
                j++
            }
        }
        this._ls[this._cameraCount].recordings = recordings
    }

    openLibrary() {
        if( this.ls.recordings && this.ls.recordings.length > 0 ) {
            this.ls.showing = true
            this.getModalDimensions()
            this.updateLibraryView()
            this.showLibraryView()
        }
    }

    playRecording(index) {
        if ( this.gs.recording === null ) {
            index += this.ls.offset;
            if (this.ls.recordings && index < this.ls.recordings.length) {
                this._melement( 'video-player' ).muted = this.gs.isMuted
                this.gs.viewer    = this.getViewType( this.lc )
                this.gs.recording = this.ls.recordings[index].url;
                this.gs.poster    = this.ls.recordings[index].thumbnail;
                this.showRecording()
            } 
        }
    }

    playLatestRecording() {
        this._melement( 'video-player' ).muted = this.gs.isMuted
        this.gs.viewer    = this.getViewType( this.cc )
        this.gs.recording = this.cs.lastRecording
        this.gs.poster    = this.cs.image
        this.showRecording()
    }

    stopRecording() {
        if ( this.gs.recording ) {
            this.pauseVideo(this._melement( 'video-player' ))
            this.hideModal()
            this.resetView()
            this.gs.recording = null
        }
    }

    firstLibraryPage() {
        this.ls.offset = 0
        this.updateLibraryView()
    }

    previousLibraryPage() {
        this.ls.offset = Math.max(this.ls.offset - this.ls.gridCount, 0)
        this.updateLibraryView()
    }

    nextLibraryPage() {
        const last = Math.max(this.ls.recordings.length - this.ls.gridCount, 0)
        this.ls.offset = Math.min(this.ls.offset + this.ls.gridCount, last)
        this.updateLibraryView()
    }

    lastLibraryPage() {
        this.ls.offset = Math.max(this.ls.recordings.length - this.ls.gridCount, 0)
        this.updateLibraryView()
    }

    resizeLibrary() {
        this.ls.sizeIndex += 1
        if( this.ls.sizeIndex === this.lc.sizes.length ) {
            this.ls.sizeIndex = 0
        }
        this.updateLibraryView()
    }

    closeLibrary() {
        this.ls.showing = false
        this.stopRecording()
        this.showImageView()
    }

    imageFailed() {
        this.cs.details.viewer = {title: "", alt: "", src: null}
        this.cs.image = null
        this.updateImageView()
        this.showImageView()
        this._log("image load failed")
    }

    imageClicked() {
        if ( this.cc.playStream ) {
            this.playStream()
        } else {
            this.playLatestRecording()
        }
    }

    setCameraImage( index ) {
        this._cameraIndex = index
        this.setupImageView()
        this.setupLibraryView()
        this.updateImageView()
    }

    nextCameraImage() {
        this.setCameraImage( this._cameraIndex === (this._cameraCount - 1) ? 0 : (this._cameraIndex + 1) )
    }

    previousCameraImage() {
        this.setCameraImage( this._cameraIndex === 0 ? (this._cameraCount - 1) : (this._cameraIndex - 1) )
    }

    videoEnded() {
        this.stopRecording()
        this.stopStream()
    }

    videoClicked() {
        if ( this._misHidden("video-controls") ) {
            this.showVideoControls(2)
        } else {
            this.hideVideoControls();
        }
    }

    videoMouseEvent() {
        this.showVideoControls(2)
    }

    controlStop() {
        this.stopRecording()
        this.stopStream()
    }

    controlPlayPause( ) {
        let video = this._melement( 'video-player' )
        if( video.paused ) {
            this.startVideo( video )
        } else {
            this.pauseVideo( video )
        }
    }

    controlToggleSound( ) {
        let video = this._melement('video-player')
        video.muted = !video.muted;
        this.gs.isMuted = video.muted
        this.updateVideoOrStreamView()
    }

    controlFullScreen() {
        let video = this._melement('video-player')
        if (video.requestFullscreen) {
            video.requestFullscreen().then()
        } else if (video.mozRequestFullScreen) {
            video.mozRequestFullScreen(); // Firefox
        } else if (video.webkitRequestFullscreen) {
            video.webkitRequestFullscreen(); // Chrome and Safari
        }
    }

    toggleCamera( ) {
        if ( this.cs.state === 'off' ) {
            this._hass.callService( 'camera','turn_on', { entity_id: this.cc.id } )
        } else {
            this._hass.callService( 'camera','turn_off', { entity_id: this.cc.id } )
        }
    }

    toggleLock( id ) {
        if ( this._getState(id,'locked').state === 'locked' ) {
            this._hass.callService( 'lock','unlock', { entity_id:id } )
        } else {
            this._hass.callService( 'lock','lock', { entity_id:id } )
        }
    }

    toggleLight( id ) {
        if ( this._getState(id,'on').state === 'on' ) {
            this._hass.callService( 'light','turn_off', { entity_id:id } )
        } else {
            this._hass.callService( 'light','turn_on', { entity_id:id } )
        }
    }

    toggleSwitch( id ) {
        if ( this._getState(id,'on').state === 'on' ) {
            this._hass.callService( 'switch','turn_off', { entity_id:id } )
        } else {
            this._hass.callService( 'switch','turn_on', { entity_id:id } )
        }
    }

    setUpSeekBar() {
        let video = this._melement('video-player')
        let seekBar = this._melement('video-seek')

        video.addEventListener( "timeupdate", () => {
            seekBar.value = (100 / video.duration) * video.currentTime;
        });
        seekBar.addEventListener( "change", () => {
            video.currentTime = video.duration * (seekBar.value / 100);
        });
        seekBar.addEventListener( "mousedown", () => {
            this.showVideoControls(0);
            video.pause();
        });
        seekBar.addEventListener( "mouseup", () => {
            video.play();
            this.hideVideoControlsLater()
        });
    }
  
    showVideoControls(seconds = 0) {
        this._mshow("video-controls")
        this._melement("video-player").style.cursor = ""
        this.hideVideoControlsCancel();
        if (seconds !== 0) {
            this.hideVideoControlsLater(seconds);
        }
    }

    hideVideoControls() {
        this.hideVideoControlsCancel();
        this._mhide("video-controls")
        this._melement("video-player").style.cursor = "none"
    }

    hideVideoControlsLater(seconds = 2) {
        this.hideVideoControlsCancel();
        this.cs.controlTimeout = setTimeout(() => {
            this.cs.controlTimeout = null;
            this.hideVideoControls()
        }, seconds * 1000);
    }

    hideVideoControlsCancel() {
        if ( this.cs.controlTimeout !== null ) {
            clearTimeout( this.cs.controlTimeout );
            this.cs.controlTimeout = null
        }
    }

    showDownloadIcon(index) {
        if( this.lc.download ) {
            this._show(`library-a-${index}`)
        }
    }

    hideDownloadIcon(index) {
        this._hide(`library-a-${index}`)
    }
}

// Bring in our custom scripts
const scripts = [
    "https://cdn.jsdelivr.net/npm/hls.js@latest",
    "https://cdn.dashjs.org/v3.2.1/dash.all.min.js",
]
function load_script( number ) {
    if ( number < scripts.length ) {
        const script = document.createElement("script")
        script.src = scripts[ number ]
        script.onload = () => {
            load_script( number + 1 )
        }
        document.head.appendChild(script)
    } else {
        customElements.define('aarlo-glance', AarloGlance)
    }
}
load_script( 0 )

// vim: set expandtab:ts=4:sw=4
