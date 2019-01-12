import {
  LitElement, html,
} from 'https://unpkg.com/@polymer/lit-element@^0.6.4/lit-element.js?module';

const weatherIconsDay = {
  clear: "day",
  cloudy: "cloudy",
  fog: "cloudy",
  hail: "rainy-7",
  lightning: "thunder",
  "lightning-rainy": "thunder",
  partlycloudy: "cloudy-day-3",
  pouring: "rainy-6",
  rainy: "rainy-5",
  snowy: "snowy-6",
  "snowy-rainy": "rainy-7",
  sunny: "day",
  windy: "cloudy",
  "windy-variant": "cloudy-day-3",
  exceptional: "!!",
};

const weatherIconsNight = {
  ...weatherIconsDay,
  "clear-night": "night",
  clear: "night",
  sunny: "night",
  partlycloudy: "cloudy-night-3",
  "windy-variant": "cloudy-night-3",
};

const windDirections = [
  "N",
  "NNE",
  "NE",
  "ENE",
  "E",
  "ESE",
  "SE",
  "SSE",
  "S",
  "SSW",
  "SW",
  "WSW",
  "W",
  "WNW",
  "NW",
  "NNW",
  "N",
];

const fireEvent = (
  node,
  type,
  detail,
  options
) => {
  options = options || {};
  detail = detail === null || detail === undefined ? {} : detail;
  const event = new Event(type, {
    bubbles: options.bubbles === undefined ? true : options.bubbles,
    cancelable: Boolean(options.cancelable),
    composed: options.composed === undefined ? true : options.composed,
  });
  event.detail = detail;
  node.dispatchEvent(event);
  return event;
};

function hasConfigOrEntityChanged(element, changedProps) {
  if (changedProps.has("_config")) {
    return true;
  }

  const oldHass = changedProps.get("hass");
  if (oldHass) {
    return (
      oldHass.states[element._config.entity] !==
      element.hass.states[element._config.entity] ||
      oldHass.states[sun.sun] !==
      element.hass.states[sun.sun]
    );
  }

  return true;
}

class WeatherCard extends LitElement {

