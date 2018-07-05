function _createStyle(element, scale) {
  element.textContent = `
    :host {
      text-align: center;
    }
    #value {
      font-size: 5em;
      line-height: 1.5em;
      color: var(--primary-text-color);
    }
    #title {
      font-size: 1.5em;
      padding-bottom: 16px;
      line-height: 1em;
      color: var(--secondary-text-color);
    }
  `;
}

class BigNumberCard extends HTMLElement {
  setConfig(config) {
    if (!config.entity) {
      throw new Error('Please define an entity');
    }

    if (this.lastChild) this.removeChild(this.lastChild);

    const cardConfig = Object.assign({}, config);

    const card = document.createElement('ha-card');

    const shadow = card.attachShadow({ mode: 'open' });
    const content = document.createElement('div');
    content.id = "value"
    const title = document.createElement('div');
    title.id = "title"
    title.textContent = config.title;
    const style = document.createElement('style');
    _createStyle(style, cardConfig.scale);
    shadow.appendChild(content);
    shadow.appendChild(title);
    shadow.appendChild(style);
    this.appendChild(card);
    this._config = cardConfig;
  }

  set hass(hass) {
    const config = this._config;
    const entityState = hass.states[config.entity].state;
    const measurement = hass.states[config.entity].attributes.unit_of_measurement;

    if (!config.entity || entityState !== this._entityState) {
      this.lastChild.shadowRoot.getElementById("value").textContent = `${entityState} ${measurement}`;
      this._entityState = entityState
    }
    this.lastChild.hass = hass;
  }

  getCardSize() {
    return 1;
  }
}

customElements.define('bignumber-card', BigNumberCard);