customElements.whenDefined('card-tools').then(() => {
class AutoEntities extends cardTools.litElement() {

  setConfig(config) {
    if(!config || !config.card)
      throw new Error("Invalid configuration");

    this._config = config;
    this.data = {};

    this.entities = this.get_entities() || [];
    this.card = cardTools.createCard(Object.assign({entities: this.entities}, config.card));
  }


  match(pattern, str){
    if (typeof(str) === "string" && typeof(pattern) === "string") {
      if((pattern.startsWith('/') && pattern.endsWith('/')) || pattern.indexOf('*') !== -1) {
        if(pattern[0] !== '/')
          pattern = `/${pattern.replace(/\*/g, '.*')}/`;
        var regex = new RegExp(pattern.substr(1).slice(0,-1));
        return regex.test(str);
      }
    }
    if(typeof(pattern) === "string") {
      if(pattern.indexOf(":") !== -1 && typeof(str) === "object") {
        while(pattern.indexOf(":") !== -1)
        {
          str = str[pattern.split(":")[0]];
          pattern = pattern.substr(pattern.indexOf(":")+1, pattern.length);
        }
      }
      if(pattern.startsWith("<=")) return parseFloat(str) <= parseFloat(pattern.substr(2));
      if(pattern.startsWith(">=")) return parseFloat(str) >= parseFloat(pattern.substr(2));
      if(pattern.startsWith("<")) return parseFloat(str) < parseFloat(pattern.substr(1));
      if(pattern.startsWith(">")) return parseFloat(str) > parseFloat(pattern.substr(1));
      if(pattern.startsWith("!")) return parseFloat(str) != parseFloat(pattern.substr(1));
      if(pattern.startsWith("=")) return parseFloat(str) == parseFloat(pattern.substr(1));
    }
    return str === pattern;
  }

  match_filter(hass, entities, filter) {
    let retval = [];
    let count = -1;
    entities.forEach((i) => {
      count++;
      if(!hass.states) return;
      const e = (typeof(i) === "string")?hass.states[i]:hass.states[i.entity];
      if(!e) return;

      let unmatched = false;
      Object.keys(filter).forEach((filterKey) => {
        const key = filterKey.split(" ")[0];
        const value = filter[filterKey];
        switch(key) {
          case "options":
            break;
          case "domain":
            if(!this.match(value, e.entity_id.split('.')[0]))
              unmatched = true;
            break;
          case "state":
            if(!this.match(value, e.state))
              unmatched = true;
            break;
          case "entity_id":
            if(!this.match(value, e.entity_id))
              unmatched = true;
            break;
          case "name":
            if(!e.attributes.friendly_name
              || !this.match(value, e.attributes.friendly_name)
            )
              unmatched = true;
            break;
          case "area":
            let found = false;
            this.data.areas.forEach((a) => {
              if(found) return;
              if(this.match(value, a.name)) {
                this.data.devices.forEach((d) => {
                  if(found) return;
                  if(d.area_id && d.area_id === a.area_id) {
                    this.data.entities.forEach((en) => {
                      if(found) return;
                      if(en.device_id === d.id && en.entity_id === e.entity_id) {
                        found = true;
                      }
                    });
                  }
                });
              }
            });
            if(!found) unmatched = true;
            break;
          case "group":
            if(!value.startsWith("group.")
              || !hass.states[value]
              || !hass.states[value].attributes.entity_id
              || !hass.states[value].attributes.entity_id.includes(e.entity_id)
            )
              unmatched = true;
            break;
          case "attributes":
            Object.keys(value).forEach((entityKey) => {
              const k = entityKey.split(" ")[0];
              const v = value[entityKey];
              if(!e.attributes[k]
                || !this.match(v, e.attributes[k])
              )
                unmatched = true;
            });
            break;
          default:
            unmatched = true;
        }
      });
      if(!unmatched) retval.push(count);
    });
    return retval;
  }

  get_entities()
  {
    let entities = [];
    if(this._config.entities)
      this._config.entities.forEach((e) => entities.push(e));

    if(this._hass && this._config.filter) {

      if(this._config.filter.include){
        this._config.filter.include.forEach((f) => {
          const add = this.match_filter(this._hass, Object.keys(this._hass.states), f);
          let toAdd = [];
          add.forEach((i) => {
            toAdd.push(Object.assign({entity: Object.keys(this._hass.states)[i]}, f.options));
          });
          toAdd.sort((a,b) => {
            if (a.entity < b.entity) return -1;
            if (a.entity > b.entity) return 1;
            return 0;
          });
          toAdd.forEach((i) => entities.push(i));
        });
      }

      if(this._config.filter.exclude) {
        this._config.filter.exclude.forEach((f) => {
          const remove = this.match_filter(this._hass, entities, f);
          for(var i = remove.length-1; i >= 0; i--)
          {
            entities.splice(remove[i],1);
          }
        });
      }
    }
    return entities;
  }

  createRenderRoot() {
    return this;
  }
  render() {
    if(this.entities.length === 0 && this._config.show_empty === false)
      return cardTools.litHtml()``;
    return cardTools.litHtml()`
      <div id="root">${this.card}</div>
    `;
  }

  async get_data(hass) {
    try {
    this.data.areas = await hass.callWS({type: "config/area_registry/list"});
    this.data.devices = await hass.callWS({type: "config/device_registry/list"});
    this.data.entities = await hass.callWS({type: "config/entity_registry/list"});
    } catch (err) {
    }
  }

  _compare_arrays(a,b) {
    if(a === b) return true;
    if(a == null || b == null) return false;
    if(a.length != b.length) return false;
    for(var i = 0; i < a.length; i++) {
      if(a[i] !== b[i]) {
        return false;
      }
    }
    return true;
  }

  set hass(hass) {
    this._hass = hass;
    this.get_data(hass).then(() => {
      if(this.card)
      {
        this.card.hass = this._hass;
      }

      const oldEntities = this.entities.map((e) => e.entity);
      this.entities = this.get_entities() || [];
      const newEntities = this.entities.map((e) => e.entity);

      if(!this._compare_arrays(oldEntities, newEntities)) {
        this.card.setConfig(Object.assign({entities: this.entities}, this._config.card));
        this.requestUpdate();
      }
    });
  }

}

customElements.define('auto-entities', AutoEntities);
});

window.setTimeout(() => {
  if(customElements.get('card-tools')) return;
  customElements.define('auto-entities', class extends HTMLElement{
    setConfig() { throw new Error("Can't find card-tools. See https://github.com/thomasloven/lovelace-card-tools");}
  });
}, 2000);
