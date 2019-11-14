!function(t){var e={};function n(i){if(e[i])return e[i].exports;var s=e[i]={i:i,l:!1,exports:{}};return t[i].call(s.exports,s,s.exports,n),s.l=!0,s.exports}n.m=t,n.c=e,n.d=function(t,e,i){n.o(t,e)||Object.defineProperty(t,e,{enumerable:!0,get:i})},n.r=function(t){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(t,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(t,"__esModule",{value:!0})},n.t=function(t,e){if(1&e&&(t=n(t)),8&e)return t;if(4&e&&"object"==typeof t&&t&&t.__esModule)return t;var i=Object.create(null);if(n.r(i),Object.defineProperty(i,"default",{enumerable:!0,value:t}),2&e&&"string"!=typeof t)for(var s in t)n.d(i,s,function(e){return t[e]}.bind(null,s));return i},n.n=function(t){var e=t&&t.__esModule?function(){return t.default}:function(){return t};return n.d(e,"a",e),e},n.o=function(t,e){return Object.prototype.hasOwnProperty.call(t,e)},n.p="",n(n.s=0)}([function(t,e,n){"use strict";n.r(e);const i=customElements.get("home-assistant-main")?Object.getPrototypeOf(customElements.get("home-assistant-main")):Object.getPrototypeOf(customElements.get("hui-view")),s=i.prototype.html,o=i.prototype.css;const r="custom:";function a(t,e){const n=document.createElement("hui-error-card");return n.setConfig({type:"error",error:t,config:e}),n}function c(t,e){if(!e||"object"!=typeof e||!e.type)return a(`No ${t} type configured`,e);let n=e.type;if(n=n.startsWith(r)?n.substr(r.length):`hui-${n}-${t}`,customElements.get(n))return function(t,e){const n=document.createElement(t);try{n.setConfig(e)}catch(t){return a(t,e)}return n}(n,e);const i=a(`Custom element doesn't exist: ${n}.`,e);i.style.display="None";const s=setTimeout(()=>{i.style.display=""},2e3);return customElements.whenDefined(n).then(()=>{clearTimeout(s),function(t,e,n=null){if((t=new Event(t,{bubbles:!0,cancelable:!1,composed:!0})).detail=e||{},n)n.dispatchEvent(t);else{var i=document.querySelector("home-assistant");(i=(i=(i=(i=(i=(i=(i=(i=(i=(i=(i=i&&i.shadowRoot)&&i.querySelector("home-assistant-main"))&&i.shadowRoot)&&i.querySelector("app-drawer-layout partial-panel-resolver"))&&i.shadowRoot||i)&&i.querySelector("ha-panel-lovelace"))&&i.shadowRoot)&&i.querySelector("hui-root"))&&i.shadowRoot)&&i.querySelector("ha-app-layout #view"))&&i.firstElementChild)&&i.dispatchEvent(t)}}("ll-rebuild",{},i)}),i}function l(){return document.querySelector("home-assistant").hass}class u extends i{static get properties(){return{hass:{},config:{},noHass:{type:Boolean}}}setConfig(t){var e;this._config=t,this.el?this.el.setConfig(t):this.el=this.create(t),this._hass&&(this.el.hass=this._hass),this.noHass&&(e=this,document.querySelector("home-assistant").provideHass(e))}set config(t){this.setConfig(t)}set hass(t){this._hass=t,this.el&&(this.el.hass=t)}createRenderRoot(){return this}render(){return s`${this.el}`}}if(!customElements.get("card-maker")){class t extends u{create(t){return function(t){return c("card",t)}(t)}}customElements.define("card-maker",t)}if(!customElements.get("element-maker")){class t extends u{create(t){return function(t){return c("element",t)}(t)}}customElements.define("element-maker",t)}if(!customElements.get("entity-row-maker")){class t extends u{create(t){return function(t){const e=new Set(["call-service","divider","section","weblink"]);if(!t)return a("Invalid configuration given.",t);if("string"==typeof t&&(t={entity:t}),"object"!=typeof t||!t.entity&&!t.type)return a("Invalid configuration given.",t);const n=t.type||"default";if(e.has(n)||n.startsWith(r))return c("row",t);const i=t.entity.split(".",1)[0];return Object.assign(t,{type:{alert:"toggle",automation:"toggle",climate:"climate",cover:"cover",fan:"toggle",group:"group",input_boolean:"toggle",input_number:"input-number",input_select:"input-select",input_text:"input-text",light:"toggle",lock:"lock",media_player:"media-player",remote:"toggle",scene:"scene",script:"script",sensor:"sensor",timer:"timer",switch:"toggle",vacuum:"toggle",water_heater:"climate",input_datetime:"input-datetime"}[i]||"text"}),c("entity-row",t)}(t)}}customElements.define("entity-row-maker",t)}function d(t,e,n){t.forEach(t=>{if(!t)return;const i=e[function(){let t=0;for(let i=0;i<e.length;i++){if(e[i].length<n.min_height)return i;e[i].length<e[t].length&&(t=i)}return t}()];i.appendChild(t),i.length+=t.getCardSize?t.getCardSize():1})}customElements.define("layout-card",class extends i{static get properties(){return{hass:{},_config:{}}}async setConfig(t){this._config={min_height:5,column_width:300,max_width:t.column_width||"500px",min_columns:t.column_num||1,max_columns:100,...t},this.cards=[],this.columns=[]}async firstUpdated(){window.addEventListener("resize",()=>this.place_cards()),window.addEventListener("hass-open-menu",()=>setTimeout(()=>this.place_cards(),100)),window.addEventListener("hass-close-menu",()=>setTimeout(()=>this.place_cards(),100)),window.addEventListener("location-changed",()=>{""===location.hash&&setTimeout(()=>this.place_cards(),100)})}async updated(t){!this.cards.length&&(this._config.entities&&this._config.entities.length||this._config.cards&&this._config.cards.length)&&(this.cards=await this.build_cards(),this.place_cards()),t.has("hass")&&this.hass&&this.cards&&this.cards.forEach(t=>{t&&(t.hass=this.hass)})}async build_card(t){if("break"===t)return null;const e=document.createElement("card-maker");return e.config={...t,...this._config.card_options},e.hass=l(),this.shadowRoot.querySelector("#staging").appendChild(e),new Promise((t,n)=>e.updateComplete.then(()=>t(e)))}async build_cards(){const t=this.shadowRoot.querySelector("#staging");for(;t.lastChild;)t.removeChild(t.lastChild);return Promise.all((this._config.entities||this._config.cards).map(t=>this.build_card(t)))}place_cards(){const t=this.shadowRoot.querySelector("#columns").clientWidth;this.columns=function(t,e,n){const i=t=>"string"==typeof t&&t.endsWith("%")?Math.floor(e*parseInt(t)/100):parseInt(t);let s=0;if("object"==typeof n.column_width){let t=e;for(;t>0;){let e=n.column_width[s];void 0===e&&(e=n.column_width.slice(-1)[0]),t-=i(e),s+=1}s=Math.max(s-1,1)}else s=Math.floor(e/i(n.column_width));s=Math.max(s,n.min_columns),s=Math.min(s,n.max_columns);let o=[];for(let t=0;t<s;t++){const t=document.createElement("div");t.classList.add("column"),t.length=0,o.push(t)}switch(n.layout){case"horizontal":!function(t,e,n){let i=0;t.forEach(t=>{if(i+=1,!t)return;const n=e[(i-1)%e.length];n.appendChild(t),n.length+=t.getCardSize?t.getCardSize():1})}(t,o);break;case"vertical":!function(t,e,n){let i=0;t.forEach(t=>{if(!t)return void(i+=1);const n=e[i%e.length];n.appendChild(t),n.length+=t.getCardSize?t.getCardSize():1})}(t,o);break;case"auto":default:d(t,o,n)}return o=o.filter(t=>t.childElementCount>0)}(this.cards,t,this._config),this.format_columns(),this.requestUpdate()}format_columns(){const t=(t,e,n,i="px")=>{if(void 0===this._config[e])return"";let s=`${t}: `;const o=this._config[e];return"object"==typeof o?o.length>n?s+=`${o[n]}`:s+=`${o.slice(-1)}`:s+=`${o}`,s.endsWith("px")||s.endsWith("%")||(s+=i),s+";"};for(const[e,n]of this.columns.entries()){const i=[t("max-width","max_width",e),t("min-width","min_width",e),t("width","column_width",e),t("flex-grow","flex_grow",e,"")];n.style.cssText="".concat(...i)}}getCardSize(){if(this.columns)return Math.max.apply(Math,this.columns.map(t=>t.length))}_isPanel(){if(this.isPanel)return!0;let t=this.parentElement,e=10;for(;e--;){if("hui-panel-view"===t.localName)return!0;if("div"===t.localName)return!1;t=t.parentElement}return!1}render(){return s`
      <div id="columns"
      class="
      ${this._config.rtl?"rtl":" "}
      ${this._isPanel()?"panel":" "}
      "
      style="
      ${this._config.justify_content?`justify-content: ${this._config.justify_content};`:""}
      ">
        ${this.columns.map(t=>s`
          ${t}
        `)}
      </div>
      <div id="staging"></div>
    `}static get styles(){return o`
      :host {
        padding: 0 4px;
        display: block;
        margin-bottom: 0!important;
      }

      #columns {
        display: flex;
        flex-direction: row;
        justify-content: center;
        margin-top: -8px;
      }
      #columns.rtl {
        flex-direction: row-reverse;
      }
      #columns.panel {
        margin-top: 0;
      }

      .column {
        flex-basis: 0;
        flex-grow: 1;
        overflow-x: hidden;
      }

      card-maker>* {
        display: block;
        margin: 4px 4px 8px;
      }
      card-maker:first-child>* {
        margin-top: 8px;
      }
      card-maker:last-child>* {
        margin-bottom: 4px;
      }

      #staging {
        visibility: hidden;
        height: 0;
      }
    `}get _cardModder(){return{target:this}}})}]);