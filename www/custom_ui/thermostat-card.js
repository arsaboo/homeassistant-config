import ThermostatUI from './thermostat-card.lib.js'
class ThermostatCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }
  set hass(hass) {
    const config = this._config;
    const entity = hass.states[config.entity];
    let hvac_state;
    if (config.hvac.attribute)
      hvac_state = entity.attributes[config.hvac.attribute];
    else
      hvac_state = entity.state;
    this.thermostat.updateState({
      min_value: entity.attributes.min_temp,
      max_value: entity.attributes.max_temp,
      ambient_temperature: entity.attributes.current_temperature,
      target_temperature: entity.attributes.temperature,
      target_temperature_low: entity.attributes.target_temp_low,
      target_temperature_high: entity.attributes.target_temp_high,
      hvac_state: config.hvac.states[hvac_state] || 'off',
      away: (entity.attributes.away_mode == 'on' ? true : false),
    });
    this._hass = hass
  }

  setConfig(config) {
    // Check config
    if (!config.entity && config.entity.split(".")[0] === 'climate') {
      throw new Error('Please define an entity');
    }

    // Cleanup DOM
    const root = this.shadowRoot;
    if (root.lastChild) root.removeChild(root.lastChild);

    // Prepare config defaults
    const cardConfig = Object.assign({}, config);
    cardConfig.hvac = Object.assign({}, config.hvac);
    if (!cardConfig.diameter) cardConfig.diameter = 400;
    if (!cardConfig.num_ticks) cardConfig.num_ticks = 150;
    if (!cardConfig.tick_degrees) cardConfig.tick_degrees = 300;
    if (!cardConfig.hvac.states) cardConfig.hvac.states = { 'off': 'off', 'heat': 'heat', 'cool': 'cool', };

    // Extra config values generated for simplicity of updates
    cardConfig.radius = cardConfig.diameter / 2;
    cardConfig.ticks_outer_radius = cardConfig.diameter / 30;
    cardConfig.ticks_inner_radius = cardConfig.diameter / 8;
    cardConfig.offset_degrees = 180 - (360 - cardConfig.tick_degrees) / 2;

    const card = document.createElement('ha-card');
    this.thermostat = new ThermostatUI(cardConfig);
    card.appendChild(this.thermostat.container);
    root.appendChild(card);
    this._config = cardConfig;
  }
}
customElements.define('thermostat-card', ThermostatCard);