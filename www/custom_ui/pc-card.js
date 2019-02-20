var LitElement =
  LitElement ||
  Object.getPrototypeOf(customElements.get("home-assistant-main"));
var html = LitElement.prototype.html;

let CURRENCY_SYMBOLS = {
  USD: "$", // US Dollar
  EUR: "€", // Euro
  CRC: "₡", // Costa Rican Colón
  GBP: "£", // British Pound Sterling
  ILS: "₪", // Israeli New Sheqel
  INR: "₹", // Indian Rupee
  JPY: "¥", // Japanese Yen
  KRW: "₩", // South Korean Won
  NGN: "₦", // Nigerian Naira
  PHP: "₱", // Philippine Peso
  PLN: "zł", // Polish Zloty
  PYG: "₲", // Paraguayan Guarani
  THB: "฿", // Thai Baht
  UAH: "₴", // Ukrainian Hryvnia
  VND: "₫" // Vietnamese Dong
};

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
        states[entity].attributes.accounts.sort(function(a, b) {
          if (a.firm_name < b.firm_name) {
            return -1;
          }
          if (a.firm_name > b.firm_name) {
            return 1;
          }
          if (a.name < b.name) {
            return -1;
          }
          if (a.name > b.name) {
            return 1;
          }
          return 0;
        });
        pc_entities.push(states[entity]);
      }
    });

    let order = [
      "Cash",
      "Investment",
      "Credit",
      "Loan",
      "Mortgage",
      "Other Asset",
      "Other Liability"
    ];

    pc_entities.sort(function(a, b) {
      return order.indexOf(a.attributes.friendly_name.replace("PC ", "")) - order.indexOf(b.attributes.friendly_name.replace("PC ", ""));
    });

    return html`
      ${this.renderStyle()}
      <ha-card>
        <ul class="list">
          <li class="netheader">
            <div class="row">NET WORTH</div>
            <div class="networth">
              ${
                this.formatMoney(
                  pc_networth.attributes.unit_of_measurement,
                  pc_networth.state,
                  0
                )
              }
            </div>
            <div class="row">
              <div>ASSETS</div>
              <div class="right">
                ${
                  this.formatMoney(
                    pc_networth.attributes.unit_of_measurement,
                    pc_networth.attributes.assets,
                    0
                  )
                }
              </div>
            </div>
            <div class="row">
              <div>LIABILITIES</div>
              <div class="right">
                ${
                  this.formatMoney(
                    pc_networth.attributes.unit_of_measurement,
                    pc_networth.attributes.liabilities,
                    0
                  )
                }
              </div>
            </div>
          </li>
          <div id="accounts">
            ${
              pc_entities.map(
                entity => html`
                  <div class="divider"></div>
                  <div
                    class="header row"
                    @click=${this.handleAccordion}
                    .category="${
                      entity.attributes.friendly_name.replace(/ /g, '-')
                    }"
                  >
                    <div
                      class="name"
                      .category="${
                        entity.attributes.friendly_name.replace(/ /g, '-')
                      }"
                    >
                      ${
                        entity.attributes.friendly_name
                          .replace("PC ", "")
                          .toUpperCase()
                      }
                    </div>
                    <div
                      class="right"
                      .category="${
                        entity.attributes.friendly_name.replace(/ /g, '-')
                      }"
                    >
                      ${
                        this.formatMoney(
                          entity.attributes.unit_of_measurement,
                          entity.state,
                          0
                        )
                      }
                    </div>
                  </div>
                  <div class="panel" id="${entity.attributes.friendly_name.replace(/ /g, '-')}">
                    ${
                      entity.attributes.accounts
                        ? entity.attributes.accounts.map(
                            account => html`
                              <div class="divider"></div>
                              <li class="account">
                                <div>
                                  <div class="subrow bold">
                                    <div>${account.name}</div>
                                    <div class="right">
                                      ${
                                        this.formatMoney(
                                          entity.attributes.unit_of_measurement,
                                          account.balance
                                        )
                                      }
                                    </div>
                                  </div>
                                  <div class="subrow">
                                    <div>${account.firm_name}</div>
                                    <div class="right">
                                      ${account.refreshed}
                                    </div>
                                  </div>
                                </div>
                              </li>
                            `
                          )
                        : ""
                    }
                  </div>
                `
              )
            }
          </div>
        </ul>
      </ha-card>
    `;
  }

  handleAccordion(e) {
    e.target.classList.toggle("active");
    let panel = this.shadowRoot.querySelector(`#${e.target.category}`);
    if (panel) {
      if (panel.style.display === "block") {
        panel.style.display = "none";
      } else {
        panel.style.display = "block";
      }
    }
  }

  renderStyle() {
    return html`
      <style>
        ha-card {
          padding: 16px 0px 16px 0px;
        }

        .list {
          list-style-type: none;
        }

        .divider {
          height: 1px;
          background-color: var(--divider-color);
          margin: 6px 40px 6px 0px;
        }

        .row,
        .header.row {
          font-weight: bold;
        }

        .row,
        .header.row,
        .subrow {
          display: flex;
        }

        .networth {
          padding: 16px 0px 16px 0px;
          font-size: 1.5em;
        }

        .subrow {
          font-size: 0.8em;
        }

        .subrow.bold {
          font-weight: bold;
        }

        .right {
          margin-left: auto;
        }

        .netheader,
        .header {
          margin-right: 40px;
        }

        .header {
          cursor: pointer;
        }

        .active,
        .header:hover {
          background-color: #ccc;
        }

        .panel {
          margin-right: 40px;
          overflow: hidden;
          display: none;
        }

        .name,
        .right {
          pointer-events: none;
        }
      </style>
    `;
  }

  formatMoney(
    currency,
    amount,
    decimalCount = 2,
    decimal = ".",
    thousands = ","
  ) {
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
        (CURRENCY_SYMBOLS[currency] !== undefined
          ? CURRENCY_SYMBOLS[currency]
          : "") +
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
