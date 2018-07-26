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

import "./gauge.min.js";

// Use this when building to prod package
//import "canvas-gauges";

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
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this.__initTests();
    }
    /**
     * Renders the card 
     */
    _render() {
        // Create the container element 
        const elemContainer = document.createElement('div');
        elemContainer.id = 'container';
        elemContainer.width = this.config.gauge['width'];
        elemContainer.height = this.config.gauge['height'];

        const shadowHeight = (this.config.shadow_height) ? this.config.shadow_height : '7%';
        // The styles
        const style = `
            <style>
                #container {
                    width: ${elemContainer.width}px;
                    height: ${elemContainer.height}px;        
                    position: relative;
                    top: 0px;
                    overflow: hidden;
                    text-align: center;
                }
                .shadow {
                    width: 100%;
                    height: ${shadowHeight};
                    left: 0px;
                    bottom: 0;
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
                width: elemCanvas.width
            });
        }
        else if (this.config.gauge.type == 'radial-gauge') {
            gauge = new RadialGauge({
                renderTo: elemCanvas,
                height: elemCanvas.height,
                width: elemCanvas.width
            });
        }

        for (const key in this.config.gauge) {
            if (this.config.gauge.hasOwnProperty(key)) {
                gauge.options[key] = this.config.gauge[key];
            }
        }
        gauge.draw();

        elemContainer.appendChild(elemCanvas);

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
            elemContainer.appendChild(elemShadow);
        }

        elemContainer.onclick = this._click.bind(this);
        this.shadowRoot.appendChild(elemContainer);

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
        const state = hass.states[entityId].state;
        this._gauge['value'] = state;
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
        this._render();

    }

    getCardSize() {
        return 2;
    }

    /** 
     * Init testdata
     * I use this in my development environment to make a very simple mock of config/hass objects 
    */
    __initTests() {
        var test_config =
        {
            entity: 'sensor.temp',
            name: undefined,
            gauge: {}
        }; //, font_size: '1ev'

        test_config.gauge['type'] = 'radial-gauge';
        test_config.gauge['title'] = 'radial-gauge';
        test_config.gauge['width'] = 300;
        test_config.gauge['height'] = 300;
        test_config.gauge['units'] = 'Km/h';
        test_config.gauge['minValue'] = 0;
        test_config.gauge['maxValue'] = 220;
        test_config.gauge['startAngle'] = 90;
        test_config.gauge['ticksAngle'] = 180;
        test_config.gauge['valueBox'] = false;
        test_config.gauge['majorTicks'] = [0,20,40,60,80,100,120,140,160,180,200,220];
        test_config.gauge['minorTicks'] = 2;
        test_config.gauge['strokeTicks'] = true;
        test_config.gauge['highlights'] = [ 
            {
                "from": 160, 
                "to": 220, 
                "color": "rgba(200, 50, 50, .75)"
            } 
        ];
        test_config.gauge['colorPlate'] = '#fff';
        test_config.gauge['borderShadowWidth'] = 0;
        test_config.gauge['borderOuterWidth'] = 0;
        test_config.gauge['borderMiddleWidth'] = 0;
        test_config.gauge['borderInnerWidth'] = 0;
        test_config.gauge['borders'] = false;
        test_config.gauge['needleType'] = 'arrow';
        test_config.gauge['needleWidth'] = 2;
        test_config.gauge['needleCircleSize'] = 7;
        test_config.gauge['needleCircleOuter'] = true;
        test_config.gauge['needleCircleInner'] = false;
        test_config.gauge['animationDuration'] = 1500;
        test_config.gauge['animationRule'] = 'linear';
        test_config.gauge['value'] = '50';

        var test_hass = { states: [] };
        test_hass.states[test_config.entity] = { state: "15" };
        this.setConfig(test_config);

        this.hass = test_hass;
    }
}

window.customElements.define('canvas-gauge-card', CanvasGaugeCard);