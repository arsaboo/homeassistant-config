import {
  LitElement,
  html
} from "https://unpkg.com/@polymer/lit-element@latest/lit-element.js?module";

class PcCard extends LitElement {
  static get properties() {
    return {
      hass: {},
      _config: {}
    };
  }

  constructor() {
    super();
  }

  getCardSize() {
    return 1;
  }

  setConfig(config) {
    this._config = config;
  }

  render() {
    if (!this._config || !this.hass) {
      return html``;
    }

    const states = this.hass.states;
    const pc_networth = states["sensor.pc_networth"];
    let pc_entities = [];

    Object.keys(states).forEach(function(entity) {
      if (entity.match("sensor.pc_") && !entity.match("sensor.pc_networth")) {
        pc_entities.push(states[entity]);
      }
    });

    return html`
      <ha-card .header="${this._config.title}">
        ${
          pc_networth
            ? html`
                <paper-item>
                  ${pc_networth.attributes.friendly_name.replace("PC ", "")}:
                  ${this.formatMoney(pc_networth.state)}
                </paper-item>
              `
            : ""
        }
        ${
          pc_entities.map(
            entity => html`
              <paper-item>
                ${entity.attributes.friendly_name.replace("PC ", "")}:
                ${this.formatMoney(entity.state)}
              </paper-item>
            `
          )
        }
      </ha-card>
    `;
  }

  formatMoney(amount, decimalCount = 2, decimal = ".", thousands = ",") {
    try {
      decimalCount = Math.abs(decimalCount);
      decimalCount = isNaN(decimalCount) ? 2 : decimalCount;

      const negativeSign = amount < 0 ? "-" : "";

      let i = parseInt(
        (amount = Math.abs(Number(amount) || 0).toFixed(decimalCount))
      ).toString();
      let j = i.length > 3 ? i.length % 3 : 0;

      return (
        negativeSign +
        (j ? i.substr(0, j) + thousands : "") +
        i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + thousands) +
        (decimalCount
          ? decimal +
            Math.abs(amount - i)
              .toFixed(decimalCount)
              .slice(2)
          : "")
      );
    } catch (e) {
      console.log(e);
    }
  }
}

customElements.define("pc-card", PcCard);
