class CalendarCard extends HTMLElement {
  set hass(hass) {
    if (!this.content) {
      const card = document.createElement('ha-card');
      card.header = this.config.name;
      this.content = document.createElement('div');
      this.content.style.padding = '0 16px 16px';
      card.appendChild(this.content);
      this.appendChild(card);
      moment.locale(hass.language);
    }

    this._hass = hass;

    this
      .getAllEvents(this.config.entities)
      .then(events => this.updateHtmlIfNecessary(events))
      .catch(error => console.log('error', error));
  }

  async getAllEvents(entities) {
    if(!this.lastUpdate || moment().diff(this.lastUpdate, 'minutes') > 15) {
      const start = moment().startOf('day').format("YYYY-MM-DDTHH:mm:ss");
      const end = moment().startOf('day').add(7, 'days').format("YYYY-MM-DDTHH:mm:ss");

      let urls = entities.map(entity => `calendars/${entity}?start=${start}Z&end=${end}Z`);
      let allResults = await this.getAllUrls(urls)
      let events = [].concat
        .apply([], allResults)
        .map(x => this.toEvent(x));

      if(this.config.showProgressBar) {
        if(events.length > 0 && moment().format('DD') === moment(events[0].startDateTime).format('DD')) {
          let now = {startDateTime: moment().format(), type: 'now'}
          events.push(now);
        }
      }

      events.sort((a, b) => new Date(a.startDateTime) - new Date(b.startDateTime));
      
      let isSomethingChanged = this.isSomethingChanged(events);
      this.events = events;
      this.lastUpdate = moment();
      return { events: events, isSomethingChanged: isSomethingChanged };
    } else {
      return this.events;
    }
  }

  async getAllUrls(urls) {
    try {
      var data = await Promise.all(
        urls.map(
          url => this._hass.callApi('get', url)));
      return (data);
    } catch (error) {
      throw (error);
    }
  }

  updateHtmlIfNecessary(eventList) {
    if(eventList.isSomethingChanged) {
      this.content.innerHTML = `
        <style>
          .day-wrapper {
            border-bottom: 1px solid rgba(0,0,0,.12);
            margin-bottom: 10px;
          }

          .day-wrapper:last-child {
            border-bottom: none;
          }

          .day {
            display: flex;
            flex-direction: row;
            width: 100%;
          }

          .date {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: top;
            flex: 0 1 40px;
          }

          .events {
            flex: 1 1 auto;
          }

          .event-wrapper {
            padding: 5px;
            margin-left: 10px;
          }

          .event {
            flex: 0 1 auto;
            display: flex;
            flex-direction: column;
          }

          .info {
            display: flex;
            width: 100%;
            justify-content: space-between;
            flex-direction: row;
          }

          .congrats {
            cursor: pointer;
          }

          .time {
            font-size: smaller;
            color: rgba(var(--primary-color),.62);
          }

          .now {
            color: #03a9f4;
          }

          hr.now {
            border-style: solid;
            border-color: var(--primary-color);
            border-width: 1px 0 0 0;
            margin-top: -9px;
            margin-left: 5px;
          }

          ha-icon {
            color: var(--state-icon-color);
          }

          ha-icon.now {
            height: 16px;
            width: 16px;
          }

        </style>
      `;

      let events = eventList.events;
      let groupedEventsPerDay = this.groupBy(events, event => moment(event.startDateTime).format('YYYY-MM-DD'));

      groupedEventsPerDay.forEach((events, day) => {
        let eventStateCardContentElement = document.createElement('div');
        eventStateCardContentElement.classList.add('day-wrapper');
        eventStateCardContentElement.innerHTML = this.getDayHtml(day, events);
        this.content.append(eventStateCardContentElement);
      });
    }
  }

