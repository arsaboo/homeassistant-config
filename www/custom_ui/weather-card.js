class weatherCard extends HTMLElement {
  set hass(hass) {
    if (!this.content) {
      const card = document.createElement('ha-card');
      card.header = 'Weather Forecast';
      const link = document.createElement('link');
      link.type = 'text/css';
      link.rel = 'stylesheet';
      link.href = '/local/css/homeassistant.css';
      card.appendChild(link);
      this.content = document.createElement('div');
      this.content.className = 'card';
      card.appendChild(this.content);
      this.appendChild(card);
      console.log('b',this);
    }

    var currentCondition;
    var humidity;
    var i;
    var iconToUse;
    var pressure;
    var sunLocation;
    var temperature;
    var visibility;
    var windBearing;
    var windSpeed;

  var dayWeatherIcons = {
    'clear-night': 'day',
    'cloudy': 'cloudy',
    'fog': 'cloudy',
    'hail': 'rainy-7',
    'lightning': 'thunder',
    'lightning-rainy': 'thunder',
    'partlycloudy': 'cloudy-day-3',
    'pouring': 'rainy-6',
    'rainy': 'rainy-5',
    'snowy': 'snowy-6',
    'snowy-rainy': 'rainy-7',
    'sunny': 'day',
    'windy': 'cloudy',
    'windy-variant': 'cloudy-day-3',
    'exceptional': '!!',
  };

  var nightWeatherIcons = {
    'clear-night': 'night',
    'cloudy': 'cloudy',
    'fog': 'cloudy',
    'hail': 'rainy-7',
    'lightning': 'thunder',
    'lightning-rainy': 'thunder',
    'partlycloudy': 'cloudy-night-3',
    'pouring': 'rainy-6',
    'rainy': 'rainy-5',
    'snowy': 'snowy-6',
    'snowy-rainy': 'rainy-7',
    'sunny': 'night',
    'windy': 'cloudy',
    'windy-variant': 'cloudy-night-3',
    'exceptional': '!!',
  };

  var windDirections = [
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
    //console.log('a',hass);
    for (i=0; i < this.config.entities.length; i++) {
        if (hass.states[this.config.entities[i]]._domain == "sun") {
            sunLocation = hass.states[this.config.entities[i]].state;
        } else if (hass.states[this.config.entities[i]]._domain == "weather") {
            currentCondition = hass.states[this.config.entities[i]].state;
            humidity = hass.states[this.config.entities[i]].attributes.humidity;
            pressure = hass.states[this.config.entities[i]].attributes.pressure;
            temperature = Math.round(hass.states[this.config.entities[i]].attributes.temperature);
            visibility = hass.states[this.config.entities[i]].attributes.visibility;
            windBearing = windDirections[(parseInt((hass.states[this.config.entities[i]].attributes.wind_bearing + 11.25) / 22.5))];
            windSpeed = hass.states[this.config.entities[i]].attributes.wind_speed;
        }
    }

    if (sunLocation == 'above_horizon') {
      iconToUse = dayWeatherIcons[currentCondition];
    } if (sunLocation == 'below_horizon') {
      iconToUse = nightWeatherIcons[currentCondition];
    }

    if (iconToUse) {
        //this.content = document.createElement('span');
      this.content.innerHTML = `
      <span class="icon bigger" style="background: none, url(/local/icons/weather_icons/animated/` + iconToUse + `.svg) no-repeat; background-size: contain;">` + currentCondition + `</span>
      <span class="temp">` + temperature + `</span><span class="temp_unit">°F</span>
      <br>
      <span>
        <ul class="variations right">
            <li><span class="iron-icon"><iron-icon icon="mdi:water-percent"></iron-icon></span>` + humidity + `<span class="unit"> %</span></li>
            <li><span class="iron-icon"><iron-icon icon="mdi:gauge"></iron-icon></span>` + pressure + `<span class="unit"> hPa</span></li>
        </ul>
        <ul class="variations">
            <li><span class="iron-icon"><iron-icon icon="mdi:weather-windy"></iron-icon></span>` + windBearing + ` ` + windSpeed + `<span class="unit"> mi/h</span></li>
            <li><span class="iron-icon"><iron-icon icon="mdi:weather-fog"></iron-icon></span>` + visibility + `<span class="unit"> mi</span></li>
        </ul>
      </span>
        `;
    }
  }

  // The height of your card. Home Assistant uses this to automatically
  // distribute all cards over the available columns.
  getCardSize() {
    return 3;
  }
}

customElements.define('weather-card', weatherCard);
