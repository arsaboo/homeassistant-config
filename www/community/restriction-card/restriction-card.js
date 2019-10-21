/*! *****************************************************************************
Copyright (c) Microsoft Corporation. All rights reserved.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0

THIS CODE IS PROVIDED ON AN *AS IS* BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION ANY IMPLIED
WARRANTIES OR CONDITIONS OF TITLE, FITNESS FOR A PARTICULAR PURPOSE,
MERCHANTABLITY OR NON-INFRINGEMENT.

See the Apache Version 2.0 License for specific language governing permissions
and limitations under the License.
***************************************************************************** */
function t(t,e,s,n){var i,r=arguments.length,o=r<3?e:null===n?n=Object.getOwnPropertyDescriptor(e,s):n;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)o=Reflect.decorate(t,e,s,n);else for(var a=t.length-1;a>=0;a--)(i=t[a])&&(o=(r<3?i(o):r>3?i(e,s,o):i(e,s))||o);return r>3&&o&&Object.defineProperty(e,s,o),o
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */}const e=new WeakMap,s=t=>(...s)=>{const n=t(...s);return e.set(n,!0),n},n=t=>"function"==typeof t&&e.has(t),i=void 0!==window.customElements&&void 0!==window.customElements.polyfillWrapFlushCallback,r=(t,e,s=null)=>{for(;e!==s;){const s=e.nextSibling;t.removeChild(e),e=s}},o={},a={},c=`{{lit-${String(Math.random()).slice(2)}}}`,l=`\x3c!--${c}--\x3e`,d=new RegExp(`${c}|${l}`),h="$lit$";class u{constructor(t,e){this.parts=[],this.element=e;const s=[],n=[],i=document.createTreeWalker(e.content,133,null,!1);let r=0,o=-1,a=0;const{strings:l,values:{length:u}}=t;for(;a<u;){const t=i.nextNode();if(null!==t){if(o++,1===t.nodeType){if(t.hasAttributes()){const e=t.attributes,{length:s}=e;let n=0;for(let t=0;t<s;t++)p(e[t].name,h)&&n++;for(;n-- >0;){const e=l[a],s=g.exec(e)[2],n=s.toLowerCase()+h,i=t.getAttribute(n);t.removeAttribute(n);const r=i.split(d);this.parts.push({type:"attribute",index:o,name:s,strings:r}),a+=r.length-1}}"TEMPLATE"===t.tagName&&(n.push(t),i.currentNode=t.content)}else if(3===t.nodeType){const e=t.data;if(e.indexOf(c)>=0){const n=t.parentNode,i=e.split(d),r=i.length-1;for(let e=0;e<r;e++){let s,r=i[e];if(""===r)s=f();else{const t=g.exec(r);null!==t&&p(t[2],h)&&(r=r.slice(0,t.index)+t[1]+t[2].slice(0,-h.length)+t[3]),s=document.createTextNode(r)}n.insertBefore(s,t),this.parts.push({type:"node",index:++o})}""===i[r]?(n.insertBefore(f(),t),s.push(t)):t.data=i[r],a+=r}}else if(8===t.nodeType)if(t.data===c){const e=t.parentNode;null!==t.previousSibling&&o!==r||(o++,e.insertBefore(f(),t)),r=o,this.parts.push({type:"node",index:o}),null===t.nextSibling?t.data="":(s.push(t),o--),a++}else{let e=-1;for(;-1!==(e=t.data.indexOf(c,e+1));)this.parts.push({type:"node",index:-1}),a++}}else i.currentNode=n.pop()}for(const t of s)t.parentNode.removeChild(t)}}const p=(t,e)=>{const s=t.length-e.length;return s>=0&&t.slice(s)===e},m=t=>-1!==t.index,f=()=>document.createComment(""),g=/([ \x09\x0a\x0c\x0d])([^\0-\x1F\x7F-\x9F "'>=/]+)([ \x09\x0a\x0c\x0d]*=[ \x09\x0a\x0c\x0d]*(?:[^ \x09\x0a\x0c\x0d"'`<>=]*|"[^"]*|'[^']*))$/;
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */
class _{constructor(t,e,s){this.__parts=[],this.template=t,this.processor=e,this.options=s}update(t){let e=0;for(const s of this.__parts)void 0!==s&&s.setValue(t[e]),e++;for(const t of this.__parts)void 0!==t&&t.commit()}_clone(){const t=i?this.template.element.content.cloneNode(!0):document.importNode(this.template.element.content,!0),e=[],s=this.template.parts,n=document.createTreeWalker(t,133,null,!1);let r,o=0,a=0,c=n.nextNode();for(;o<s.length;)if(r=s[o],m(r)){for(;a<r.index;)a++,"TEMPLATE"===c.nodeName&&(e.push(c),n.currentNode=c.content),null===(c=n.nextNode())&&(n.currentNode=e.pop(),c=n.nextNode());if("node"===r.type){const t=this.processor.handleTextExpression(this.options);t.insertAfterNode(c.previousSibling),this.__parts.push(t)}else this.__parts.push(...this.processor.handleAttributeExpressions(c,r.name,r.strings,this.options));o++}else this.__parts.push(void 0),o++;return i&&(document.adoptNode(t),customElements.upgrade(t)),t}}
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */const y=` ${c} `;class v{constructor(t,e,s,n){this.strings=t,this.values=e,this.type=s,this.processor=n}getHTML(){const t=this.strings.length-1;let e="",s=!1;for(let n=0;n<t;n++){const t=this.strings[n],i=t.lastIndexOf("\x3c!--");s=(i>-1||s)&&-1===t.indexOf("--\x3e",i+1);const r=g.exec(t);e+=null===r?t+(s?y:l):t.substr(0,r.index)+r[1]+r[2]+h+r[3]+c}return e+=this.strings[t]}getTemplateElement(){const t=document.createElement("template");return t.innerHTML=this.getHTML(),t}}
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */const S=t=>null===t||!("object"==typeof t||"function"==typeof t),w=t=>Array.isArray(t)||!(!t||!t[Symbol.iterator]);class b{constructor(t,e,s){this.dirty=!0,this.element=t,this.name=e,this.strings=s,this.parts=[];for(let t=0;t<s.length-1;t++)this.parts[t]=this._createPart()}_createPart(){return new x(this)}_getValue(){const t=this.strings,e=t.length-1;let s="";for(let n=0;n<e;n++){s+=t[n];const e=this.parts[n];if(void 0!==e){const t=e.value;if(S(t)||!w(t))s+="string"==typeof t?t:String(t);else for(const e of t)s+="string"==typeof e?e:String(e)}}return s+=t[e]}commit(){this.dirty&&(this.dirty=!1,this.element.setAttribute(this.name,this._getValue()))}}class x{constructor(t){this.value=void 0,this.committer=t}setValue(t){t===o||S(t)&&t===this.value||(this.value=t,n(t)||(this.committer.dirty=!0))}commit(){for(;n(this.value);){const t=this.value;this.value=o,t(this)}this.value!==o&&this.committer.commit()}}class P{constructor(t){this.value=void 0,this.__pendingValue=void 0,this.options=t}appendInto(t){this.startNode=t.appendChild(f()),this.endNode=t.appendChild(f())}insertAfterNode(t){this.startNode=t,this.endNode=t.nextSibling}appendIntoPart(t){t.__insert(this.startNode=f()),t.__insert(this.endNode=f())}insertAfterPart(t){t.__insert(this.startNode=f()),this.endNode=t.endNode,t.endNode=this.startNode}setValue(t){this.__pendingValue=t}commit(){for(;n(this.__pendingValue);){const t=this.__pendingValue;this.__pendingValue=o,t(this)}const t=this.__pendingValue;t!==o&&(S(t)?t!==this.value&&this.__commitText(t):t instanceof v?this.__commitTemplateResult(t):t instanceof Node?this.__commitNode(t):w(t)?this.__commitIterable(t):t===a?(this.value=a,this.clear()):this.__commitText(t))}__insert(t){this.endNode.parentNode.insertBefore(t,this.endNode)}__commitNode(t){this.value!==t&&(this.clear(),this.__insert(t),this.value=t)}__commitText(t){const e=this.startNode.nextSibling,s="string"==typeof(t=null==t?"":t)?t:String(t);e===this.endNode.previousSibling&&3===e.nodeType?e.data=s:this.__commitNode(document.createTextNode(s)),this.value=t}__commitTemplateResult(t){const e=this.options.templateFactory(t);if(this.value instanceof _&&this.value.template===e)this.value.update(t.values);else{const s=new _(e,t.processor,this.options),n=s._clone();s.update(t.values),this.__commitNode(n),this.value=s}}__commitIterable(t){Array.isArray(this.value)||(this.value=[],this.clear());const e=this.value;let s,n=0;for(const i of t)void 0===(s=e[n])&&(s=new P(this.options),e.push(s),0===n?s.appendIntoPart(this):s.insertAfterPart(e[n-1])),s.setValue(i),s.commit(),n++;n<e.length&&(e.length=n,this.clear(s&&s.endNode))}clear(t=this.startNode){r(this.startNode.parentNode,t.nextSibling,this.endNode)}}class C{constructor(t,e,s){if(this.value=void 0,this.__pendingValue=void 0,2!==s.length||""!==s[0]||""!==s[1])throw new Error("Boolean attributes can only contain a single expression");this.element=t,this.name=e,this.strings=s}setValue(t){this.__pendingValue=t}commit(){for(;n(this.__pendingValue);){const t=this.__pendingValue;this.__pendingValue=o,t(this)}if(this.__pendingValue===o)return;const t=!!this.__pendingValue;this.value!==t&&(t?this.element.setAttribute(this.name,""):this.element.removeAttribute(this.name),this.value=t),this.__pendingValue=o}}class E extends b{constructor(t,e,s){super(t,e,s),this.single=2===s.length&&""===s[0]&&""===s[1]}_createPart(){return new N(this)}_getValue(){return this.single?this.parts[0].value:super._getValue()}commit(){this.dirty&&(this.dirty=!1,this.element[this.name]=this._getValue())}}class N extends x{}let k=!1;try{const t={get capture(){return k=!0,!1}};window.addEventListener("test",t,t),window.removeEventListener("test",t,t)}catch(t){}class M{constructor(t,e,s){this.value=void 0,this.__pendingValue=void 0,this.element=t,this.eventName=e,this.eventContext=s,this.__boundHandleEvent=t=>this.handleEvent(t)}setValue(t){this.__pendingValue=t}commit(){for(;n(this.__pendingValue);){const t=this.__pendingValue;this.__pendingValue=o,t(this)}if(this.__pendingValue===o)return;const t=this.__pendingValue,e=this.value,s=null==t||null!=e&&(t.capture!==e.capture||t.once!==e.once||t.passive!==e.passive),i=null!=t&&(null==e||s);s&&this.element.removeEventListener(this.eventName,this.__boundHandleEvent,this.__options),i&&(this.__options=T(t),this.element.addEventListener(this.eventName,this.__boundHandleEvent,this.__options)),this.value=t,this.__pendingValue=o}handleEvent(t){"function"==typeof this.value?this.value.call(this.eventContext||this.element,t):this.value.handleEvent(t)}}const T=t=>t&&(k?{capture:t.capture,passive:t.passive,once:t.once}:t.capture);
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */const A=new class{handleAttributeExpressions(t,e,s,n){const i=e[0];if("."===i){return new E(t,e.slice(1),s).parts}return"@"===i?[new M(t,e.slice(1),n.eventContext)]:"?"===i?[new C(t,e.slice(1),s)]:new b(t,e,s).parts}handleTextExpression(t){return new P(t)}};
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */function D(t){let e=R.get(t.type);void 0===e&&(e={stringsArray:new WeakMap,keyString:new Map},R.set(t.type,e));let s=e.stringsArray.get(t.strings);if(void 0!==s)return s;const n=t.strings.join(c);return void 0===(s=e.keyString.get(n))&&(s=new u(t,t.getTemplateElement()),e.keyString.set(n,s)),e.stringsArray.set(t.strings,s),s}const R=new Map,V=new WeakMap;
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */
(window.litHtmlVersions||(window.litHtmlVersions=[])).push("1.1.2");const O=(t,...e)=>new v(t,e,"html",A),Y=133;
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */function H(t,e){const{element:{content:s},parts:n}=t,i=document.createTreeWalker(s,Y,null,!1);let r=U(n),o=n[r],a=-1,c=0;const l=[];let d=null;for(;i.nextNode();){a++;const t=i.currentNode;for(t.previousSibling===d&&(d=null),e.has(t)&&(l.push(t),null===d&&(d=t)),null!==d&&c++;void 0!==o&&o.index===a;)o.index=null!==d?-1:o.index-c,o=n[r=U(n,r)]}l.forEach(t=>t.parentNode.removeChild(t))}const L=t=>{let e=11===t.nodeType?0:1;const s=document.createTreeWalker(t,Y,null,!1);for(;s.nextNode();)e++;return e},U=(t,e=-1)=>{for(let s=e+1;s<t.length;s++){const e=t[s];if(m(e))return s}return-1};
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */
const j=(t,e)=>`${t}--${e}`;let $=!0;void 0===window.ShadyCSS?$=!1:void 0===window.ShadyCSS.prepareTemplateDom&&(console.warn("Incompatible ShadyCSS version detected. Please update to at least @webcomponents/webcomponentsjs@2.0.2 and @webcomponents/shadycss@1.3.1."),$=!1);const z=t=>e=>{const s=j(e.type,t);let n=R.get(s);void 0===n&&(n={stringsArray:new WeakMap,keyString:new Map},R.set(s,n));let i=n.stringsArray.get(e.strings);if(void 0!==i)return i;const r=e.strings.join(c);if(void 0===(i=n.keyString.get(r))){const s=e.getTemplateElement();$&&window.ShadyCSS.prepareTemplateDom(s,t),i=new u(e,s),n.keyString.set(r,i)}return n.stringsArray.set(e.strings,i),i},F=["html","svg"],q=new Set,I=(t,e,s)=>{q.add(t);const n=s?s.element:document.createElement("template"),i=e.querySelectorAll("style"),{length:r}=i;if(0===r)return void window.ShadyCSS.prepareTemplateStyles(n,t);const o=document.createElement("style");for(let t=0;t<r;t++){const e=i[t];e.parentNode.removeChild(e),o.textContent+=e.textContent}(t=>{F.forEach(e=>{const s=R.get(j(e,t));void 0!==s&&s.keyString.forEach(t=>{const{element:{content:e}}=t,s=new Set;Array.from(e.querySelectorAll("style")).forEach(t=>{s.add(t)}),H(t,s)})})})(t);const a=n.content;s?function(t,e,s=null){const{element:{content:n},parts:i}=t;if(null==s)return void n.appendChild(e);const r=document.createTreeWalker(n,Y,null,!1);let o=U(i),a=0,c=-1;for(;r.nextNode();){for(c++,r.currentNode===s&&(a=L(e),s.parentNode.insertBefore(e,s));-1!==o&&i[o].index===c;){if(a>0){for(;-1!==o;)i[o].index+=a,o=U(i,o);return}o=U(i,o)}}}(s,o,a.firstChild):a.insertBefore(o,a.firstChild),window.ShadyCSS.prepareTemplateStyles(n,t);const c=a.querySelector("style");if(window.ShadyCSS.nativeShadow&&null!==c)e.insertBefore(c.cloneNode(!0),e.firstChild);else if(s){a.insertBefore(o,a.firstChild);const t=new Set;t.add(o),H(s,t)}};window.JSCompiler_renameProperty=(t,e)=>t;const B={toAttribute(t,e){switch(e){case Boolean:return t?"":null;case Object:case Array:return null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){switch(e){case Boolean:return null!==t;case Number:return null===t?null:Number(t);case Object:case Array:return JSON.parse(t)}return t}},W=(t,e)=>e!==t&&(e==e||t==t),J={attribute:!0,type:String,converter:B,reflect:!1,hasChanged:W},Z=Promise.resolve(!0),X=1,G=4,K=8,Q=16,tt=32,et="finalized";class st extends HTMLElement{constructor(){super(),this._updateState=0,this._instanceProperties=void 0,this._updatePromise=Z,this._hasConnectedResolver=void 0,this._changedProperties=new Map,this._reflectingProperties=void 0,this.initialize()}static get observedAttributes(){this.finalize();const t=[];return this._classProperties.forEach((e,s)=>{const n=this._attributeNameForProperty(s,e);void 0!==n&&(this._attributeToPropertyMap.set(n,s),t.push(n))}),t}static _ensureClassProperties(){if(!this.hasOwnProperty(JSCompiler_renameProperty("_classProperties",this))){this._classProperties=new Map;const t=Object.getPrototypeOf(this)._classProperties;void 0!==t&&t.forEach((t,e)=>this._classProperties.set(e,t))}}static createProperty(t,e=J){if(this._ensureClassProperties(),this._classProperties.set(t,e),e.noAccessor||this.prototype.hasOwnProperty(t))return;const s="symbol"==typeof t?Symbol():`__${t}`;Object.defineProperty(this.prototype,t,{get(){return this[s]},set(e){const n=this[t];this[s]=e,this._requestUpdate(t,n)},configurable:!0,enumerable:!0})}static finalize(){const t=Object.getPrototypeOf(this);if(t.hasOwnProperty(et)||t.finalize(),this[et]=!0,this._ensureClassProperties(),this._attributeToPropertyMap=new Map,this.hasOwnProperty(JSCompiler_renameProperty("properties",this))){const t=this.properties,e=[...Object.getOwnPropertyNames(t),..."function"==typeof Object.getOwnPropertySymbols?Object.getOwnPropertySymbols(t):[]];for(const s of e)this.createProperty(s,t[s])}}static _attributeNameForProperty(t,e){const s=e.attribute;return!1===s?void 0:"string"==typeof s?s:"string"==typeof t?t.toLowerCase():void 0}static _valueHasChanged(t,e,s=W){return s(t,e)}static _propertyValueFromAttribute(t,e){const s=e.type,n=e.converter||B,i="function"==typeof n?n:n.fromAttribute;return i?i(t,s):t}static _propertyValueToAttribute(t,e){if(void 0===e.reflect)return;const s=e.type,n=e.converter;return(n&&n.toAttribute||B.toAttribute)(t,s)}initialize(){this._saveInstanceProperties(),this._requestUpdate()}_saveInstanceProperties(){this.constructor._classProperties.forEach((t,e)=>{if(this.hasOwnProperty(e)){const t=this[e];delete this[e],this._instanceProperties||(this._instanceProperties=new Map),this._instanceProperties.set(e,t)}})}_applyInstanceProperties(){this._instanceProperties.forEach((t,e)=>this[e]=t),this._instanceProperties=void 0}connectedCallback(){this._updateState=this._updateState|tt,this._hasConnectedResolver&&(this._hasConnectedResolver(),this._hasConnectedResolver=void 0)}disconnectedCallback(){}attributeChangedCallback(t,e,s){e!==s&&this._attributeToProperty(t,s)}_propertyToAttribute(t,e,s=J){const n=this.constructor,i=n._attributeNameForProperty(t,s);if(void 0!==i){const t=n._propertyValueToAttribute(e,s);if(void 0===t)return;this._updateState=this._updateState|K,null==t?this.removeAttribute(i):this.setAttribute(i,t),this._updateState=this._updateState&~K}}_attributeToProperty(t,e){if(this._updateState&K)return;const s=this.constructor,n=s._attributeToPropertyMap.get(t);if(void 0!==n){const t=s._classProperties.get(n)||J;this._updateState=this._updateState|Q,this[n]=s._propertyValueFromAttribute(e,t),this._updateState=this._updateState&~Q}}_requestUpdate(t,e){let s=!0;if(void 0!==t){const n=this.constructor,i=n._classProperties.get(t)||J;n._valueHasChanged(this[t],e,i.hasChanged)?(this._changedProperties.has(t)||this._changedProperties.set(t,e),!0!==i.reflect||this._updateState&Q||(void 0===this._reflectingProperties&&(this._reflectingProperties=new Map),this._reflectingProperties.set(t,i))):s=!1}!this._hasRequestedUpdate&&s&&this._enqueueUpdate()}requestUpdate(t,e){return this._requestUpdate(t,e),this.updateComplete}async _enqueueUpdate(){let t,e;this._updateState=this._updateState|G;const s=this._updatePromise;this._updatePromise=new Promise((s,n)=>{t=s,e=n});try{await s}catch(t){}this._hasConnected||await new Promise(t=>this._hasConnectedResolver=t);try{const t=this.performUpdate();null!=t&&await t}catch(t){e(t)}t(!this._hasRequestedUpdate)}get _hasConnected(){return this._updateState&tt}get _hasRequestedUpdate(){return this._updateState&G}get hasUpdated(){return this._updateState&X}performUpdate(){this._instanceProperties&&this._applyInstanceProperties();let t=!1;const e=this._changedProperties;try{(t=this.shouldUpdate(e))&&this.update(e)}catch(e){throw t=!1,e}finally{this._markUpdated()}t&&(this._updateState&X||(this._updateState=this._updateState|X,this.firstUpdated(e)),this.updated(e))}_markUpdated(){this._changedProperties=new Map,this._updateState=this._updateState&~G}get updateComplete(){return this._getUpdateComplete()}_getUpdateComplete(){return this._updatePromise}shouldUpdate(t){return!0}update(t){void 0!==this._reflectingProperties&&this._reflectingProperties.size>0&&(this._reflectingProperties.forEach((t,e)=>this._propertyToAttribute(e,this[e],t)),this._reflectingProperties=void 0)}updated(t){}firstUpdated(t){}}st[et]=!0;
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */
const nt=(t,e)=>"method"!==e.kind||!e.descriptor||"value"in e.descriptor?{kind:"field",key:Symbol(),placement:"own",descriptor:{},initializer(){"function"==typeof e.initializer&&(this[e.key]=e.initializer.call(this))},finisher(s){s.createProperty(e.key,t)}}:Object.assign({},e,{finisher(s){s.createProperty(e.key,t)}}),it=(t,e,s)=>{e.constructor.createProperty(s,t)};function rt(t){return(e,s)=>void 0!==s?it(t,e,s):nt(t,e)}
/**
@license
Copyright (c) 2019 The Polymer Project Authors. All rights reserved.
This code may only be used under the BSD style license found at
http://polymer.github.io/LICENSE.txt The complete set of authors may be found at
http://polymer.github.io/AUTHORS.txt The complete set of contributors may be
found at http://polymer.github.io/CONTRIBUTORS.txt Code distributed by Google as
part of the polymer project is also subject to an additional IP rights grant
found at http://polymer.github.io/PATENTS.txt
*/const ot="adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,at=Symbol();class ct{constructor(t,e){if(e!==at)throw new Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t}get styleSheet(){return void 0===this._styleSheet&&(ot?(this._styleSheet=new CSSStyleSheet,this._styleSheet.replaceSync(this.cssText)):this._styleSheet=null),this._styleSheet}toString(){return this.cssText}}const lt=(t,...e)=>{const s=e.reduce((e,s,n)=>e+(t=>{if(t instanceof ct)return t.cssText;if("number"==typeof t)return t;throw new Error(`Value passed to 'css' function must be a 'css' function result: ${t}. Use 'unsafeCSS' to pass non-literal values, but\n            take care to ensure page security.`)})(s)+t[n+1],t[0]);return new ct(s,at)};
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */
(window.litElementVersions||(window.litElementVersions=[])).push("2.2.1");const dt=t=>t.flat?t.flat(1/0):function t(e,s=[]){for(let n=0,i=e.length;n<i;n++){const i=e[n];Array.isArray(i)?t(i,s):s.push(i)}return s}(t);class ht extends st{static finalize(){super.finalize.call(this),this._styles=this.hasOwnProperty(JSCompiler_renameProperty("styles",this))?this._getUniqueStyles():this._styles||[]}static _getUniqueStyles(){const t=this.styles,e=[];if(Array.isArray(t)){dt(t).reduceRight((t,e)=>(t.add(e),t),new Set).forEach(t=>e.unshift(t))}else t&&e.push(t);return e}initialize(){super.initialize(),this.renderRoot=this.createRenderRoot(),window.ShadowRoot&&this.renderRoot instanceof window.ShadowRoot&&this.adoptStyles()}createRenderRoot(){return this.attachShadow({mode:"open"})}adoptStyles(){const t=this.constructor._styles;0!==t.length&&(void 0===window.ShadyCSS||window.ShadyCSS.nativeShadow?ot?this.renderRoot.adoptedStyleSheets=t.map(t=>t.styleSheet):this._needsShimAdoptedStyleSheets=!0:window.ShadyCSS.ScopingShim.prepareAdoptedCssText(t.map(t=>t.cssText),this.localName))}connectedCallback(){super.connectedCallback(),this.hasUpdated&&void 0!==window.ShadyCSS&&window.ShadyCSS.styleElement(this)}update(t){super.update(t);const e=this.render();e instanceof v&&this.constructor.render(e,this.renderRoot,{scopeName:this.localName,eventContext:this}),this._needsShimAdoptedStyleSheets&&(this._needsShimAdoptedStyleSheets=!1,this.constructor._styles.forEach(t=>{const e=document.createElement("style");e.textContent=t.cssText,this.renderRoot.appendChild(e)}))}render(){}}ht.finalized=!0,ht.render=(t,e,s)=>{if(!s||"object"!=typeof s||!s.scopeName)throw new Error("The `scopeName` option is required.");const n=s.scopeName,i=V.has(e),o=$&&11===e.nodeType&&!!e.host,a=o&&!q.has(n),c=a?document.createDocumentFragment():e;if(((t,e,s)=>{let n=V.get(e);void 0===n&&(r(e,e.firstChild),V.set(e,n=new P(Object.assign({templateFactory:D},s))),n.appendInto(e)),n.setValue(t),n.commit()})(t,c,Object.assign({templateFactory:z(n)},s)),a){const t=V.get(c);V.delete(c);const s=t.value instanceof _?t.value.template:void 0;I(n,c,s),r(e,e.firstChild),e.appendChild(c),V.set(e,t)}!i&&o&&window.ShadyCSS.styleElement(e.host)};
/**
 * @license
 * Copyright (c) 2018 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */
const ut=new WeakMap,pt=s(t=>e=>{if(!(e instanceof x)||e instanceof N||"class"!==e.committer.name||e.committer.parts.length>1)throw new Error("The `classMap` directive must be used in the `class` attribute and must be the only part in the attribute.");const{committer:s}=e,{element:n}=s;ut.has(e)||(n.className=s.strings.join(" "));const{classList:i}=n,r=ut.get(e);for(const e in r)e in t||i.remove(e);for(const e in t){const s=t[e];if(!r||s!==r[e]){i[s?"add":"remove"](e)}}ut.set(e,t)});var mt={},ft=/d{1,4}|M{1,4}|YY(?:YY)?|S{1,3}|Do|ZZ|([HhMsDm])\1?|[aA]|"[^"]*"|'[^']*'/g,gt="[^\\s]+",_t=/\[([^]*?)\]/gm,yt=function(){};function vt(t,e){for(var s=[],n=0,i=t.length;n<i;n++)s.push(t[n].substr(0,e));return s}function St(t){return function(e,s,n){var i=n[t].indexOf(s.charAt(0).toUpperCase()+s.substr(1).toLowerCase());~i&&(e.month=i)}}function wt(t,e){for(t=String(t),e=e||2;t.length<e;)t="0"+t;return t}var bt=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],xt=["January","February","March","April","May","June","July","August","September","October","November","December"],Pt=vt(xt,3),Ct=vt(bt,3);mt.i18n={dayNamesShort:Ct,dayNames:bt,monthNamesShort:Pt,monthNames:xt,amPm:["am","pm"],DoFn:function(t){return t+["th","st","nd","rd"][t%10>3?0:(t-t%10!=10)*t%10]}};var Et={D:function(t){return t.getDate()},DD:function(t){return wt(t.getDate())},Do:function(t,e){return e.DoFn(t.getDate())},d:function(t){return t.getDay()},dd:function(t){return wt(t.getDay())},ddd:function(t,e){return e.dayNamesShort[t.getDay()]},dddd:function(t,e){return e.dayNames[t.getDay()]},M:function(t){return t.getMonth()+1},MM:function(t){return wt(t.getMonth()+1)},MMM:function(t,e){return e.monthNamesShort[t.getMonth()]},MMMM:function(t,e){return e.monthNames[t.getMonth()]},YY:function(t){return wt(String(t.getFullYear()),4).substr(2)},YYYY:function(t){return wt(t.getFullYear(),4)},h:function(t){return t.getHours()%12||12},hh:function(t){return wt(t.getHours()%12||12)},H:function(t){return t.getHours()},HH:function(t){return wt(t.getHours())},m:function(t){return t.getMinutes()},mm:function(t){return wt(t.getMinutes())},s:function(t){return t.getSeconds()},ss:function(t){return wt(t.getSeconds())},S:function(t){return Math.round(t.getMilliseconds()/100)},SS:function(t){return wt(Math.round(t.getMilliseconds()/10),2)},SSS:function(t){return wt(t.getMilliseconds(),3)},a:function(t,e){return t.getHours()<12?e.amPm[0]:e.amPm[1]},A:function(t,e){return t.getHours()<12?e.amPm[0].toUpperCase():e.amPm[1].toUpperCase()},ZZ:function(t){var e=t.getTimezoneOffset();return(e>0?"-":"+")+wt(100*Math.floor(Math.abs(e)/60)+Math.abs(e)%60,4)}},Nt={D:["\\d\\d?",function(t,e){t.day=e}],Do:["\\d\\d?"+gt,function(t,e){t.day=parseInt(e,10)}],M:["\\d\\d?",function(t,e){t.month=e-1}],YY:["\\d\\d?",function(t,e){var s=+(""+(new Date).getFullYear()).substr(0,2);t.year=""+(e>68?s-1:s)+e}],h:["\\d\\d?",function(t,e){t.hour=e}],m:["\\d\\d?",function(t,e){t.minute=e}],s:["\\d\\d?",function(t,e){t.second=e}],YYYY:["\\d{4}",function(t,e){t.year=e}],S:["\\d",function(t,e){t.millisecond=100*e}],SS:["\\d{2}",function(t,e){t.millisecond=10*e}],SSS:["\\d{3}",function(t,e){t.millisecond=e}],d:["\\d\\d?",yt],ddd:[gt,yt],MMM:[gt,St("monthNamesShort")],MMMM:[gt,St("monthNames")],a:[gt,function(t,e,s){var n=e.toLowerCase();n===s.amPm[0]?t.isPm=!1:n===s.amPm[1]&&(t.isPm=!0)}],ZZ:["[^\\s]*?[\\+\\-]\\d\\d:?\\d\\d|[^\\s]*?Z",function(t,e){var s,n=(e+"").match(/([+-]|\d\d)/gi);n&&(s=60*n[1]+parseInt(n[2],10),t.timezoneOffset="+"===n[0]?s:-s)}]};Nt.dd=Nt.d,Nt.dddd=Nt.ddd,Nt.DD=Nt.D,Nt.mm=Nt.m,Nt.hh=Nt.H=Nt.HH=Nt.h,Nt.MM=Nt.M,Nt.ss=Nt.s,Nt.A=Nt.a,mt.masks={default:"ddd MMM DD YYYY HH:mm:ss",shortDate:"M/D/YY",mediumDate:"MMM D, YYYY",longDate:"MMMM D, YYYY",fullDate:"dddd, MMMM D, YYYY",shortTime:"HH:mm",mediumTime:"HH:mm:ss",longTime:"HH:mm:ss.SSS"},mt.format=function(t,e,s){var n=s||mt.i18n;if("number"==typeof t&&(t=new Date(t)),"[object Date]"!==Object.prototype.toString.call(t)||isNaN(t.getTime()))throw new Error("Invalid Date in fecha.format");e=mt.masks[e]||e||mt.masks.default;var i=[];return(e=(e=e.replace(_t,(function(t,e){return i.push(e),"@@@"}))).replace(ft,(function(e){return e in Et?Et[e](t,n):e.slice(1,e.length-1)}))).replace(/@@@/g,(function(){return i.shift()}))},mt.parse=function(t,e,s){var n=s||mt.i18n;if("string"!=typeof e)throw new Error("Invalid format in fecha.parse");if(e=mt.masks[e]||e,t.length>1e3)return null;var i={},r=[],o=[];e=e.replace(_t,(function(t,e){return o.push(e),"@@@"}));var a,c=(a=e,a.replace(/[|\\{()[^$+*?.-]/g,"\\$&")).replace(ft,(function(t){if(Nt[t]){var e=Nt[t];return r.push(e[1]),"("+e[0]+")"}return t}));c=c.replace(/@@@/g,(function(){return o.shift()}));var l=t.match(new RegExp(c,"i"));if(!l)return null;for(var d=1;d<l.length;d++)r[d-1](i,l[d],n);var h,u=new Date;return!0===i.isPm&&null!=i.hour&&12!=+i.hour?i.hour=+i.hour+12:!1===i.isPm&&12==+i.hour&&(i.hour=0),null!=i.timezoneOffset?(i.minute=+(i.minute||0)-+i.timezoneOffset,h=new Date(Date.UTC(i.year||u.getFullYear(),i.month||0,i.day||1,i.hour||0,i.minute||0,i.second||0,i.millisecond||0))):h=new Date(i.year||u.getFullYear(),i.month||0,i.day||1,i.hour||0,i.minute||0,i.second||0,i.millisecond||0),h};(function(){try{(new Date).toLocaleDateString("i")}catch(t){return"RangeError"===t.name}})(),function(){try{(new Date).toLocaleString("i")}catch(t){return"RangeError"===t.name}}(),function(){try{(new Date).toLocaleTimeString("i")}catch(t){return"RangeError"===t.name}}();var kt=function(t){var e=function(t,e){return s("hui-error-card",{type:"error",error:t,config:e})},s=function(t,s){var n=window.document.createElement(t);try{n.setConfig(s)}catch(n){return console.error(t,n),e(n.message,s)}return n};if(!t||"object"!=typeof t||!t.type)return e("No type defined",t);var n=t.type;if(n=n.startsWith("custom:")?n.substr("custom:".length):"hui-"+n+"-card",customElements.get(n))return s(n,t);var i=e("Custom element doesn't exist: "+t.type+".",t);i.style.display="None";var r=setTimeout((function(){i.style.display=""}),2e3);return customElements.whenDefined(t.type).then((function(){clearTimeout(r),function(t,e,s,n){n=n||{},s=null==s?{}:s;var i=new Event(e,{bubbles:void 0===n.bubbles||n.bubbles,cancelable:Boolean(n.cancelable),composed:void 0===n.composed||n.composed});i.detail=s,t.dispatchEvent(i)}(i,"ll-rebuild",{},i)})),i},Mt=function(t,e){var s=e.value||e,n=e.attribute?t.attributes[e.attribute]:t.state;switch(e.operator||"=="){case"==":return n===s;case"<=":return n<=s;case"<":return n<s;case">=":return n>=s;case">":return n>s;case"!=":return n!==s;case"regex":return n.match(s);default:return!1}};const Tt="ontouchstart"in window||navigator.maxTouchPoints>0||navigator.msMaxTouchPoints>0;class At extends HTMLElement{constructor(){super(),this.holdTime=500,this.ripple=document.createElement("mwc-ripple"),this.timer=void 0,this.held=!1,this.cooldownStart=!1,this.cooldownEnd=!1}connectedCallback(){Object.assign(this.style,{position:"absolute",width:Tt?"100px":"50px",height:Tt?"100px":"50px",transform:"translate(-50%, -50%)",pointerEvents:"none"}),this.appendChild(this.ripple),this.ripple.primary=!0,["touchcancel","mouseout","mouseup","touchmove","mousewheel","wheel","scroll"].forEach(t=>{document.addEventListener(t,()=>{clearTimeout(this.timer),this.stopAnimation(),this.timer=void 0},{passive:!0})})}bind(t,e){if(t.longPress)return;t.longPress=!0,t.addEventListener("contextmenu",t=>{const e=t||window.event;return e.preventDefault&&e.preventDefault(),e.stopPropagation&&e.stopPropagation(),e.cancelBubble=!0,e.returnValue=!1,!1});const s=t=>{if(this.cooldownStart)return;let e,s;this.held=!1,t.touches?(e=t.touches[0].pageX,s=t.touches[0].pageY):(e=t.pageX,s=t.pageY),this.timer=window.setTimeout(()=>{this.startAnimation(e,s),this.held=!0},this.holdTime),this.cooldownStart=!0,window.setTimeout(()=>this.cooldownStart=!1,100)},n=s=>{this.cooldownEnd||["touchend","touchcancel"].includes(s.type)&&void 0===this.timer||(clearTimeout(this.timer),this.stopAnimation(),this.timer=void 0,this.held?t.dispatchEvent(new Event("ha-hold")):e.hasDoubleClick?1===s.detail?this.dblClickTimeout=window.setTimeout(()=>{t.dispatchEvent(new Event("ha-click"))},250):(clearTimeout(this.dblClickTimeout),t.dispatchEvent(new Event("ha-dblclick"))):t.dispatchEvent(new Event("ha-click")),this.cooldownEnd=!0,window.setTimeout(()=>this.cooldownEnd=!1,100))};t.addEventListener("touchstart",s,{passive:!0}),t.addEventListener("touchend",n),t.addEventListener("touchcancel",n),window.navigator.userAgent.match(/iPhone OS 13_/)||(t.addEventListener("mousedown",s,{passive:!0}),t.addEventListener("click",n))}startAnimation(t,e){Object.assign(this.style,{left:`${t}px`,top:`${e}px`,display:null}),this.ripple.disabled=!1,this.ripple.active=!0,this.ripple.unbounded=!0}stopAnimation(){this.ripple.active=!1,this.ripple.disabled=!0,this.style.display="none"}}customElements.define("long-press-restriction",At);const Dt=(t,e)=>{const s=(()=>{const t=document.body;if(t.querySelector("long-press-restriction"))return t.querySelector("long-press-restriction");const e=document.createElement("long-press-restriction");return t.appendChild(e),e})();s&&s.bind(t,e)},Rt=s((t={})=>e=>{Dt(e.committer.element,t)});let Vt=class extends ht{set hass(t){this._hass=t;const e=this.shadowRoot.querySelector("#card > *");e&&(e.hass=t)}getCardSize(){const t=this.shadowRoot.querySelector("#card > *");return t&&"function"==typeof(e=t).getCardSize?e.getCardSize():1;var e}setConfig(t){if(!t.card)throw new Error("Error in card configuration.");if(t.restrictions&&t.restrictions.pin&&!t.restrictions.pin.code)throw new Error("A pin code is required for pin restrictions");this._config=Object.assign({duration:5,action:"tap"},t)}shouldUpdate(t){const e=t.get("hass");return!(!t.has("config")&&e)||!!(this._config&&this._config.condition&&this._config.condition.entity)&&e.states[this._config.condition.entity]!==this._hass.states[this._config.condition.entity]}render(){return this._config&&this._hass?this._config.restrictions&&this._matchRestriction(this._config.restrictions.hide)?O``:O`
      <div>
        ${this._config.exemptions&&this._config.exemptions.some(t=>t.user===this._hass.user.id)||this._config.condition&&!Mt(this._hass.states[this._config.condition.entity],this._config.condition)?"":O`
              <div
              @ha-click=${this._handleClick}
              @ha-hold=${this._handleHold}
              @ha-dblclick=${this._handleDblClick}
              .longPress=${Rt({hasDoubleClick:"double_tap"===this._config.action})}
                @click=${this._handleClick}
                id="overlay"
                class="${pt({blocked:!!this._config.restrictions&&this._matchRestriction(this._config.restrictions.block)})}"
              >
                <ha-icon
                  icon="mdi:lock-outline"
                  id="lock"
                  class="${pt({row:Boolean(this._config.row)})}"
                ></ha-icon>
              </div>
            `}
        ${this.renderCard(this._config.card)}
      </div>
    `:O``}renderCard(t){const e=kt(t);return this._hass&&(e.hass=this._hass),O`
      <div id="card">
        ${e}
      </div>
    `}_matchRestriction(t){return t&&(!t.exemptions||!t.exemptions.some(t=>t.user===this._hass.user.id))&&(!t.condition||Mt(this._hass.states[t.condition.entity],t.condition))}_handleClick(){"tap"===this._config.action&&this._handleRestriction()}_handleDblClick(){"double_tap"===this._config.action&&this._handleRestriction()}_handleHold(){"hold"===this._config.action&&this._handleRestriction()}_handleRestriction(){const t=this.shadowRoot.getElementById("lock");if(this._config.restrictions){if(this._matchRestriction(this._config.restrictions.block))return this._config.restrictions.block.text&&alert(this._config.restrictions.block.text),t.classList.add("invalid"),void window.setTimeout(()=>{t&&t.classList.remove("invalid")},3e3);if(this._matchRestriction(this._config.restrictions.pin)){if(prompt(this._config.restrictions.pin.text||"Input pin code")!=this._config.restrictions.pin.code)return t.classList.add("invalid"),void window.setTimeout(()=>{t&&t.classList.remove("invalid")},3e3)}if(this._matchRestriction(this._config.restrictions.confirm)&&!confirm(this._config.restrictions.confirm.text||"Are you sure you want to unlock?"))return}const e=this.shadowRoot.getElementById("overlay");e.style.setProperty("pointer-events","none"),t.classList.add("hidden"),window.setTimeout(()=>{e.style.setProperty("pointer-events",""),t&&t.classList.remove("hidden")},1e3*this._config.duration)}static get styles(){return lt`
      :host {
        display: block;
        position: relative;
        --regular-lock-color: var(
          --restriction-regular-lock-color,
          var(--primary-text-color, #212121)
        );
        --success-lock-color: var(
          --restriction-success-lock-color,
          var(--primary-color, #03a9f4)
        );
        --blocked-lock-color: var(
          --restriction-blocked-lock-color,
          var(--error-state-color, #db4437)
        );
        --invalid-lock-color: var(
          --restriction-invalid--color,
          var(--error-state-color, #db4437)
        );
        --lock-margin-left: var(--restriction-lock-margin-left, 0px);
      }
      #overlay {
        align-items: flex-start;
        padding: 8px 7px;
        opacity: 0.5;
        position: absolute;
        left: 0;
        right: 0;
        top: 0;
        bottom: 0;
        z-index: 50;
        display: flex;
        color: var(--regular-lock-color);
      }
      .blocked {
        color: var(--blocked-lock-color) !important;
      }
      #lock {
        margin-left: var(--lock-margin-left);
      }
      .row {
        margin-left: 24px !important;
      }
      .hidden {
        visibility: hidden;
        opacity: 0;
        transition: visibility 0s 2s, opacity 2s linear;
        color: var(--success-lock-color);
      }
      @keyframes blinker {
        50% {
          opacity: 0;
        }
      }
      .invalid {
        animation: blinker 1s linear infinite;
        color: var(--invalid-lock-color);
      }
    `}};t([rt()],Vt.prototype,"_config",void 0),t([rt()],Vt.prototype,"_hass",void 0),Vt=t([(t=>e=>"function"==typeof e?((t,e)=>(window.customElements.define(t,e),e))(t,e):((t,e)=>{const{kind:s,elements:n}=e;return{kind:s,elements:n,finisher(e){window.customElements.define(t,e)}}})(t,e))("restriction-card")],Vt);
