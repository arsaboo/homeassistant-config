class SliderEntityRow extends Polymer.Element {
  static get template() {
    let slider = Polymer.html`
      <paper-slider min="[[min]]" max="[[max]]" value="{{value}}" on-change="selectedValue" on-click="stopPropagation"></paper-slider>
      `
    return Polymer.html`
    <style>
      hui-generic-entity-row {
        margin: var(--ha-themed-slider-margin, initial);
      }
      paper-slider {
        margin-left: auto;
      }
      .second-line paper-slider {
        width: 100%;
      }
    </style>
    <hui-generic-entity-row config="[[_config]]" hass="[[_hass]]">
      <template is='dom-if' if='{{showTop}}'>
      ${slider}
      </template>
      <template is='dom-if' if='{{!hideControl}}'>
      <ha-entity-toggle state-obj="[[stateObj]]" hass="[[_hass]]"></ha-entity-toggle>
      </template>
      </hui-generic-entity-row>
      <template is='dom-if' if='{{showBottom}}'>
      <div class="second-line">
      ${slider}
      </div>
      </template>
    `
  }

  static get properties() {
    return {
      _hass: Object,
      _config: Object,
      hideControl: { type: Boolean, value: false },
      breakSlider: { type: Boolean, value: false },
      hideWhenOff: { type: Boolean, value: false },
      isOn: { type: Boolean },
      stateObj: { type: Object, value: null },
      min: { type: Number, value: 0 },
      max: { type: Number, value: 255 },
      attribute: { type: String, value: 'brightness' },
      value: Number,
    };
  }

  setConfig(config)
  {
    this._config = config;
    if('hide_control' in config && config.hide_control)
      this.hideControl = true;
    if('break_slider' in config && config.break_slider)
      this.breakSlider = true;
    if('hide_when_off' in config && config.hide_when_off)
      this.hideWhenOff = true;
  }

  updateSliders()
  {
    this.showTop = false;
    this.showBottom = false;
    if(!(this.attribute in this.stateObj.attributes)) {
      if(!('supported_features' in this.stateObj.attributes) ||
        !(this.stateObj.attributes['supported_features'] & 1)) {
          return;
      }
    }
    if(!(this.hideWhenOff && !this.isOn)) {
      if(this.breakSlider)
        this.showBottom = true;
      else
        this.showTop = true;
    }
  }

  set hass(hass) {
    this._hass = hass;
    this.stateObj = this._config.entity in hass.states ? hass.states[this._config.entity] : null;
    if(this.stateObj) {
      if(this.stateObj.state === 'on') {
        this.value = this.stateObj.attributes[this.attribute];
        this.isOn = true;
      } else {
        this.value = this.min;
        this.isOn = false;
      }
      this.updateSliders();
    }
  }

  selectedValue(ev) {
    const value = parseInt(this.value, 10);
    const param = {entity_id: this.stateObj.entity_id };
    if(Number.isNaN(value)) return;
    if(value === 0) {
      this._hass.callService('light', 'turn_off', param);
    } else {
      param[this.attribute] = value;
      this._hass.callService('light', 'turn_on', param);
    }
  }

  stopPropagation(ev) {
    ev.stopPropagation();
  }
}

customElements.define('slider-entity-row', SliderEntityRow);
