class DarkSkyWeatherCard extends HTMLElement {
  set hass(hass) {
    if (!this.content) {
      const card = document.createElement('ha-card');
      const link = document.createElement('link');
      link.type = 'text/css';
      link.rel = 'stylesheet';
      link.href = '/local/custom_ui/dark-sky-weather-card.css';
      card.appendChild(link);
      this.content = document.createElement('div');
      this.content.className = 'card';
      card.appendChild(this.content);
      this.appendChild(card);
    }

    const getUnit = function(measure) {
      const lengthUnit = hass.config.core.unit_system.length;
      switch (measure) {
        case 'air_pressure':
          return lengthUnit === 'km' ? 'hPa' : 'mbar';
        case 'length':
          return lengthUnit;
        case 'precipitation':
          return lengthUnit === 'km' ? 'mm' : 'in';
        default:
          return hass.config.core.unit_system[measure] || '';
      }
    };

    const transformDayNight = {
      "below_horizon": "night",
      "above_horizon": "day",
    }
    const sunLocation = transformDayNight[hass.states[this.config.entity_sun].state];
    const weatherIcons = {
      'clear-day': 'day',
      'clear-night': 'night',
      'rain': 'rainy-5',
      'snow': 'snowy-6',
      'sleet': 'rainy-6',
      'wind': 'cloudy',
      'fog': 'cloudy',
      'cloudy': 'cloudy',
      'partly-cloudy-day': 'cloudy-day-3',
      'partly-cloudy-night': 'cloudy-night-3',
      'hail': 'rainy-7',
      'lightning': 'thunder',
      'thunderstorm': 'thunder',
      'windy-variant': `cloudy-${sunLocation}-3`,
      'exceptional': '!!',
    }

    const windDirections = [
      'N',
      'NNE',
      'NE',
      'ENE',
      'E',
      'ESE',
      'SE',
      'SSE',
      'S',
      'SSW',
      'SW',
      'WSW',
      'W',
      'WNW',
      'NW',
      'NNW',
      'N'
    ];

    var forecastDate1 = new Date();
    forecastDate1.setDate(forecastDate1.getDate() + 1);
    var forecastDate2 = new Date();
    forecastDate2.setDate(forecastDate2.getDate() + 2);
    var forecastDate3 = new Date();
    forecastDate3.setDate(forecastDate3.getDate() + 3);
    var forecastDate4 = new Date();
    forecastDate4.setDate(forecastDate4.getDate() + 4);
    var forecastDate5 = new Date();
    forecastDate5.setDate(forecastDate5.getDate() + 5);


    const currentConditions = hass.states[this.config.entity_current_conditions].state;
    const humidity = hass.states[this.config.entity_humidity].state;
    const pressure = Math.round(hass.states[this.config.entity_pressure].state);
    const temperature = Math.round(hass.states[this.config.entity_temperature].state);
    const visibility = hass.states[this.config.entity_visibility].state;
    const windBearing = windDirections[(Math.round((hass.states[this.config.entity_wind_bearing].state / 360) * 16))];
    const windSpeed = Math.round(hass.states[this.config.entity_wind_speed].state);
    const forecast1 = {
      date: forecastDate1,
      condition: this.config.entity_forecast_icon_1,
      temphigh: this.config.entity_forecast_high_temp_1,
      templow: this.config.entity_forecast_low_temp_1,
    };
    const forecast2 = {
      date: forecastDate2,
      condition: this.config.entity_forecast_icon_2,
      temphigh: this.config.entity_forecast_high_temp_2,
      templow: this.config.entity_forecast_low_temp_2,
    };
    const forecast3 = {
      date: forecastDate3,
      condition: this.config.entity_forecast_icon_3,
      temphigh: this.config.entity_forecast_high_temp_3,
      templow: this.config.entity_forecast_low_temp_3,
    };
    const forecast4 = {
      date: forecastDate4,
      condition: this.config.entity_forecast_icon_4,
      temphigh: this.config.entity_forecast_high_temp_4,
      templow: this.config.entity_forecast_low_temp_4,
    };
    const forecast5 = {
      date: forecastDate5,
      condition: this.config.entity_forecast_icon_5,
      temphigh: this.config.entity_forecast_high_temp_5,
      templow: this.config.entity_forecast_low_temp_5,
    };

    const forecast = [forecast1, forecast2, forecast3, forecast4, forecast5];


    this.content.innerHTML = `
      <span class="icon bigger" style="background: none, url(/local/icons/weather_icons/animated/${weatherIcons[currentConditions]}.svg) no-repeat; background-size: contain;">${currentConditions}</span>
      <span class="temp">${temperature}</span><span class="tempc"> ${getUnit('temperature')}</span>
      <span>
        <ul class="variations right">
            <li><span class="ha-icon"><ha-icon icon="mdi:water-percent"></ha-icon></span>${humidity}<span class="unit"> %</span></li>
            <li><span class="ha-icon"><ha-icon icon="mdi:gauge"></ha-icon></span>${pressure}<span class="unit"> ${getUnit('air_pressure')}</span></li>
        </ul>
        <ul class="variations">
            <li><span class="ha-icon"><ha-icon icon="mdi:weather-windy"></ha-icon></span>${windBearing} ${windSpeed}<span class="unit"> ${getUnit('length')}/h</span></li>
            <li><span class="ha-icon"><ha-icon icon="mdi:weather-fog"></ha-icon></span>${visibility}<span class="unit"> ${getUnit('length')}</span></li>
        </ul>
      </span>
      <div class="forecast clear">
          ${forecast.map(daily => `
              <div class="day">
                  <span class="dayname">${(daily.date).toString().split(' ')[0]}</span>
                  <br><i class="icon" style="background: none, url(/local/icons/weather_icons/animated/${weatherIcons[hass.states[daily.condition].state]}.svg) no-repeat; background-size: contain;"></i>
                  <br><span class="highTemp">${Math.round(hass.states[daily.temphigh].state)}${getUnit('temperature')}</span>
                  <br><span class="lowTemp">${Math.round(hass.states[daily.templow].state)}${getUnit('temperature')}</span>
              </div>`).join('')}
      </div>`;
  }

  setConfig(config) {
    if (!config.entity_current_conditions ||
      !config.entity_humidity ||
      !config.entity_pressure ||
      !config.entity_temperature ||
      !config.entity_visibility ||
      !config.entity_wind_bearing ||
      !config.entity_wind_speed) {
      throw new Error('Please define entities');
    }
    this.config = config;
  }

  // @TODO: This requires more intelligent logic
  getCardSize() {
    return 3;
  }
}

customElements.define('dark-sky-weather-card', DarkSkyWeatherCard);
