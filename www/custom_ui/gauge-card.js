function _updateStyle(element, scale) {
  element.textContent = `
    :host {
      --base-unit: ${scale};
      height: calc(var(--base-unit)*3);
      position: relative;
    }
    .container{
      width: calc(var(--base-unit) * 4);
      height: calc(var(--base-unit) * 2);
      position: absolute;
      top: calc(var(--base-unit)*1.5);
      left: 50%;
      overflow: hidden;
      text-align: center;
      transform: translate(-50%, -50%);
    }
    .gauge-a{
      z-index: 1;
      position: absolute;
      background-color: var(--primary-background-color);
      width: calc(var(--base-unit) * 4);
      height: calc(var(--base-unit) * 2);
      top: 0%;
      border-radius:calc(var(--base-unit) * 2.5) calc(var(--base-unit) * 2.5) 0px 0px ;
    }
    .gauge-b{
      z-index: 3;
      position: absolute;
      background-color: var(--paper-card-background-color);
      width: calc(var(--base-unit) * 2.5);
      height: calc(var(--base-unit) * 1.25);
      top: calc(var(--base-unit) * 0.75);
      margin-left: calc(var(--base-unit) * 0.75);
      margin-right: auto;
      border-radius: calc(var(--base-unit) * 2.5) calc(var(--base-unit) * 2.5) 0px 0px ;
    }
    .gauge-c{
      z-index: 2;
      position: absolute;
      background-color: var(--label-badge-yellow);
      width: calc(var(--base-unit) * 4);
      height: calc(var(--base-unit) * 2);
      top: calc(var(--base-unit) * 2);
      margin-left: auto;
      margin-right: auto;
      border-radius: 0px 0px calc(var(--base-unit) * 2) calc(var(--base-unit) * 2) ;
      transform-origin:center top;
      transition: all 1.3s ease-in-out;
    }
    
    .gauge-data{
      z-index: 4;
      color: var(--primary-text-color);
      line-height: calc(var(--base-unit) * 0.3);
      position: absolute;
      width: calc(var(--base-unit) * 4);
      height: calc(var(--base-unit) * 2.1);
      top: calc(var(--base-unit) * 1.2);
      margin-left: auto;
      margin-right: auto;
      transition: all 1s ease-out;
    }
    .gauge-data #percent{
      font-size: calc(var(--base-unit) * 0.55);
    }
    .gauge-data #title{
      padding-top: calc(var(--base-unit) * 0.15);
      font-size: calc(var(--base-unit) * 0.30);
    }
  `;
}

function _updateContent(element) {
  element.innerHTML = `
    <div class="container">
      <div class="gauge-a"></div>
      <div class="gauge-b"></div>
      <div class="gauge-c" id="gauge"></div>
      <div class="gauge-data"><div id="percent"></div><div id="title"></div></div>
    </div>
  `;
}

function _translateTurn(value, config) {
  return 5 * (value - config.min) / (config.max - config.min)
}

function _computeSeverity(stateValue, sections) {
  let numberValue = Number(stateValue);
  const severityMap = {
    red: "var(--label-badge-red)",
    green: "var(--label-badge-green)",
    amber: "var(--label-badge-yellow)",
    normal: "var(--label-badge-blue)",
  }
  if (!sections) return severityMap["normal"];
  let sortable = [];
  for (let severity in sections) {
    sortable.push([severity, sections[severity]]);
  }
  sortable.sort((a, b) => { return a[1] - b[1] });

  if (numberValue >= sortable[0][1] && numberValue < sortable[1][1]) {
    return severityMap[sortable[0][0]]
  }
  if (numberValue >= sortable[1][1] && numberValue < sortable[2][1]) {
    return severityMap[sortable[1][0]]
  }
  if (numberValue >= sortable[2][1]) {
    return severityMap[sortable[2][0]]
  }
  return severityMap["normal"];
}

class GaugeCard extends HTMLElement {
  setConfig(config) {
    if (!config.entity) {
      throw new Error('Please define an entity');
    }

    if (this.lastChild) this.removeChild(this.lastChild);

    const cardConfig = Object.assign({}, config);
    if (!cardConfig.scale) cardConfig.scale = "50px";
    if (!cardConfig.min) cardConfig.min = 0;
    if (!cardConfig.max) cardConfig.max = 100;

    const card = document.createElement('ha-card');
    const shadow = card.attachShadow({ mode: 'open' });
    const content = document.createElement('div');
    const style = document.createElement('style');
    _updateStyle(style, cardConfig.scale);
    _updateContent(content);
    shadow.appendChild(content);
    shadow.appendChild(style);
    this.appendChild(card);
    this._config = cardConfig;
  }

  set hass(hass) {
    const config = this._config;
    const entityState = hass.states[config.entity].state;
    const measurement = hass.states[config.entity].attributes.unit_of_measurement;

    if (entityState !== this._entityState) {
      this.lastChild.shadowRoot.getElementById("percent").textContent = `${entityState} ${measurement}`;
      this.lastChild.shadowRoot.getElementById("title").textContent = config.title;
      const turn = _translateTurn(entityState, config) / 10;
      this.lastChild.shadowRoot.getElementById("gauge").style.transform = `rotate(${turn}turn)`;
      this.lastChild.shadowRoot.getElementById("gauge").style.backgroundColor = _computeSeverity(entityState, config.severity);
      this._entityState = entityState
    }

    this.lastChild.hass = hass;
  }

  getCardSize() {
    return 1;
  }
}

customElements.define('gauge-card', GaugeCard);