  getDayHtml(day, events) {
    let clazz = moment().format('DD') === moment(day).format('DD') ? 'date now' : 'date';
    return `
      <div class="day">
        <div class="${clazz}">
          <div>${moment(day).format('DD')}</div>
          <div>${moment(day).format('ddd')}</div>
        </div>
        <div class="events">${events.map(event => this.getEventHtml(event)).join('')}</div>
      </div>`;
  }

  getEventHtml(event) {
    if(event.type) {
        return `<ha-icon icon="mdi:circle" class="now"></ha-icon><hr class="now" />`;
    }
    //${event.summary.indexOf('birthday') > 0 ? `<div class="congrats"><i class="fas fa-gift"></i>&nbsp;Send congrats</div>` : ''}
    return `
      <div class="event-wrapper">
        <div class="event">
          <div class="info">
            <div class="summary">${event.title}</div>
            ${event.location ? `<div class="location"><ha-icon icon="mdi:map-marker"></ha-icon>&nbsp;${event.location}</div>` : ''}
            
          </div>
          <div class="time">${event.isFullDayEvent ? 'All day' : (moment(event.startDateTime).format('HH:mm') + `-` + moment(event.endDateTime).format('HH:mm'))}</div>
        </div>
      </div>`;
  }

  setConfig(config) {
    if (!config.entities) {
      throw new Error('You need to define at least one calendar entity via entities');
    }
    this.config = {
      name: 'Calendar',
      showProgressBar: true,
      ...config
    };
  }

  // The height of your card. Home Assistant uses this to automatically
  // distribute all cards over the available columns.
  getCardSize() {
    return 3;
  }

  toEvent(anEvent) {
    if(anEvent.htmlLink) {
      return new GoogleCalendarEvent(anEvent);
    }
    return new CalDavCalendarEvent(anEvent);
  }

  isSomethingChanged(events) {
    let isSomethingChanged = JSON.stringify(events) !== JSON.stringify(this.events);
    return isSomethingChanged;
  }

  deepClone(obj) {
    return JSON.parse(JSON.stringify(obj));
  }

  groupBy(list, keyGetter) {
    const map = new Map();
    list.forEach((item) => {
        const key = keyGetter(item);
        const collection = map.get(key);
        if (!collection) {
            map.set(key, [item]);
        } else {
            collection.push(item);
        }
    });
    return map;
  }
}

class GoogleCalendarEvent {
  constructor(googleCalendarEvent) {
    this.googleCalendarEvent = googleCalendarEvent;
  }

  get startDateTime() {
    if (this.googleCalendarEvent.start.date) {
      let dateTime = moment(this.googleCalendarEvent.start.date);
      return dateTime.toISOString();
    }
    return this.googleCalendarEvent.start.dateTime;
  }

  get endDateTime() {
    return this.googleCalendarEvent.end.dateTime;
  }

  get title() {
    return this.googleCalendarEvent.summary;
  }

  get description() {
    return this.googleCalendarEvent.description;
  }

  get location() {
    if(this.googleCalendarEvent.location) {
      return this.googleCalendarEvent.location.split(',')[0]
    }
    return undefined;
  }

  get isFullDayEvent() {
    return this.googleCalendarEvent.start.date;
  }
}

class CalDavCalendarEvent {
  constructor(calDavCalendarEvent) {
    this.calDavCalendarEvent = calDavCalendarEvent;
  }

  get startDateTime() {
    return this.calDavCalendarEvent.start;
  }

  get endDateTime() {
    return this.calDavCalendarEvent.end;
  }

  get title() {
    return this.calDavCalendarEvent.title;
  }

  get description() {
    return this.calDavCalendarEvent.description;
  }

  get location() {
    if(this.calDavCalendarEvent.location) {
      return this.calDavCalendarEvent.location;
    }
    return undefined;
  }

  get isFullDayEvent() {
    let start = moment(this.startDateTime);
    let end = moment(this.endDateTime);
    let diffInHours = end.diff(start, 'hours');
    return diffInHours >= 24;
  }
}

customElements.define('calendar-card', CalendarCard);