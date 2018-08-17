class AlarmControlPanelCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._stateStrings = {
      'arm_away': 'Arm away',
      'arm_custom_bypass': 'Custom',
      'arm_home': 'Arm home',
      'arming': 'Arming',
      'arm_night': 'Arm night',
      'armed_away': 'Armed away',
      'armed_custom_bypass': 'Armed custom',
      'armed_home': 'Armed home',
      'armed_night': 'Armed night',
      'disarm': 'Disarm',
      'disarmed': 'Disarmed',
      'pending': 'Pending',
      'triggered': 'Triggered',
    }
    this._icons = {
      'armed_away': 'mdi:security-lock',
      'armed_custom_bypass': 'mdi:security',
      'armed_home': 'mdi:security-home',
      'armed_night': 'mdi:security-home',
      'disarmed': 'mdi:verified',
      'pending': 'mdi:shield-outline',
      'triggered': 'hass:bell-ring',
    }
  }

  set hass(hass) {
    this.myhass = hass;
    const entity = hass.states[this._config.entity];
    if (entity && entity.state != this._state) {
      this._state = entity.state;
      this._updateCardContent(entity);
    }
  }

  setConfig(config) {
    if (!config.entity || config.entity.split(".")[0] !== "alarm_control_panel") {
      throw new Error('Please specify an entity from alarm_control_panel domain.');
    }
    if (config.auto_enter) {
      if (!config.auto_enter.code_length || !config.auto_enter.arm_action) {
        throw new
          Error('Specify both code_length and arm_action when using auto_enter.');
      }
      this._arm_action = config.auto_enter.arm_action;
    }

    const root = this.shadowRoot;
    if (root.lastChild) root.removeChild(root.lastChild);
    if (!config.states) config.states = ['arm_home', 'arm_away'];
    if (!config.scale) config.scale = '15px';

    this._card = document.createElement('ha-card');
    const content = document.createElement('div');
    content.id = "content";
    this._config = Object.assign({}, config);
    this._card.appendChild(this._style(config.style));
    this._card.appendChild(content);
    root.appendChild(this._card);
    this._config = Object.assign({}, config);
  }

  _updateCardContent(entity) {
    const root = this.shadowRoot;
    const card = root.lastChild;
    const config = this._config;

    if (!config.title) {
      card.header = this._stateToText(this._state);
    } else {
      card.header = config.title;
    }

    root.getElementById("content").innerHTML = `
      ${this._icon()}
      ${config.title ? `<div class='state ${this._state}'>
        ${this._stateToText(this._state)}</div>` : ''}
      ${this._actionButtons()}
      ${entity.attributes.code_format ? '<paper-input label="Alarm code" type="password"></paper-input>' : ''}
      ${this._keypad(entity)}
    `;

    this._setupActions();
    this._setupInput();
    this._setupKeypad();
  }

  _icon() {
    return `<ha-icon icon='${this._stateToIcon(this._state)}'
      class='${this._state}'></ha-icon>`
  }

  _actionButtons() {
    const armVisible = (this._state === 'disarmed');
    return `
      <div class="actions">
        ${armVisible
        ? `${this._config.states.map(el => `${this._actionButton(el)}`).join('')}`
        : `${this._actionButton('disarm')}`}
      </div>`
  }

  _actionButton(state) {
    return `<paper-button noink raised id="${state}">${this._stateToText(state)}
      </paper-button>`;
  }

  _setupActions() {
    // TODO: fix memory leak for reattaching handlers every time
    // Need a way to avoid doing innerHTML, at least without detaching handlers first
    const card = this.shadowRoot.lastChild;
    const config = this._config;

    if (config.auto_enter) {
      card.querySelectorAll(".actions paper-button").forEach(element => {
        element.classList.remove('autoarm');
        if (element.id === this._arm_action || element.id === 'disarm') {
          element.classList.add('autoarm');
        }
        element.addEventListener('click', event => {
          card.querySelectorAll(".actions paper-button").forEach(element => {
            element.classList.remove('autoarm');
          })
          element.classList.add('autoarm');
          if (element.id !== 'disarm') this._arm_action = element.id;
        })
      })
    } else {
      card.querySelectorAll(".actions paper-button").forEach(element => {
        element.addEventListener('click', event => {
          const input = card.querySelector('paper-input');
          const value = input ? input.value : '';
          this._callService(element.id, value);
        })
      })
    }
  }

  _callService(service, code) {
    const input = this.shadowRoot.lastChild.querySelector("paper-input");
    this.myhass.callService('alarm_control_panel', `alarm_${service}`, {
      entity_id: this._config.entity,
      code: code,
    });
    if (input) input.value = '';
  }

  _setupInput() {
    if (this._config.auto_enter) {
      const input = this.shadowRoot.lastChild.querySelector("paper-input");
      input.addEventListener('input', event => { this._autoEnter() })
    }
  }

  _setupKeypad() {
    const root = this.shadowRoot;

    const input = root.lastChild.querySelector('paper-input');
    root.querySelectorAll(".pad paper-button").forEach(element => {
      if (element.getAttribute('value') === 'Clear') {
        element.addEventListener('click', event => {
          input.value = '';
        })
      } else {
        element.addEventListener('click', event => {
          input.value += element.getAttribute('value');
          this._autoEnter();
        })
      }
    });
  }

  _autoEnter() {
    const config = this._config;

    if (config.auto_enter) {
      const card = this.shadowRoot.lastChild;
      const code = card.querySelector("paper-input").value;
      if (code.length == config.auto_enter.code_length) {
        const service = card.querySelector(".actions .autoarm").id;
        this._callService(service, code);
      }
    }
  }

  _keypad(entity) {
    if (this._config.hide_keypad || !entity.attributes.code_format) return '';

    return `
      <div class="pad">
        <div>
          ${this._keypadButton("1", "")}
          ${this._keypadButton("4", "GHI")}
          ${this._keypadButton("7", "PQRS")}
        </div>
        <div>
          ${this._keypadButton("2", "ABC")}
          ${this._keypadButton("5", "JKL")}
          ${this._keypadButton("8", "TUV")}
          ${this._keypadButton("0", "")}
        </div>
        <div>
          ${this._keypadButton("3", "DEF")}
          ${this._keypadButton("6", "MNO")}
          ${this._keypadButton("9", "WXYZ")}
          ${this._keypadButton("Clear", "")}
        </div>
      </div>`
  }

  _keypadButton(button, alpha) {
    let letterHTML = '';
    if (this._config.display_letters) {
      letterHTML = `<div class='alpha'>${alpha}</div>`
    }
    return `<paper-button noink raised value="${button}">${button}${letterHTML}
      </paper-button>`;
  }

  _style(icon_style) {
    const style = document.createElement('style');
    style.textContent = `
      ha-card {
        padding-bottom: 16px;
        position: relative;
        --alarm-color-disarmed: var(--label-badge-green);
        --alarm-color-pending: var(--label-badge-yellow);
        --alarm-color-triggered: var(--label-badge-red);
        --alarm-color-armed: var(--label-badge-red);
        --alarm-color-autoarm: rgba(0, 153, 255, .1);
        --alarm-state-color: var(--alarm-color-armed);
        --base-unit: ${this._config.scale};
        font-size: calc(var(--base-unit));
        ${icon_style}
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
        --alarm-state-color: var(--alarm-color-disarmed);
      }
      .triggered {
        --alarm-state-color: var(--alarm-color-triggered);
        animation: pulse 1s infinite;
      }
      .arming {
        --alarm-state-color: var(--alarm-color-pending);
        animation: pulse 1s infinite;
      }
      .pending {
        --alarm-state-color: var(--alarm-color-pending);
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
        font-size: calc(var(--base-unit));
      }
      .state {
        margin-left: 20px;
        font-size: calc(var(--base-unit) * 0.9);
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
        margin-bottom: 10%;
        position: relative;
        padding: calc(var(--base-unit));
        font-size: calc(var(--base-unit) * 1.1);
      }
      .actions {
        margin: 0 8px;
        display: flex;
        justify-content: center;
        font-size: calc(var(--base-unit) * 1);
      }
      .actions paper-button {
        min-width: calc(var(--base-unit) * 9);
        color: var(--primary-color);
      }
      .actions .autoarm {
        background: var(--alarm-color-autoarm);
      }
      paper-button#disarm {
        color: var(--google-red-500);
      }
      .alpha {
        position: absolute;
        text-align: center;
        bottom: calc(var(--base-unit) * 0.1);
        color: var(--secondary-text-color);
        font-size: calc(var(--base-unit) * 0.7);
      }
    `;
    return style;
  }

  _stateToIcon(state) {
    return this._icons[state] || 'mdi:shield-outline'
  }

  _stateToText(state) {
    return this._stateStrings[state] || 'Unknown'
  }

  getCardSize() {
    return 1;
  }
}

customElements.define('alarm_control_panel-card', AlarmControlPanelCard);