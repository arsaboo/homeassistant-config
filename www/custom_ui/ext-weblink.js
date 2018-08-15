class ExtWebLink extends HTMLElement {
  set hass(hass) {
    if (!this.config.entity) {
      var state = "";
    } else {
      var state = hass.states[this.config.entity].state;
    }
    this.innerHTML =`
      <style>
        a {
          display: flex;
          align-items: center;
          color: var(--primary-color);
          text-decoration-line: none;
        }
        ha-icon {
          padding: 8px;
          color: var(--paper-item-icon-color);
        }
        ha-icon .innline {
          padding: 0px;
          color: var(--paper-item-icon-color);
        }
        div {
          flex: 1;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          margin-left: 16px;
        }
        div .state {
          text-align: right;
        }
      </style>
      <a href="${this.config.url}" target="_blank">
      <ha-icon icon="${this.config.icon}"></ha-icon>
        <div class="name">
          ${this.config.name} <ha-icon icon="mdi:open-in-new" class="innline"></ha-icon>
        </div>
        <div class="state">
          ${state}
        </div>
      </a>
    `;
  }
  setConfig(config) {
    this.config = config;
  }

  getCardSize() {
    return 1;
  }
}
customElements.define('ext-weblink', ExtWebLink);