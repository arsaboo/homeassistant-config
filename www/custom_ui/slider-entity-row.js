class SliderEntityRow extends Polymer.Element {
  static get template() {
    let slider = Polymer.html`
      <paper-slider
        min="[[min]]"
        max="[[max]]"
        value="{{value}}"
        step="[[step]]"
        pin
        on-change="selectedValue"
        ignore-bar-touch
        on-click="stopPropagation">
      </paper-slider>
      `
    return Polymer.html`
    <style>
      hui-generic-entity-row {
        margin: var(--ha-themed-slider-margin, initial);
      }
      .flex {
        display: flex;
        align-items: center;
      }
      .second-line paper-slider {
        width: 100%;
      }
    </style>
    <hui-generic-entity-row
      config="[[_config]]"
      hass="[[_hass]]"
      >
      <div class="flex">
        <template is='dom-if' if='{{displayTop}}'>
          ${slider}
        </template>
        <template is='dom-if' if='{{displayToggle}}'>
          <ha-entity-toggle
            state-obj="[[stateObj]]"
            hass="[[_hass]]"
          ></ha-entity-toggle>
        </template>
        <template is='dom-if' if='{{displayStatus}}'>
          <div>
            [[statusString(stateObj)]]
          </div>
        </template>
      </div>
    </hui-generic-entity-row>
    <template is='dom-if' if='{{displayBottom}}'>
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
      hideToggle: { type: Boolean, value: false },
      breakSlider: { type: Boolean, value: false },
      hideWhenOff: { type: Boolean, value: false },
      showValue: { type: Boolean, value: false },
      isOn: { type: Boolean },
      stateObj: { type: Object, value: null },
      min: { type: Number, value: 0 },
      max: { type: Number, value: 100 },
      step: { type: Number, value: 5 },
      attribute: { type: String, value: 'brightness' },
      value: Number,
    };
  }

  setConfig(config)
  {
    this._config = config;
    this.hideToggle = config.hide_control || config.hide_toggle || false;
    this.breakSlider = config.break_slider || false;
    this.hideWhenOff = config.hide_when_off || false;
    this.showValue = config.show_value || false;
  }

  statusString(stateObj) {
    let l18n = this._hass.resources[this._hass.language];
    if(stateObj.state === 'on') {
      return Math.ceil(stateObj.attributes[this.attribute]/2.55).toString(10);
    } else if (stateObj.state === 'off') {
      return l18n['state.default.off'];
    } else {
      return l18n['state.default.unavailable'];
    }
  }

  updateSliders()
  {
    this.displayTop = false;
    this.displayBottom = false;
    this.displayToggle = true;
    this.displayStatus = false;

    if(this.hideToggle) this.displayToggle = false;

    if(this.showValue) {
      this.displayToggle = false;
      this.displayStatus = true;
    }

    if(!(this.stateObj.state === 'on' || this.stateObj.state === 'off')) {
      this.displayToggle = false;
      this.displayStatus = true;
    }

    if(this.stateObj.state === 'on' || !this.hideWhenOff) {
      this.displayBottom = this.breakSlider;
      this.displayTop = !this.breakSlider;
    }

    if(!(this.attribute in this.stateObj.attributes)) {
      if(!('supported_features' in this.stateObj.attributes) ||
        !(this.stateObj.attributes['supported_features'] & 1)) {
          this.displayTop = this.displayBottom = false;
      }
    }

  }

  set hass(hass) {
    this._hass = hass;
    this.stateObj = this._config.entity in hass.states ? hass.states[this._config.entity] : null;
    if(this.stateObj) {
      if(this.stateObj.state === 'on') {
        this.value = this.stateObj.attributes[this.attribute]/2.55;
        this.isOn = true;
      } else {
        this.value = this.min;
        this.isOn = false;
      }
      this.updateSliders();
    }
  }

  selectedValue(ev) {
    const value = Math.ceil(parseInt(this.value, 10)*2.55);
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
