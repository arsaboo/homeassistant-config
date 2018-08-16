class SliderEntityRow extends Polymer.Element {
  static get template() {
    return Polymer.html`
    <style>
      hui-generic-entity-row {
        margin: var(--ha-themed-slider-margin, initial);
      }
      paper-slider {
        margin-left: auto;
      }
    </style>
    <hui-generic-entity-row config="[[_config]]" hass="[[_hass]]">
      <paper-slider min="[[min]]" max="[[max]]" value="{{value}}" on-change="selectedValue" on-click="stopPropagation"></paper-slider>
      <ha-entity-toggle state-obj="[[stateObj]]" hass="[[_hass]]"></ha-entity-toggle>
      </hui-generic-entity-row>
    `
  }

  static get properties() {
    return {
      _hass: Object,
      _config: Object,
      stateObj: {
        type: Object,
        value: null,
      },
      min: {
        type: Number,
        value: 0,
      },
      max: {
        type: Number,
        value: 255,
      },
      attribute: {
        type: String,
        value: 'brightness',
      },
      value: Number,
    };
  }

  setConfig(config)
  {
    this._config = config;
  }

  set hass(hass) {
    this._hass = hass;
    this.stateObj = this._config.entity in hass.states ? hass.states[this._config.entity] : null;
    if(this.stateObj) {
      if(this.stateObj.state === 'on')
        this.value = this.stateObj.attributes[this.attribute];
      else
        this.value = this.min;
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
