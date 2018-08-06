/*!
 * The MIT License (MIT)
 *
 * Copyright (c) 2017 Tomas Hellström (https://github.com/helto4real/lovelace-custom-cards)
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

  /**
  * DO NOT USE THIS FILE IF USING SINGLE CARDS, USE THE VERSION UNDER 'dist' CATALOG!!!!
  */

import "./gauge.min.js";

/**
 * `canvas-gauge-card`
 * Lovelace element for displaying the canvas gauges at 
 * https://canvas-gauges.com/
 * 
 * If you like the gauges please support the original gauge devs.
 * 
 * Usage och card:
 *  - Copy this file 'canvas-guage-card.js' and 'gauge.min.js' to same folder in hass. 
 *  - Set the ui-lovelace.yaml, Include the canvas-guage-card.js and cofigure at minimum:
    * cards:
        - type: custom:canvas-gauge-card
            entity: sensor.temp_outside
            gauge:
            type: "linear-gauge"
            width: 120
            height: 400
    - Use the javascript properties withouth the ',' to configure properties under 'gauge'
    - Use name property to show the name att bottom of the card
    - See http://sss for docs
 */
class CanvasGaugeCard extends HTMLElement {
    /**
     * Renders the card 
     */
    _render() {
        const elemCardRoot = document.createElement('div');
        elemCardRoot.id = 'cardroot';
        // Create the container element 
        const elemContainer = document.createElement('div');
        elemContainer.id = 'container';
        elemContainer.width = this.config.card_width ? this.config.card_width : this.config.gauge['width'];
        elemContainer.height = this.config.card_height ? this.config.card_height : this.config.gauge['height'];

        const shadowHeight = (this.config.shadow_height) ? this.config.shadow_height : '10%';
        // The styles
        const style = `
            <style>
                #cardroot {
                    width: ${elemContainer.width}px;
                    height: calc(${elemContainer.height}px + ${this.config.shadow_bottom ? this.config.shadow_bottom : 0}px);
                    position: relative;
                }
                #container {
                    width: ${elemContainer.width}px;
                    height: ${elemContainer.height}px;        
                    position: relative;
                    top: 0px;
                    overflow: hidden;
                    text-align: center;
                }
                #innercontainer {
                    position: relative;
                    top: ${this.config.card_top ? this.config.card_top : 0}
                    left: ${this.config.card_left ? this.config.card_left : 0}
                }
                .shadow {
                    width: 100%;
                    height: ${shadowHeight};
                    left: 0px;
                    bottom: 0px;
                    background: rgba(0, 0, 0, 0.5);;
                    position: absolute;
                    }
                #state{
                    position: relative;
                    float: left;
                    top: 50%;
                    left: 50%;
                    color: white;
                    font-size: 100%;
                    transform: translate(-50%, -50%);
                }
            </style>
           
        `;
        this.shadowRoot.innerHTML = style;

        // We need an inner container so we can hide part of the gauge cause it
        // renders full circle even if only showing half gauge. 
        const elemInnerContainer = document.createElement('div');
        elemInnerContainer.id = 'innercontainer';

        // canvas element that the gauge will be drawn by the canvas gauge Lib
        const elemCanvas = document.createElement('canvas');
        elemCanvas.width = this.config.gauge['width'];
        elemCanvas.height = this.config.gauge['height'];

        // Have to do this cause some bug in library gauge.min.js dont display the gauge
        // keep this code for a while incase I need to activate it again...
        //var ctx = elemCanvas.getContext('2d');
        //ctx.fillStyle = 'black';
        //ctx.fillRect(0, 0, elemCanvas.width, elemCanvas.height);
        var gauge;
        if (this.config.gauge.type == 'linear-gauge') {
            gauge = new LinearGauge({
                renderTo: elemCanvas,
                height: elemCanvas.height,
                width: elemCanvas.width,
                value: 0
            });
        }
        else if (this.config.gauge.type == 'radial-gauge') {
            gauge = new RadialGauge({
                renderTo: elemCanvas,
                height: elemCanvas.height,
                width: elemCanvas.width,
                value: 0
            });
        }


        for (const key in this.config.gauge) {
            if (this.config.gauge.hasOwnProperty(key)) {
                gauge.options[key] = this.config.gauge[key];
            }
        }

        elemInnerContainer.appendChild(elemCanvas);

        elemContainer.appendChild(elemInnerContainer);
        elemCardRoot.appendChild(elemContainer);
        elemContainer.onclick = this._click.bind(this);
        if (this.config.name) {
            var elemShadow = document.createElement('div');
            elemShadow.className = 'shadow';

            var elemState = document.createElement('div');
            elemState.id = 'state';
            // Automatic font resize or set one
            var font_size = this.config.font_size ? this.config.font_size : `calc(${this.config.gauge['height']}px/22)`;
            elemState.style.fontSize = font_size;
            elemState.innerText = this.config.name;

            elemShadow.appendChild(elemState);
            elemCardRoot.appendChild(elemShadow);
        }

        this.shadowRoot.appendChild(elemCardRoot);
        this._gauge = gauge;
    }

    /**
     * onclick event for card, gets the enity info
     */
    _click() {
        this._fire('hass-more-info', { entityId: this.config.entity });
    }

    /**
     * Fires the event that opens the enity info
     */
    _fire(type, detail) {

        const event = new Event(type, {
            bubbles: true,
            cancelable: false,
            composed: true
        });
        event.detail = detail || {};
        this.shadowRoot.dispatchEvent(event);
        return event;
    }

    set hass(hass) {
        const entityId = this.config.entity;
        this._state = hass.states[entityId].state;
        this._gauge['value'] = this._state;
        this._gauge.draw(); // Have to call to redraw canvas
    }

    setConfig(config) {
        if (!config.entity) {
            throw new Error('You need to define an entity');
        }
        if (!config.gauge) {
            throw new Error('You need to define gauge and default gauge values');
        }
        if (!config.gauge.height) {
            throw new Error('You need to define gauge height');
        }
        if (!config.gauge.width) {
            throw new Error('You need to define gauge width');
        }
        if (!config.gauge.type) {
            throw new Error('You need to define gauge type');
        }
        if (!(config.gauge.type == 'linear-gauge' || config.gauge.type == 'radial-gauge')) {
            throw new Error('You need to define gauge type "linear-gauge" or "radial-gauge"');
        }
        this.config = config;

        // Fix initbug from the canvas lib that shows borders even if set to false
        if (typeof config.gauge.borders != typeof undefined && config.gauge.borders === false) {
            config.gauge['borderShadowWidth'] = 0;
            config.gauge['borderOuterWidth'] = 0;
            config.gauge['borderMiddleWidth'] = 0;
            config.gauge['borderInnerWidth'] = 0;
        }
        this._render();
    }

    getCardSize() {
        return 2;
    }

    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
    }

}

window.customElements.define('canvas-gauge-card', CanvasGaugeCard);
