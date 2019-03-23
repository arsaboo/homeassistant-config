!function(t,e){"object"==typeof exports&&"undefined"!=typeof module?module.exports=e():"function"==typeof define&&define.amd?define(e):(t=t||self).SimpleThermostat=e()}(this,function(){"use strict";const t=new WeakMap,e=e=>"function"==typeof e&&t.has(e),s=void 0!==window.customElements&&void 0!==window.customElements.polyfillWrapFlushCallback,i=(t,e,s=null)=>{let i=e;for(;i!==s;){const e=i.nextSibling;t.removeChild(i),i=e}},n={},r={},o=`{{lit-${String(Math.random()).slice(2)}}}`,a=`\x3c!--${o}--\x3e`,l=new RegExp(`${o}|${a}`),h="$lit$";class c{constructor(t,e){this.parts=[],this.element=e;let s=-1,i=0;const n=[],r=e=>{const a=e.content,c=document.createTreeWalker(a,133,null,!1);let d=0;for(;c.nextNode();){s++;const e=c.currentNode;if(1===e.nodeType){if(e.hasAttributes()){const n=e.attributes;let r=0;for(let t=0;t<n.length;t++)n[t].value.indexOf(o)>=0&&r++;for(;r-- >0;){const n=t.strings[i],r=u.exec(n)[2],o=r.toLowerCase()+h,a=e.getAttribute(o).split(l);this.parts.push({type:"attribute",index:s,name:r,strings:a}),e.removeAttribute(o),i+=a.length-1}}"TEMPLATE"===e.tagName&&r(e)}else if(3===e.nodeType){const t=e.data;if(t.indexOf(o)>=0){const r=e.parentNode,o=t.split(l),a=o.length-1;for(let t=0;t<a;t++)r.insertBefore(""===o[t]?p():document.createTextNode(o[t]),e),this.parts.push({type:"node",index:++s});""===o[a]?(r.insertBefore(p(),e),n.push(e)):e.data=o[a],i+=a}}else if(8===e.nodeType)if(e.data===o){const t=e.parentNode;null!==e.previousSibling&&s!==d||(s++,t.insertBefore(p(),e)),d=s,this.parts.push({type:"node",index:s}),null===e.nextSibling?e.data="":(n.push(e),s--),i++}else{let t=-1;for(;-1!==(t=e.data.indexOf(o,t+1));)this.parts.push({type:"node",index:-1})}}};r(e);for(const t of n)t.parentNode.removeChild(t)}}const d=t=>-1!==t.index,p=()=>document.createComment(""),u=/([ \x09\x0a\x0c\x0d])([^\0-\x1F\x7F-\x9F \x09\x0a\x0c\x0d"'>=\/]+)([ \x09\x0a\x0c\x0d]*=[ \x09\x0a\x0c\x0d]*(?:[^ \x09\x0a\x0c\x0d"'`<>=]*|"[^"]*|'[^']*))$/;class m{constructor(t,e,s){this._parts=[],this.template=t,this.processor=e,this.options=s}update(t){let e=0;for(const s of this._parts)void 0!==s&&s.setValue(t[e]),e++;for(const t of this._parts)void 0!==t&&t.commit()}_clone(){const t=s?this.template.element.content.cloneNode(!0):document.importNode(this.template.element.content,!0),e=this.template.parts;let i=0,n=0;const r=t=>{const s=document.createTreeWalker(t,133,null,!1);let o=s.nextNode();for(;i<e.length&&null!==o;){const t=e[i];if(d(t))if(n===t.index){if("node"===t.type){const t=this.processor.handleTextExpression(this.options);t.insertAfterNode(o.previousSibling),this._parts.push(t)}else this._parts.push(...this.processor.handleAttributeExpressions(o,t.name,t.strings,this.options));i++}else n++,"TEMPLATE"===o.nodeName&&r(o.content),o=s.nextNode();else this._parts.push(void 0),i++}};return r(t),s&&(document.adoptNode(t),customElements.upgrade(t)),t}}class f{constructor(t,e,s,i){this.strings=t,this.values=e,this.type=s,this.processor=i}getHTML(){const t=this.strings.length-1;let e="";for(let s=0;s<t;s++){const t=this.strings[s],i=u.exec(t);e+=i?t.substr(0,i.index)+i[1]+i[2]+h+i[3]+o:t+a}return e+this.strings[t]}getTemplateElement(){const t=document.createElement("template");return t.innerHTML=this.getHTML(),t}}const _=t=>null===t||!("object"==typeof t||"function"==typeof t);class g{constructor(t,e,s){this.dirty=!0,this.element=t,this.name=e,this.strings=s,this.parts=[];for(let t=0;t<s.length-1;t++)this.parts[t]=this._createPart()}_createPart(){return new y(this)}_getValue(){const t=this.strings,e=t.length-1;let s="";for(let i=0;i<e;i++){s+=t[i];const e=this.parts[i];if(void 0!==e){const t=e.value;if(null!=t&&(Array.isArray(t)||"string"!=typeof t&&t[Symbol.iterator]))for(const e of t)s+="string"==typeof e?e:String(e);else s+="string"==typeof t?t:String(t)}}return s+=t[e]}commit(){this.dirty&&(this.dirty=!1,this.element.setAttribute(this.name,this._getValue()))}}class y{constructor(t){this.value=void 0,this.committer=t}setValue(t){t===n||_(t)&&t===this.value||(this.value=t,e(t)||(this.committer.dirty=!0))}commit(){for(;e(this.value);){const t=this.value;this.value=n,t(this)}this.value!==n&&this.committer.commit()}}class v{constructor(t){this.value=void 0,this._pendingValue=void 0,this.options=t}appendInto(t){this.startNode=t.appendChild(p()),this.endNode=t.appendChild(p())}insertAfterNode(t){this.startNode=t,this.endNode=t.nextSibling}appendIntoPart(t){t._insert(this.startNode=p()),t._insert(this.endNode=p())}insertAfterPart(t){t._insert(this.startNode=p()),this.endNode=t.endNode,t.endNode=this.startNode}setValue(t){this._pendingValue=t}commit(){for(;e(this._pendingValue);){const t=this._pendingValue;this._pendingValue=n,t(this)}const t=this._pendingValue;t!==n&&(_(t)?t!==this.value&&this._commitText(t):t instanceof f?this._commitTemplateResult(t):t instanceof Node?this._commitNode(t):Array.isArray(t)||t[Symbol.iterator]?this._commitIterable(t):t===r?(this.value=r,this.clear()):this._commitText(t))}_insert(t){this.endNode.parentNode.insertBefore(t,this.endNode)}_commitNode(t){this.value!==t&&(this.clear(),this._insert(t),this.value=t)}_commitText(t){const e=this.startNode.nextSibling;t=null==t?"":t,e===this.endNode.previousSibling&&3===e.nodeType?e.data=t:this._commitNode(document.createTextNode("string"==typeof t?t:String(t))),this.value=t}_commitTemplateResult(t){const e=this.options.templateFactory(t);if(this.value instanceof m&&this.value.template===e)this.value.update(t.values);else{const s=new m(e,t.processor,this.options),i=s._clone();s.update(t.values),this._commitNode(i),this.value=s}}_commitIterable(t){Array.isArray(this.value)||(this.value=[],this.clear());const e=this.value;let s,i=0;for(const n of t)void 0===(s=e[i])&&(s=new v(this.options),e.push(s),0===i?s.appendIntoPart(this):s.insertAfterPart(e[i-1])),s.setValue(n),s.commit(),i++;i<e.length&&(e.length=i,this.clear(s&&s.endNode))}clear(t=this.startNode){i(this.startNode.parentNode,t.nextSibling,this.endNode)}}class b{constructor(t,e,s){if(this.value=void 0,this._pendingValue=void 0,2!==s.length||""!==s[0]||""!==s[1])throw new Error("Boolean attributes can only contain a single expression");this.element=t,this.name=e,this.strings=s}setValue(t){this._pendingValue=t}commit(){for(;e(this._pendingValue);){const t=this._pendingValue;this._pendingValue=n,t(this)}if(this._pendingValue===n)return;const t=!!this._pendingValue;this.value!==t&&(t?this.element.setAttribute(this.name,""):this.element.removeAttribute(this.name)),this.value=t,this._pendingValue=n}}class w extends g{constructor(t,e,s){super(t,e,s),this.single=2===s.length&&""===s[0]&&""===s[1]}_createPart(){return new S(this)}_getValue(){return this.single?this.parts[0].value:super._getValue()}commit(){this.dirty&&(this.dirty=!1,this.element[this.name]=this._getValue())}}class S extends y{}let x=!1;try{const t={get capture(){return x=!0,!1}};window.addEventListener("test",t,t),window.removeEventListener("test",t,t)}catch(t){}class P{constructor(t,e,s){this.value=void 0,this._pendingValue=void 0,this.element=t,this.eventName=e,this.eventContext=s,this._boundHandleEvent=(t=>this.handleEvent(t))}setValue(t){this._pendingValue=t}commit(){for(;e(this._pendingValue);){const t=this._pendingValue;this._pendingValue=n,t(this)}if(this._pendingValue===n)return;const t=this._pendingValue,s=this.value,i=null==t||null!=s&&(t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive),r=null!=t&&(null==s||i);i&&this.element.removeEventListener(this.eventName,this._boundHandleEvent,this._options),r&&(this._options=C(t),this.element.addEventListener(this.eventName,this._boundHandleEvent,this._options)),this.value=t,this._pendingValue=n}handleEvent(t){"function"==typeof this.value?this.value.call(this.eventContext||this.element,t):this.value.handleEvent(t)}}const C=t=>t&&(x?{capture:t.capture,passive:t.passive,once:t.once}:t.capture);const N=new class{handleAttributeExpressions(t,e,s,i){const n=e[0];return"."===n?new w(t,e.slice(1),s).parts:"@"===n?[new P(t,e.slice(1),i.eventContext)]:"?"===n?[new b(t,e.slice(1),s)]:new g(t,e,s).parts}handleTextExpression(t){return new v(t)}};function A(t){let e=T.get(t.type);void 0===e&&(e={stringsArray:new WeakMap,keyString:new Map},T.set(t.type,e));let s=e.stringsArray.get(t.strings);if(void 0!==s)return s;const i=t.strings.join(o);return void 0===(s=e.keyString.get(i))&&(s=new c(t,t.getTemplateElement()),e.keyString.set(i,s)),e.stringsArray.set(t.strings,s),s}const T=new Map,$=new WeakMap;(window.litHtmlVersions||(window.litHtmlVersions=[])).push("1.0.0");const z=(t,...e)=>new f(t,e,"html",N),E=133;function k(t,e){const{element:{content:s},parts:i}=t,n=document.createTreeWalker(s,E,null,!1);let r=O(i),o=i[r],a=-1,l=0;const h=[];let c=null;for(;n.nextNode();){a++;const t=n.currentNode;for(t.previousSibling===c&&(c=null),e.has(t)&&(h.push(t),null===c&&(c=t)),null!==c&&l++;void 0!==o&&o.index===a;)o.index=null!==c?-1:o.index-l,o=i[r=O(i,r)]}h.forEach(t=>t.parentNode.removeChild(t))}const V=t=>{let e=11===t.nodeType?0:1;const s=document.createTreeWalker(t,E,null,!1);for(;s.nextNode();)e++;return e},O=(t,e=-1)=>{for(let s=e+1;s<t.length;s++){const e=t[s];if(d(e))return s}return-1};const M=(t,e)=>`${t}--${e}`;let j=!0;void 0===window.ShadyCSS?j=!1:void 0===window.ShadyCSS.prepareTemplateDom&&(console.warn("Incompatible ShadyCSS version detected.Please update to at least @webcomponents/webcomponentsjs@2.0.2 and@webcomponents/shadycss@1.3.1."),j=!1);const R=t=>e=>{const s=M(e.type,t);let i=T.get(s);void 0===i&&(i={stringsArray:new WeakMap,keyString:new Map},T.set(s,i));let n=i.stringsArray.get(e.strings);if(void 0!==n)return n;const r=e.strings.join(o);if(void 0===(n=i.keyString.get(r))){const s=e.getTemplateElement();j&&window.ShadyCSS.prepareTemplateDom(s,t),n=new c(e,s),i.keyString.set(r,n)}return i.stringsArray.set(e.strings,n),n},U=["html","svg"],I=new Set,q=(t,e,s)=>{I.add(s);const i=t.querySelectorAll("style");if(0===i.length)return void window.ShadyCSS.prepareTemplateStyles(e.element,s);const n=document.createElement("style");for(let t=0;t<i.length;t++){const e=i[t];e.parentNode.removeChild(e),n.textContent+=e.textContent}if((t=>{U.forEach(e=>{const s=T.get(M(e,t));void 0!==s&&s.keyString.forEach(t=>{const{element:{content:e}}=t,s=new Set;Array.from(e.querySelectorAll("style")).forEach(t=>{s.add(t)}),k(t,s)})})})(s),function(t,e,s=null){const{element:{content:i},parts:n}=t;if(null==s)return void i.appendChild(e);const r=document.createTreeWalker(i,E,null,!1);let o=O(n),a=0,l=-1;for(;r.nextNode();)for(l++,r.currentNode===s&&(a=V(e),s.parentNode.insertBefore(e,s));-1!==o&&n[o].index===l;){if(a>0){for(;-1!==o;)n[o].index+=a,o=O(n,o);return}o=O(n,o)}}(e,n,e.element.content.firstChild),window.ShadyCSS.prepareTemplateStyles(e.element,s),window.ShadyCSS.nativeShadow){const s=e.element.content.querySelector("style");t.insertBefore(s.cloneNode(!0),t.firstChild)}else{e.element.content.insertBefore(n,e.element.content.firstChild);const t=new Set;t.add(n),k(e,t)}};window.JSCompiler_renameProperty=((t,e)=>t);const F={toAttribute(t,e){switch(e){case Boolean:return t?"":null;case Object:case Array:return null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){switch(e){case Boolean:return null!==t;case Number:return null===t?null:Number(t);case Object:case Array:return JSON.parse(t)}return t}},H=(t,e)=>e!==t&&(e==e||t==t),L={attribute:!0,type:String,converter:F,reflect:!1,hasChanged:H},B=Promise.resolve(!0),W=1,J=4,D=8,Y=16,G=32;class K extends HTMLElement{constructor(){super(),this._updateState=0,this._instanceProperties=void 0,this._updatePromise=B,this._hasConnectedResolver=void 0,this._changedProperties=new Map,this._reflectingProperties=void 0,this.initialize()}static get observedAttributes(){this.finalize();const t=[];return this._classProperties.forEach((e,s)=>{const i=this._attributeNameForProperty(s,e);void 0!==i&&(this._attributeToPropertyMap.set(i,s),t.push(i))}),t}static _ensureClassProperties(){if(!this.hasOwnProperty(JSCompiler_renameProperty("_classProperties",this))){this._classProperties=new Map;const t=Object.getPrototypeOf(this)._classProperties;void 0!==t&&t.forEach((t,e)=>this._classProperties.set(e,t))}}static createProperty(t,e=L){if(this._ensureClassProperties(),this._classProperties.set(t,e),e.noAccessor||this.prototype.hasOwnProperty(t))return;const s="symbol"==typeof t?Symbol():`__${t}`;Object.defineProperty(this.prototype,t,{get(){return this[s]},set(e){const i=this[t];this[s]=e,this.requestUpdate(t,i)},configurable:!0,enumerable:!0})}static finalize(){if(this.hasOwnProperty(JSCompiler_renameProperty("finalized",this))&&this.finalized)return;const t=Object.getPrototypeOf(this);if("function"==typeof t.finalize&&t.finalize(),this.finalized=!0,this._ensureClassProperties(),this._attributeToPropertyMap=new Map,this.hasOwnProperty(JSCompiler_renameProperty("properties",this))){const t=this.properties,e=[...Object.getOwnPropertyNames(t),..."function"==typeof Object.getOwnPropertySymbols?Object.getOwnPropertySymbols(t):[]];for(const s of e)this.createProperty(s,t[s])}}static _attributeNameForProperty(t,e){const s=e.attribute;return!1===s?void 0:"string"==typeof s?s:"string"==typeof t?t.toLowerCase():void 0}static _valueHasChanged(t,e,s=H){return s(t,e)}static _propertyValueFromAttribute(t,e){const s=e.type,i=e.converter||F,n="function"==typeof i?i:i.fromAttribute;return n?n(t,s):t}static _propertyValueToAttribute(t,e){if(void 0===e.reflect)return;const s=e.type,i=e.converter;return(i&&i.toAttribute||F.toAttribute)(t,s)}initialize(){this._saveInstanceProperties()}_saveInstanceProperties(){this.constructor._classProperties.forEach((t,e)=>{if(this.hasOwnProperty(e)){const t=this[e];delete this[e],this._instanceProperties||(this._instanceProperties=new Map),this._instanceProperties.set(e,t)}})}_applyInstanceProperties(){this._instanceProperties.forEach((t,e)=>this[e]=t),this._instanceProperties=void 0}connectedCallback(){this._updateState=this._updateState|G,this._hasConnectedResolver?(this._hasConnectedResolver(),this._hasConnectedResolver=void 0):this.requestUpdate()}disconnectedCallback(){}attributeChangedCallback(t,e,s){e!==s&&this._attributeToProperty(t,s)}_propertyToAttribute(t,e,s=L){const i=this.constructor,n=i._attributeNameForProperty(t,s);if(void 0!==n){const t=i._propertyValueToAttribute(e,s);if(void 0===t)return;this._updateState=this._updateState|D,null==t?this.removeAttribute(n):this.setAttribute(n,t),this._updateState=this._updateState&~D}}_attributeToProperty(t,e){if(this._updateState&D)return;const s=this.constructor,i=s._attributeToPropertyMap.get(t);if(void 0!==i){const t=s._classProperties.get(i)||L;this._updateState=this._updateState|Y,this[i]=s._propertyValueFromAttribute(e,t),this._updateState=this._updateState&~Y}}requestUpdate(t,e){let s=!0;if(void 0!==t&&!this._changedProperties.has(t)){const i=this.constructor,n=i._classProperties.get(t)||L;i._valueHasChanged(this[t],e,n.hasChanged)?(this._changedProperties.set(t,e),!0!==n.reflect||this._updateState&Y||(void 0===this._reflectingProperties&&(this._reflectingProperties=new Map),this._reflectingProperties.set(t,n))):s=!1}return!this._hasRequestedUpdate&&s&&this._enqueueUpdate(),this.updateComplete}async _enqueueUpdate(){let t;this._updateState=this._updateState|J;const e=this._updatePromise;this._updatePromise=new Promise(e=>t=e),await e,this._hasConnected||await new Promise(t=>this._hasConnectedResolver=t);const s=this.performUpdate();null!=s&&"function"==typeof s.then&&await s,t(!this._hasRequestedUpdate)}get _hasConnected(){return this._updateState&G}get _hasRequestedUpdate(){return this._updateState&J}get hasUpdated(){return this._updateState&W}performUpdate(){if(this._instanceProperties&&this._applyInstanceProperties(),this.shouldUpdate(this._changedProperties)){const t=this._changedProperties;this.update(t),this._markUpdated(),this._updateState&W||(this._updateState=this._updateState|W,this.firstUpdated(t)),this.updated(t)}else this._markUpdated()}_markUpdated(){this._changedProperties=new Map,this._updateState=this._updateState&~J}get updateComplete(){return this._updatePromise}shouldUpdate(t){return!0}update(t){void 0!==this._reflectingProperties&&this._reflectingProperties.size>0&&(this._reflectingProperties.forEach((t,e)=>this._propertyToAttribute(e,this[e],t)),this._reflectingProperties=void 0)}updated(t){}firstUpdated(t){}}K.finalized=!0;const Q="adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype;(window.litElementVersions||(window.litElementVersions=[])).push("2.0.1");const X=t=>t.flat?t.flat(1/0):function t(e,s=[]){for(let i=0,n=e.length;i<n;i++){const n=e[i];Array.isArray(n)?t(n,s):s.push(n)}return s}(t);class Z extends K{static finalize(){super.finalize(),this._styles=this.hasOwnProperty(JSCompiler_renameProperty("styles",this))?this._getUniqueStyles():this._styles||[]}static _getUniqueStyles(){const t=this.styles,e=[];if(Array.isArray(t)){X(t).reduceRight((t,e)=>(t.add(e),t),new Set).forEach(t=>e.unshift(t))}else t&&e.push(t);return e}initialize(){super.initialize(),this.renderRoot=this.createRenderRoot(),window.ShadowRoot&&this.renderRoot instanceof window.ShadowRoot&&this.adoptStyles()}createRenderRoot(){return this.attachShadow({mode:"open"})}adoptStyles(){const t=this.constructor._styles;0!==t.length&&(void 0===window.ShadyCSS||window.ShadyCSS.nativeShadow?Q?this.renderRoot.adoptedStyleSheets=t.map(t=>t.styleSheet):this._needsShimAdoptedStyleSheets=!0:window.ShadyCSS.ScopingShim.prepareAdoptedCssText(t.map(t=>t.cssText),this.localName))}connectedCallback(){super.connectedCallback(),this.hasUpdated&&void 0!==window.ShadyCSS&&window.ShadyCSS.styleElement(this)}update(t){super.update(t);const e=this.render();e instanceof f&&this.constructor.render(e,this.renderRoot,{scopeName:this.localName,eventContext:this}),this._needsShimAdoptedStyleSheets&&(this._needsShimAdoptedStyleSheets=!1,this.constructor._styles.forEach(t=>{const e=document.createElement("style");e.textContent=t.cssText,this.renderRoot.appendChild(e)}))}render(){}}Z.finalized=!0,Z.render=((t,e,s)=>{const n=s.scopeName,r=$.has(e),o=e instanceof ShadowRoot&&j&&t instanceof f,a=o&&!I.has(n),l=a?document.createDocumentFragment():e;if(((t,e,s)=>{let n=$.get(e);void 0===n&&(i(e,e.firstChild),$.set(e,n=new v(Object.assign({templateFactory:A},s))),n.appendInto(e)),n.setValue(t),n.commit()})(t,l,Object.assign({templateFactory:R(n)},s)),a){const t=$.get(l);$.delete(l),t.value instanceof m&&q(l,t.value.template,n),i(e,e.firstChild),e.appendChild(l),$.set(e,t)}!r&&o&&window.ShadyCSS.styleElement(e.host)}),window.JSCompiler_renameProperty=function(t,e){return t};let tt=[],et=document.createTextNode("");new window.MutationObserver(function(){const t=tt.length;for(let e=0;e<t;e++){let t=tt[e];if(t)try{t()}catch(t){setTimeout(()=>{throw t})}}tt.splice(0,t)}).observe(et,{characterData:!0});class st{constructor(){this._asyncModule=null,this._callback=null,this._timer=null}setConfig(t,e){this._asyncModule=t,this._callback=e,this._timer=this._asyncModule.run(()=>{this._timer=null,this._callback()})}cancel(){this.isActive()&&(this._asyncModule.cancel(this._timer),this._timer=null)}flush(){this.isActive()&&(this.cancel(),this._callback())}isActive(){return null!=this._timer}static debounce(t,e,s){return t instanceof st?t.cancel():t=new st,t.setConfig(e,s),t}}const it=1e3,nt=.5,rt=1,ot=["entity","sensors","_values"],at={auto:"hass:autorenew",manual:"hass:cursor-pointer",heat:"hass:fire",cool:"hass:snowflake",off:"hass:power",fan_only:"hass:fan",fan:"hass:fan",eco:"hass:leaf",dry:"hass:water-percent",idle:"hass:power"},lt={off:"mdi:radiator-off",on:"mdi:radiator",idle:"mdi:radiator-disabled",heat:"mdi:radiator",cool:"mdi:snowflake",auto:"mdi:radiator",manual:"mdi:radiator",boost:"mdi:fire",away:"mdi:radiator-disabled"},ht={temperature:!1,state:!1,mode:!1,away:!0};function ct(t,e=1){const[s,i]=String(t).split(".");return Number.isNaN(s)?"N/A":e?`${s}.${i||"0"}`:Math.round(s)}class dt extends Z{static get properties(){return{_hass:Object,config:Object,entity:Object,sensors:Array,modes:Object,icon:String,_values:Object,_mode:String,_hide:Object,name:String}}constructor(){super(),this._hass=null,this.entity=null,this.icon=null,this.sensors=[],this._stepSize=nt,this._values={},this._mode=null,this._hide=ht,this._haVersion=null}set hass(t){this._hass=t;const e=t.states[this.config.entity];if(void 0===e)return;this._haVersion=t.config.version.split(".").map(t=>parseInt(t,10));const{attributes:{operation_mode:s,operation_list:i=[],...n}}=e;if(this.entityType=function(t){return"number"==typeof t.target_temp_high&&"number"==typeof t.target_temp_low?"dual":"single"}(n),"dual"===this.entityType?this._values={target_temp_low:n.target_temp_low,target_temp_high:n.target_temp_high}:this._values={temperature:n.temperature},this.entity!==e){this.entity=e,this._mode=s,this.modes={};for(const t of i)this.modes[t]={include:!0,icon:at[t]}}!1===this.config.modes?this.modes=!1:"object"==typeof this.config.modes&&Object.entries(this.config.modes).map(([t,e])=>{this.modes.hasOwnProperty(t)&&("boolean"==typeof e?this.modes[t].include=e:this.modes[t]={...this.modes[t],...e})}),this.config.icon?this.icon=this.config.icon:this.icon=lt,this.config.step_size&&(this._stepSize=this.config.step_size),this.config.hide&&(this._hide={...this._hide,...this.config.hide}),"string"==typeof this.config.name?this.name=this.config.name:!1===this.config.name?this.name=!1:this.name=e.attributes.friendly_name,this.config.sensors&&(this.sensors=this.config.sensors.map(({name:e,entity:s,attribute:i,unit:n=""})=>{let r;const o=[e];return s?(r=t.states[s],o.push(r&&r.attributes&&r.attributes.friendly_name)):i&&i in this.entity.attributes&&(r=this.entity.attributes[i]+n,o.push(i)),o.push(s),{name:o.find(t=>!!t),state:r,entity:s}}))}shouldUpdate(t){return ot.some(e=>t.has(e))}localize(t,e=""){const s=this._hass.selectedLanguage||this._hass.language,i=`${e}${t}`,n=this._hass.resources[s];return i in n?n[i]:t}render({_hass:t,_hide:e,_values:s,config:i,entity:n,sensors:r}=this){if(!n)return z`
        ${z`
    <style is="custom-style">
      ha-card {
        ${"\n    --thermostat-font-size-xl: var(--paper-font-display3_-_font-size);\n    --thermostat-font-size-l: var(--paper-font-display2_-_font-size);\n    --thermostat-font-size-m: var(--paper-font-title_-_font-size);\n    --thermostat-font-size-title: 24px; --thermostat-spacing: 4px;\n  "}
        font-weight: var(--paper-font-body1_-_font-weight);
        line-height: var(--paper-font-body1_-_line-height);
      }
      .not-found {
        flex: 1;
        background-color: yellow;
        padding: calc(var(--thermostat-spacing) * 4);
      }
    </style>
  `}
        <ha-card class="not-found">
          Entity not available: <strong class="name">${i.entity}</strong>
        </ha-card>
      `;const{state:o,attributes:{min_temp:a=null,max_temp:l=null,current_temperature:h,operation_mode:c,...d}}=n,p=this._hass.config.unit_system.temperature,u=[e.temperature?null:this.renderInfoItem(`${ct(h,i.decimals)}${p}`,"Temperature"),e.state?null:this.renderInfoItem(this.localize(o,"state.climate."),"State"),e.away?null:this.renderAwayToggle(d.away_mode),r.map(({name:t,state:e})=>e&&this.renderInfoItem(e,t))||null].filter(t=>null!==t);return z`
      ${z`
    <style is="custom-style">
      ha-card {
        ${"\n    --thermostat-font-size-xl: var(--paper-font-display3_-_font-size);\n    --thermostat-font-size-l: var(--paper-font-display2_-_font-size);\n    --thermostat-font-size-m: var(--paper-font-title_-_font-size);\n    --thermostat-font-size-title: 24px; --thermostat-spacing: 4px;\n  "}
        -webkit-font-smoothing: var(
          --paper-font-body1_-_-webkit-font-smoothing
        );
        font-size: var(--paper-font-body1_-_font-size);
        font-weight: var(--paper-font-body1_-_font-weight);
        line-height: var(--paper-font-body1_-_line-height);

        padding-bottom: calc(var(--thermostat-spacing) * 4);
      }

      ha-card.no-header {
        padding: calc(var(--thermostat-spacing) * 4) 0;
      }

      .body {
        display: flex;
        flex-direction: row;
        justify-content: space-around;
        align-items: center;
      }
      .main {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;
      }
      .sensors {
        font-size: 1.1em;
      }
      table:empty {
        display: none;
      }
      header {
        display: flex;
        flex-direction: row;
        align-items: center;

        font-family: var(--paper-font-headline_-_font-family);
        -webkit-font-smoothing: var(
          --paper-font-headline_-_-webkit-font-smoothing
        );
        font-size: var(--paper-font-headline_-_font-size);
        font-weight: var(--paper-font-headline_-_font-weight);
        letter-spacing: var(--paper-font-headline_-_letter-spacing);
        line-height: var(--paper-font-headline_-_line-height);
        text-rendering: var(
          --paper-font-common-expensive-kerning_-_text-rendering
        );
        opacity: var(--dark-primary-opacity);
        padding: calc(var(--thermostat-spacing) * 6)
          calc(var(--thermostat-spacing) * 4)
          calc(var(--thermostat-spacing) * 4);
      }
      .header__icon {
        margin-right: calc(var(--thermostat-spacing) * 2);
        color: var(--paper-item-icon-color, #44739e);
      }
      .header__title {
        font-size: var(--thermostat-font-size-title);
        line-height: var(--thermostat-font-size-title);
        font-weight: normal;
        margin: 0;
        align-self: left;
      }
      .current-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
      }
      .current--value {
        margin: 0;
        font-size: var(--thermostat-font-size-xl);
        font-weight: 400;
        line-height: var(--thermostat-font-size-xl);
      }
      .current--unit {
        font-size: var(--thermostat-font-size-m);
      }
      .thermostat-trigger {
        padding: 0px;
      }
      .sensors th {
        text-align: right;
        font-weight: 300;
        padding-right: 8px;
        padding-bottom: 4px;
      }
      .sensors td {
        padding-bottom: 4px;
      }
      .clickable {
        cursor: pointer;
      }
      .modes {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        padding-left: calc(var(--thermostat-spacing) * 4);
        padding-right: calc(var(--thermostat-spacing) * 4);
      }
      .mode--active {
        color: var(--paper-item-icon-color, #44739e);
      }
      .mode__icon {
        padding-right: var(--thermostat-spacing);
      }
    </style>
  `}
      <ha-card class="${this.name?"":"no-header"}">
        ${this.renderHeader()}
        <section class="body">
          <table class="sensors">
            ${u}
          </table>

          ${Object.entries(s).map(([t,e])=>z`
              <div class="main">
                <div class="current-wrapper">
                  <paper-icon-button
                    ?disabled=${l&&e>=l}
                    class="thermostat-trigger"
                    icon="hass:chevron-up"
                    @click="${()=>this.setTemperature(this._stepSize,t)}"
                  >
                  </paper-icon-button>

                  <div @click=${()=>this.openEntityPopover()}>
                    <h3 class="current--value">
                      ${ct(e,i.decimals)}
                    </h3>
                  </div>
                  <paper-icon-button
                    ?disabled=${a&&e<=a}
                    class="thermostat-trigger"
                    icon="hass:chevron-down"
                    @click="${()=>this.setTemperature(-this._stepSize,t)}"
                  >
                  </paper-icon-button>
                </div>
                <span class="current--unit">${p}</span>
              </div>
            `)}
        </section>
        ${this.renderModeSelector(c)}
      </ha-card>
    `}renderHeader(){if(!1===this.name)return"";let t=this.icon;const{state:e}=this.entity;return"object"==typeof this.icon&&(t=e in this.icon&&this.icon[e]),z`
      <header class="clickable" @click=${()=>this.openEntityPopover()}>
        ${t&&z`
            <ha-icon class="header__icon" .icon=${t}></ha-icon>
          `||""}
        <h2 class="header__title">${this.name}</h2>
      </header>
    `}renderModeSelector(t){if(!1===this.modes)return;const e=Object.entries(this.modes).filter(([t,e])=>e.include),s=(t,e)=>!1===e.name?null:e.name||this.localize(t,"state.climate."),i=t=>!1===t?null:z`
        <ha-icon class="mode__icon" .icon=${t}></ha-icon>
      `;return this._haVersion[1]<=87?z`
        <div class="modes">
          ${e.map(([e,n])=>z`
              <paper-button
                class="${e===t?"mode--active":""}"
                @click=${()=>this.setMode(e)}
              >
                ${i(n.icon)} ${s(e,n)}
              </paper-button>
            `)}
        </div>
      `:z`
      <div class="modes">
        ${e.map(([e,n])=>z`
            <mwc-button
              ?disabled=${e===t}
              ?outlined=${e===t}
              ?dense=${!0}
              @click=${()=>this.setMode(e)}
            >
              ${i(n.icon)} ${s(e,n)}
            </mwc-button>
          `)}
      </div>
    `}renderAwayToggle(t){return z`
      <tr>
        <th>${this.localize("ui.card.climate.away_mode")}</th>
        <td>
          <paper-toggle-button
            ?checked=${"on"===t}
            @click=${()=>{this._hass.callService("climate","set_away_mode",{entity_id:this.config.entity,away_mode:!("on"===t)})}}
          />
        </td>
      </tr>
    `}renderInfoItem(t,e){if(!t)return;let s;if("object"==typeof t){let e=t.state;if("device_class"in t.attributes){const[s]=t.entity_id.split("."),i=["state",s,t.attributes.device_class,""].join(".");e=this.localize(t.state,i)}s=z`
        <td
          class="clickable"
          @click="${()=>this.openEntityPopover(t.entity_id)}"
        >
          ${e} ${t.attributes.unit_of_measurement}
        </td>
      `}else s=z`
        <td>${t}</td>
      `;return z`
      <tr>
        <th>${e}:</th>
        ${s}
      </tr>
    `}setTemperature(t,e="temperature"){this._values={...this._values,[e]:this._values[e]+t},this._debouncedSetTemperature=st.debounce(this._debouncedSetTemperature,{run:t=>window.setTimeout(t,it),cancel:t=>window.clearTimeout(t)},()=>{this._hass.callService("climate","set_temperature",{entity_id:this.config.entity,...this._values})})}setMode(t){t&&t!==this._mode&&this._hass.callService("climate","set_operation_mode",{entity_id:this.config.entity,operation_mode:t})}openEntityPopover(t=this.config.entity){this.fire("hass-more-info",{entityId:t})}fire(t,e,s){s=s||{},e=null==e?{}:e;const i=new Event(t,{bubbles:void 0===s.bubbles||s.bubbles,cancelable:Boolean(s.cancelable),composed:void 0===s.composed||s.composed});return i.detail=e,this.dispatchEvent(i),i}setConfig(t){if(!t.entity)throw new Error("You need to define an entity");this.config={decimals:rt,...t}}getCardSize(){return 3}}return window.customElements.define("simple-thermostat",dt),dt});
