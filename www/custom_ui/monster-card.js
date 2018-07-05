const _filterEntityId = function (stateObj, pattern) {
  if (pattern.indexOf('*') === -1) {
    return stateObj.entity_id === pattern;
  }
  const regEx = new RegExp(`^${pattern.replace(/\*/g, '.*')}$`);
  return stateObj.entity_id.search(regEx) === 0;
}

const computeDomain = function (entityId) {
  return entityId.substr(0, entityId.indexOf('.'));
}

const computeStateDomain = function (stateObj) {
  if (!stateObj._domain) {
    stateObj._domain = computeDomain(stateObj.entity_id);
  }
  return stateObj._domain;
}

const _getEntities = function (hass, filters) {
  const entities = new Set();
  filters.forEach((filter) => {
    const filters = [];
    if (filter.domain) {
      filters.push(stateObj => computeStateDomain(stateObj) === filter.domain);
    }
    if (filter.entity_id) {
      filters.push(stateObj => _filterEntityId(stateObj, filter.entity_id));
    }
    if (filter.state) {
      filters.push(stateObj => stateObj.state === filter.state);
    }

    Object.values(hass.states).forEach((stateObj) => {
      if (filters.every(filterFunc => filterFunc(stateObj))) {
        entities.add(stateObj.entity_id);
      }
    });
  });
  return Array.from(entities);
}

class MonsterCard extends HTMLElement {

  set hass(hass) {
    if (!this.card) {
      this.card = document.createElement(`hui-${this.config.card}-card`);
      this.appendChild(this.card);
    }

    let entitiesList = _getEntities(hass, this.config.filter.include);
    if (this.config.filter.exclude) {
      const excludeEntities = _getEntities(hass, this.config.filter.exclude);
      entitiesList = entitiesList.filter(el => !excludeEntities.includes(el));
    }
    entitiesList = entitiesList.sort();

    this.card.hass = hass;
    const options = {
      title: this.config.title,
      entities: entitiesList,
    }
    this.card.setConfig(options);
  }

  setConfig(config) {
    if (!config.filter.include || !Array.isArray(config.filter.include)) {
      throw new Error('Please define filters');
    }
    if (!config.card || !['glance', 'entities'].includes(config.card)) {
      config.card = 'entities';
    }

    this.config = config;
  }
  getCardSize() {
    return 1;
  }
}

customElements.define('monster-card', MonsterCard);