import 'https://unpkg.com/wired-card@0.6.5/wired-card.js?module';
import 'https://unpkg.com/wired-toggle@0.6.5/wired-toggle.js?module';
import {
  LitElement, html
} from 'https://unpkg.com/@polymer/lit-element@^0.5.2/lit-element.js?module';

function loadCSS(url) {
  const link = document.createElement('link');
  link.type = 'text/css';
  link.rel = 'stylesheet';
  link.href = url;
  document.head.appendChild(link);
}

loadCSS('https://fonts.googleapis.com/css?family=Gloria+Hallelujah');

class WiredToggleCard extends LitElement {
  static get properties() {
    return {
      hass: Object,
      config: Object,
    }
  }

  _render({ hass, config }) {
    return html`
      <style>
        :host {
          font-family: 'Gloria Hallelujah', cursive;
        }
        wired-card {
          background-color: white;
          padding: 16px;
          display: block;
          font-size: 18px;
        }
        .state {
          display: flex;
          justify-content: space-between;
          padding: 8px;
          align-items: center;
        }
        wired-toggle {
          margin-left: 8px;
        }
      </style>
      <wired-card elevation="2">
        ${config.entities.map(ent => hass.states[ent]).map((state) =>
          html`
            <div class='state'>
              ${state.attributes.friendly_name}
              <wired-toggle
                checked="${state.state === 'on'}"
                on-change="${ev => this._toggle(state)}"
              ></wired-toggle>
            </div>
          `
        )}
      </wired-card>
    `;
  }

  _toggle(state) {
    this.hass.callService('homeassistant', 'toggle', {
      entity_id: state.entity_id
    });
  }

  // The height of your card. Home Assistant uses this to automatically
  // distribute all cards over the available columns.
  getCardSize() {
    return this.config.entities.length + 1;
  }
}
customElements.define('wired-toggle-card', WiredToggleCard);
