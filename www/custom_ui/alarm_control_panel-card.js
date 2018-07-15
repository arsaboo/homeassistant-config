class AlarmControlPanelCard extends HTMLElement {
  constructor() {
    super();
    this._armedStates = ['armed_home', 'armed_away', 'armed_night', 'armed_custom_bypass'];
    this.attachShadow({ mode: 'open' });
    this._enteredCode = '';
  }

  setConfig(config) {
    if (!config.entity && config.entity.split(".")[0] != "alarm_control_panel") {
      throw new Error('Please specify an entity from alarm_control_panel domain.');
    }
    const root = this.shadowRoot;
    if (root.lastChild) root.removeChild(root.lastChild);
    const cardConfig = Object.assign({}, config);
    if (!cardConfig.states) cardConfig.states = ['arm_home', 'arm_away'];
    const card = document.createElement('ha-card');
    card.header = config.title;
    const content = document.createElement('div');
    const style = document.createElement('style');
    style.textContent = `
      ha-card {
        padding-bottom: 16px;
        position: relative;
        --alarm-state-color: var(--label-badge-green)
      }
      ha-icon {
        color: var(--alarm-state-color);
        position: absolute;
        right: 20px;
        top: 20px;
        padding: 10px;
        border: 2px solid var(--alarm-state-color);
        border-radius: 50%;
      }
      .disarmed {
        --alarm-state-color: var(--label-badge-red);
      }
      .pending {
        --alarm-state-color: var(--label-badge-yellow);
        animation: pulse 1s infinite;
      }
      @keyframes pulse {
        0% {
          border: 2px solid var(--alarm-state-color);
        }
        100% {
          border: 2px solid rgba(255, 153, 0, 0.3);
        }
      }
      paper-input {
        margin: auto;
        max-width: 200px;
      }
      .state {
        margin-left: 20px;
        position: relative;
        bottom: 16px;
        color: var(--alarm-state-color);
        animation: none;
      }
      .pad {
        display: flex;
        justify-content: center;
      }
      .pad div {
        display: flex;
        flex-direction: column;
      }
      .pad paper-button {
        width: 80px;
        margin-bottom: 8px;
      }
      .actions {
        margin: 0 8px;
        display: flex;
        justify-content: center;
      }
      .actions paper-button {
        min-width: 115px;
        color: var(--primary-color);
      }
      paper-button#disarm {
        color: var(--google-red-500);
      }
    `;
    content.id = "content";
    card.appendChild(style);
    card.appendChild(content);
    root.appendChild(card)
    this._config = cardConfig;
  }

  set hass(hass) {
    const config = this._config;
    this.myhass = hass;
    const entity = hass.states[config.entity];
    if (entity.state != this._state) {
      this._updateCardContent(entity);
      this._state = entity.state;
    }
  }

  _updateCardContent(entity) {
    const root = this.shadowRoot;
    const card = root.lastChild;
    const config = this._config;
    const _armVisible = entity.state === 'disarmed';
    const _disarmVisible = (this._armedStates.includes(entity.state) || entity.state === 'pending' || entity.state === 'triggered');
    if (!config.title) {
      card.header = this._translateState(entity.state);
    }
    const content = `
      <ha-icon icon='${this._getIcon(entity.state)}' class='${entity.state}'></ha-icon>
      ${config.title ? `<div class='state ${entity.state}'>${this._translateState(entity.state)}</div>` : ''}
      <div class="actions">
        ${_disarmVisible ? `
          ${this._generateButton('disarm')}
        `: ''}
        ${_armVisible ? `
        ${config.states.map(el => `${this._generateButton(el)}`).join('')}
        `: ''}
      </div>
      ${entity.attributes.code_format ? `
        <paper-input label="Alarm code" type="password"></paper-input>
      `: ''}
      ${entity.attributes.code_format == 'Number' ? `
          <div class="pad">
            <div>
              <paper-button data-digit="1" raised>1</paper-button>
              <paper-button data-digit="4" raised>4</paper-button>
              <paper-button data-digit="7" raised>7</paper-button>
            </div>
            <div>
              <paper-button data-digit="2" raised>2</paper-button>
              <paper-button data-digit="5" raised>5</paper-button>
              <paper-button data-digit="8" raised>8</paper-button>
              <paper-button data-digit="0" raised>0</paper-button>
            </div>
            <div>
              <paper-button data-digit="3" raised>3</paper-button>
              <paper-button data-digit="6" raised>6</paper-button>
              <paper-button data-digit="9" raised>9</paper-button>
              <paper-button raised id='clear'>Clear</paper-button>
            </div>
          </div>
      `: ''}
    `;
    root.getElementById("content").innerHTML = content;
    this._bindService('disarm');
    config.states.forEach(state => this._bindService(state));

    if (entity.attributes.code_format) {
      root.lastChild.querySelectorAll('.actions paper-button').forEach(elem => {
        elem.setAttribute('disabled', true);
      });
    }

    const input = root.querySelector("paper-input");
    if (input) {
      input.addEventListener('keypress', event => {
        this._enteredCode = root.lastChild.querySelector('paper-input').value;
        root.lastChild.querySelectorAll('.actions paper-button').forEach(elem => {
          elem.removeAttribute('disabled');
        });
      })
    }

    root.querySelectorAll(".pad paper-button").forEach(el => {
      el.addEventListener('click', event => {
        if (event.target.id == 'clear') {
          root.lastChild.querySelector('paper-input').value = '';
          this._enteredCode = '';
        } else {
          this._enteredCode += event.target.getAttribute('data-digit');
          root.lastChild.querySelector('paper-input').value = this._enteredCode;
          root.lastChild.querySelectorAll('.actions paper-button').forEach(elem => {
            elem.removeAttribute('disabled');
          });
        }
      })
    });

  }

  _bindService(button) {
    const card = this.shadowRoot.lastChild;
    const config = this._config;
    const entity = this.myhass.states[config.entity];
    const dom_button = card.querySelector(`#${button}`);
    if (dom_button) {
      dom_button.addEventListener('click', event => {
        if (entity.attributes.code_format) {
          this._enteredCode = card.querySelector('paper-input').value;
        }
        this.myhass.callService('alarm_control_panel', `alarm_${button}`, {
          entity_id: config.entity,
          code: this._enteredCode,
        });
        this._enteredCode = '';
      });
    }
  }

  _getIcon(state) {
    switch (state) {
      case 'disarmed':
        return 'mdi:security-close'
      case 'armed_home':
        return 'mdi:security-home'
      case 'pending':
        return 'mdi:shield-outline'
      case 'armed_away':
        return 'mdi:security-lock'
      case 'triggered':
        return 'hass:bell-ring'
      case 'armed_custom_bypass':
        return 'mdi:security'
      case 'armed_night':
        return 'mdi:security-home'
    }
    return 'mdi:shield-outline'
  }

  _translateState(state) {
    switch (state) {
      case 'disarmed':
        return 'Disarmed'
      case 'armed_home':
        return 'Armed home'
      case 'pending':
        return 'Pending'
      case 'triggered':
        return 'Triggered'
      case 'armed_away':
        return 'Armed away'
      case 'armed_night':
        return 'Armed night'
      case 'armed_custom_bypass':
        return 'Armed custom'
      case 'disarm':
        return 'Disarm'
      case 'arm_home':
        return 'Arm home'
      case 'arm_away':
        return 'Arm away'
      case 'arm_night':
        return 'Arm night'
      case 'arm_custom_bypass':
        return 'Custom'
    }
    return 'Unknown'
  }

  _generateButton(state) {
    return `<paper-button raised id="${state}">${this._translateState(state)}</paper-button>`;
  }

  getCardSize() {
    return 1;
  }
}
customElements.define('alarm_control_panel-card', AlarmControlPanelCard);