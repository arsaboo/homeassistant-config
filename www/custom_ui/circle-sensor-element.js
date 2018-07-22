import {
  LitElement,
  html
} from 'https://unpkg.com/@polymer/lit-element@^0.5.2/lit-element.js?module';

class CircleSensorElement extends LitElement {
  static get properties() {
    return {
      hass: Object,
      config: Object,
      state: Object,
      dashArray: String,
    }
  }

  _render({
    state,
    dashArray
  }) {
    return html `
      <style>
          :host {
            cursor: pointer;
          }
          svg {
            transform: rotate(-90deg);
          }

          .container {
            position: relative;
            height: 100%;
            width: 100%;
          }

          .labelContainer {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
          }

          #label {
            display: flex;
            line-height: 1;
          }

          .text {
            font-size: 100%;
          }
          .unit {
            font-size: 75%;
          }

      </style>
      <div class="container" id="container">
        <svg viewbox="0 0 200 200" id="svg">
          <circle id="circle" cx="50%" cy="50%" r="45%" fill="#FFF" stroke="#F82"
            stroke-width="6" stroke-dasharray$="${dashArray}"/>
        </svg>
        <span class="labelContainer">
          <span id="label">
            <span class="text">${state.state}</span>
            <span class="unit">${state.attributes.unit_of_measurement}</span>
          </span>
        </span>
      </div>
    `;
  }

  constructor() {
    super();
    this._clickListener = this._click.bind(this);
  }

  connectedCallback() {
    super.connectedCallback();
    this.addEventListener('click', this._clickListener);
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this.removeEventListener('click', this._clickListener);
  }

  ready() {
    super.ready();
    this.circle = this._root.querySelector('#circle');
    this._updateConfig();
  }

  setConfig(config) {
    if (!config.entity) {
      throw Error('No entity defined')
    }
    this.config = config;
    if (this.circle) {
      this._updateConfig();
    }
  }

  getCardSize() {
    return 3;
  }

  _updateConfig() {
    this.circle.setAttribute('fill', this.config.fill || 'rgba(255, 255, 255, .75)');
    this._root.querySelector('#label').style.fontSize = this.config.font_size || '1em';
    if (!isNaN(this.config.stroke_width)) {
      this.circle.setAttribute('stroke-width', this.config.stroke_width);
    }
  }

  set hass(hass) {
    this.state = hass.states[this.config.entity];
    if (!this.state || isNaN(this.state.state)) {
      console.error(`State is not a number: ${this.state.state}`);
      return;
    }
    const state = this.state.state;

    const r = 200 * .45;
    const min = this.config.min || 0;
    const max = this.config.max || 100;
    const val = this._calculateValueBetween(min, max, state);
    const score = val * 2 * Math.PI * r;
    const total = 10 * r;
    this.dashArray = `${score} ${total}`;

    let colorStops = {};
    colorStops[min] = this.config.stroke_color || '#03a9f4';
    if (this.config.color_stops) {
      Object.keys(this.config.color_stops).forEach((key) => {
        colorStops[key] = this.config.color_stops[key];
      });
    }

    const stroke = this._calculateStrokeColor(state, colorStops);
    if (this.circle) {
      this.circle.setAttribute('stroke', stroke);
    }
  }

  _click() {
    this._fire('hass-more-info', {
      entityId: this.config.entity
    });
  }

  _calculateStrokeColor(state, stops) {
    const sortedStops = Object.keys(stops).map(n => Number(n)).sort((a, b) => a - b);
    let start, end, val;
    const l = sortedStops.length;
    if (state <= sortedStops[0]) {
      return stops[sortedStops[0]];
    } else if (state >= sortedStops[l - 1]) {
      return stops[sortedStops[l - 1]];
    } else {
      for (let i = 0; i < l - 1; i++) {
        const s1 = sortedStops[i];
        const s2 = sortedStops[i + 1];
        if (state >= s1 && state < s2) {
          [start, end] = [stops[s1], stops[s2]];
          if (!this.config.gradient) {
            return start;
          }
          val = this._calculateValueBetween(s1, s2, state);
        }
      }
    }
    return this._getGradientValue(start, end, val);
  }

  _calculateValueBetween(start, end, val) {
    return (val - start) / (end - start);
  }

  _getGradientValue(colorA, colorB, val) {
    const v1 = 1 - val;
    const v2 = val;
    const decA = this._hexColorToDecimal(colorA);
    const decB = this._hexColorToDecimal(colorB);
    const rDec = Math.floor((decA[0] * v1) + (decB[0] * v2));
    const gDec = Math.floor((decA[1] * v1) + (decB[1] * v2));
    const bDec = Math.floor((decA[2] * v1) + (decB[2] * v2));
    const rHex = this._padZero(rDec.toString(16));
    const gHex = this._padZero(gDec.toString(16));
    const bHex = this._padZero(bDec.toString(16));
    return `#${rHex}${gHex}${bHex}`;
  }

  _hexColorToDecimal(color) {
    let c = color.substr(1);
    if (c.length === 3) {
      c = `${c[0]}${c[0]}${c[1]}${c[1]}${c[2]}${c[2]}`;
    }

    const r = parseInt(c.substr(0, 2), 16);
    const g = parseInt(c.substr(2, 2), 16);
    const b = parseInt(c.substr(4, 2), 16);

    return [r, g, b];
  }

  _padZero(val) {
    if (val.length < 2) {
      val = `0${val}`;
    }
    return val.substr(0, 2);
  }

  _fire(type, detail, options) {
    const node = this.shadowRoot;
    options = options || {};
    detail = (detail === null || detail === undefined) ? {} : detail;
    const event = new Event(type, {
      bubbles: options.bubbles === undefined ? true : options.bubbles,
      cancelable: Boolean(options.cancelable),
      composed: options.composed === undefined ? true : options.composed
    });
    event.detail = detail;
    node.dispatchEvent(event);
    return event;
  }
}
customElements.define('circle-sensor-element', CircleSensorElement);