  get properties() {
    return {
      _config: {},
      hass: {},
    };
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error("Please define a weather entity");
    }
    this._config = config;
  }

  shouldUpdate(changedProps) {
    return hasConfigOrEntityChanged(this, changedProps);
  }

  render() {
    if (!this._config || !this.hass) {
      return html``;
    }

    const stateObj = this.hass.states[this._config.entity];
    const lang = this.hass.selectedLanguage || this.hass.language;

    return html`
      ${this.renderStyle()}
      <ha-card @click="${this._handleClick}">
          <span
            class="icon bigger"
            style="background: none, url(/local/icons/weather_icons/animated/${
              this.getWeatherIcon(stateObj.state.toLowerCase(), this.hass.states["sun.sun"].state)
            }.svg) no-repeat; background-size: contain;"
            >${stateObj.state}</span
          >
          <span class="temp">${Math.round(stateObj.attributes.temperature)}</span
          ><span class="tempc"> ${this.getUnit("temperature")}</span>
          <span>
            <ul class="variations right">
              <li>
                <span class="ha-icon"
                  ><ha-icon icon="mdi:water-percent"></ha-icon></span
                >${stateObj.attributes.humidity}<span class="unit"> %</span>
              </li>
              <li>
                <span class="ha-icon"><ha-icon icon="mdi:gauge"></ha-icon></span
                >${stateObj.attributes.pressure}<span class="unit">
                  ${this.getUnit("air_pressure")}</span
                >
              </li>
            </ul>
            <ul class="variations">
              <li>
                <span class="ha-icon"
                  ><ha-icon icon="mdi:weather-windy"></ha-icon></span
                >${windDirections[(parseInt((stateObj.attributes.wind_bearing + 11.25) / 22.5))]} ${stateObj.attributes.wind_speed}<span class="unit">
                  ${this.getUnit("length")}/h</span
                >
              </li>
              <li>
                <span class="ha-icon"
                  ><ha-icon icon="mdi:weather-fog"></ha-icon></span
                >${stateObj.attributes.visibility}<span class="unit"> ${this.getUnit("length")}</span>
              </li>
            </ul>
          </span>
          <div class="forecast clear">
            ${
              stateObj.attributes.forecast.slice(0, 5)
                .map(
                  (daily) => html`
                  <div class="day">
                      <span class="dayname">${
                        new Date(daily.datetime).toLocaleDateString(lang, {weekday: 'short'}).split(" ")[0]
                      }</span>
                      <br><i class="icon" style="background: none, url(/local/icons/weather_icons/animated/${
                        weatherIconsDay[daily.condition.toLowerCase()]
                      }.svg) no-repeat; background-size: contain;"></i>
                      <br><span class="highTemp">${daily.temperature}${this.getUnit(
                    "temperature"
                  )}</span>
                      <br><span class="lowTemp">${daily.templow}${this.getUnit(
                    "temperature"
                  )}</span>
                  </div>`
                )
            }
          </div>
      </ha-card>
    `;
  }

  getWeatherIcon(condition, sun) {
    return sun == "above_horizon" ? weatherIconsDay[condition] : weatherIconsNight[condition];
  }

   getUnit(measure) {
      const lengthUnit = this.hass.config.unit_system.length;
      switch (measure) {
        case "air_pressure":
          return lengthUnit === "km" ? "hPa" : "inHg";
        case "length":
          return lengthUnit;
        case "precipitation":
          return lengthUnit === "km" ? "mm" : "in";
        default:
          return this.hass.config.unit_system[measure] || "";
      }
  }

  _handleClick() {
    fireEvent(this, "hass-more-info", { entityId: this._config.entity });
  }

  getCardSize() {
    return 3;
  }

  renderStyle() {
    return html`
      <style>
          ha-card {
            cursor: pointer;
            margin: auto;
            padding-top: 2.5em;
            padding-bottom: 1.3em;
            padding-left: 1em;
            padding-right:1em;
            position: relative;
          }

          .clear {
            clear: both;
          }

          .ha-icon {
            height: 18px;
            margin-right: 5px;
            color: var(--paper-item-icon-color);
          }

          .temp {
            font-weight: 300;
            font-size: 4em;
            color: var(--primary-text-color);
            position: absolute;
            right: 1em;
          }

          .tempc {
            font-weight: 300;
            font-size: 1.5em;
            vertical-align: super;
            color: var(--primary-text-color);
            position: absolute;
            right: 1em;
            margin-top: -14px;
            margin-right: 7px;
          }

          .variations {
            display: inline-block;
            font-weight: 300;
            color: var(--primary-text-color);
            list-style: none;
            margin-left: -2em;
            margin-top: 4.5em;
          }

          .variations.right {
            position: absolute;
            right: 1em;
            margin-left: 0;
            margin-right: 1em;
          }

          .unit {
            font-size: .8em;
          }

          .forecast {
            width: 100%;
            margin: 0 auto;
            height: 9em;
          }

          .day {
            display: block;
            width: 20%;
            float: left;
            text-align: center;
            color: var(--primary-text-color);
            border-right: .1em solid #d9d9d9;
            line-height: 2;
            box-sizing: border-box;
          }

          .dayname {
            text-transform: uppercase;
          }

          .forecast .day:first-child {
            margin-left: 0;
          }

          .forecast .day:nth-last-child(1) {
            border-right: none;
            margin-right: 0;
          }

          .highTemp {
            font-weight: bold;
          }

          .lowTemp {
            color: var(--secondary-text-color);
          }

          .icon.bigger {
            width: 10em;
            height: 10em;
            margin-top: -4em;
            position: absolute;
            left: 0em;
          }

          .icon {
            width: 50px;
            height: 50px;
            margin-right: 5px;
            display: inline-block;
            vertical-align: middle;
            background-size: contain;
            background-position: center center;
            background-repeat: no-repeat;
            text-indent: -9999px;
          }

          .weather {
            font-weight: 300;
            font-size: 1.5em;
            color: var(--primary-text-color);
            text-align: left;
            position: absolute;
            top: -0.5em;
            left: 6em;
            word-wrap: break-word;
            width: 30%;
          }
      </style>
    `;
  }
}

customElements.define("weather-card", WeatherCard);
