/**
 * Javascript utility functions for the Pianocktail
 * 
 * @author Bertrand Verdu
 */

var touch = false;
var rb = 0;
var pb = 0;
var cb = 0;
var pos = 0;
var popup = 0;
var centi = 0;
var pumpmax = 0;
var num = 0;
var inglist = [];
// initialise les centièmes de sec
var running = 0;
var tim;
var chrono;
var port = parseInt(window.location.port);
var hostname = window.location.hostname;
if (isNaN(port)) {
    var wsUri = "ws://" + hostname + "/ws";
    var Uri = "http://" + hostname + "/";
} else {
    var Uri = "http://" + hostname + ":" + port + "/";
    var wsUri = "ws://" + hostname + ":" + port + "/ws";
}
var output;
var websocket;
var down = false;
var cur_x;
var cur_y;
var lastev;
var changelist = {};
var updatedrows = [];
var deleted = [];
var sysvalues = ["gpio", "gpio_in", "pwm", "stepper_ENA", "stepper_ENB", "stepper_A1", "stepper_A2", "stepper_B1", "stepper_B2", "motor_ENA", "motor_A", "motor_B"];

window.onbeforeunload = checkData;

// common utilities

function eventFire(el, etype) {
    if (el.fireEvent) {
        (el.fireEvent('on' + etype));
        console.log('on' + etype);
    } else {
        var evObj = document.createEvent('Events');
        console.log(etype);
        evObj.initEvent(etype, true, false);
        el.dispatchEvent(evObj);
    }
}

function getInputKeys() {
    document.addEventListener('keypress', function (event) {
        var nl = event.which == 13,
            // tb = event.which == 9,
            el = event.target;
        console.log(el);
        d = el.getAttribute('Id');
        r = el.getAttribute('onBlur');
        console.log("keydown");
        console.log("d= " + d);
        console.log("r= " + r);
        if (el.getAttribute('type') == "number") {
            var charCode = event.which || event.keyCode;
            var chr = String.fromCharCode(charCode);
            console.log(chr);
            if ((isNaN(chr)) && (!/[\x00-\x09\x0E-\x1F]/.test(chr))) {
                console.log("??");
                event.preventDefault();
                return false;
            }
        }
        if (r) {
            if (nl) {
                // save
                eval(r);
                console.log("validate: " + r)
                el.blur();
                event.preventDefault();
            } else {
                console.log("got " + d);
                //				if (updatedrows.indexOf("r" + rr) == -1) {
                //					console.log("updated: r" + rr);
                //					updatedrows.push("r" + rr);
                // el.blur();
                // event.preventDefault();
                //				}
                //				el.blur();
                switchEditButtons(1);
            }
        }
        return true;
    }, true);
};

function log(s) {
    document.getElementById('debug').innerHTML = 'value changed to: ' + s;
};

function checkData() {
    console.log("?!");
    if ((updatedrows.length > 0) && (popup == 0)) {
        console.log('tain tain !!!')
        return "Really quit?\nChanges will be lost.";
    }
    //	else{
    //		return 1;
    //	}

};

function isTouchDevice() {
    return "ontouchstart" in window;
}

// Main page utilities

function drawPiano() {
    output = document.getElementById('control_panel');
    if (output.getContext) {
        context = output.getContext("2d");
        context.fillStyle = "#3f3e3e";
        context.beginPath();
        context.moveTo(5, 0);
        context.lineTo(545, 0);
        context.quadraticCurveTo(595, 8, 600, 50);
        context.lineTo(600, 70);
        context.quadraticCurveTo(575, 180, 450, 198);
        context.quadraticCurveTo(282, 210, 185, 290);
        context.quadraticCurveTo(180, 297, 170, 300);
        context.lineTo(5, 300);
        context.quadraticCurveTo(0, 300, 0, 295);
        context.lineTo(0, 285);
        context.lineTo(45, 285);
        context.lineTo(45, 15);
        context.lineTo(0, 15);
        context.lineTo(0, 5);
        context.quadraticCurveTo(0, 0, 5, 0);
        context.fill();
        context.fillStyle = 'black';
        context.lineWidth = 7.5;
        context.beginPath();
        context.moveTo(8.8, 3.8);
        context.lineTo(545, 3.8);
        context.quadraticCurveTo(595, 8, 596.2, 50);
        context.lineTo(596.2, 70);
        context.quadraticCurveTo(575, 180, 450, 198);
        context.quadraticCurveTo(282, 210, 185, 290);
        context.quadraticCurveTo(180, 297, 170, 296.2);
        context.lineTo(8.8, 296.2);
        context.quadraticCurveTo(3.8, 296.2, 3.8, 296.2);
        context.lineTo(3.8, 288.8);
        context.lineTo(48.8, 288.8);
        context.lineTo(48.8, 11.2);
        context.lineTo(3.8, 11.2);
        context.lineTo(8.8, 3.8);
        context.quadraticCurveTo(0, 0, 5, 0);
        context.stroke();
    }
}

function writeToScreen(message) {
    if (pos >= 280) {
        pos = 0;
        context.clearRect(0, 0, output.width, output.height);
        drawPiano();
        drawPianokeyboard();
        context.fillStyle = "white";
        pos = 0;
    }
    context.font = '15px Calibri';
    pos = pos + 20;
    context.fillText(message, 70, pos);
}

function drawKeyboard() {
    canv = document.getElementById('piano_keyboard');
    touch = isTouchDevice()
    if (touch) {
        // writeToScreen("touch");
        canv.addEventListener('touchstart', notedown, true);
        canv.addEventListener('touchend', noteup, true);
        canv.addEventListener('touchmove', changenote, true);
    } else {
        // writeToScreen("desktop");
        canv.addEventListener('mousedown', notedown, true);
        canv.addEventListener('mouseup', noteup, true);
        canv.addEventListener('mousemove', changenote, true);
    }
    if (canv.getContext) {
        canvcontext = canv.getContext("2d");
        canvcontext.fillStyle = "white";
        canvcontext.strokeStyle = "black";
        canvcontext.fillRect(0, 0, 800, 120);
        canvcontext.fillStyle = "black"
        for (var i = 0; i < 800; i = i + 100) {
            canvcontext.moveTo(i + 100, 0);
            canvcontext.lineTo(i + 100, 120);
        }
        canvcontext.stroke();
        canvcontext.fillStyle = "black"
        canvcontext.fillRect(62, 0, 75, 60)
        canvcontext.fillRect(162, 0, 75, 60)
        canvcontext.fillRect(362, 0, 75, 60)
        canvcontext.fillRect(462, 0, 75, 60)
        canvcontext.fillRect(562, 0, 75, 60)
        canvcontext.fillRect(762, 0, 75, 60)
    }
}

function drawPianokeyboard() {
    context.fillStyle = 'white'
    context.fillRect(10, 15, 35, 270)
    context.beginPath();
    context.fillStyle = 'black';
    context.moveTo(45, 285)
    y = 285;
    tt = 1;
    dd = 0;
    for (var i = 0; i < 4; i++) {
        var dep = 45;
        var ar = 18;
        if (i == 1) {
            y = y - 4
            context.lineTo(dep, y);
            context.lineTo(ar, y)
            y = y - 4
            context.lineTo(ar, y)
            context.lineTo(dep, y)
            dd = 1
            if (y < 19) {
                i = 4;
            }
        }
        if (i == 2) {
            y = y - 2;
            context.lineTo(dep, y);
            context.lineTo(ar, y);
            y = y - 4;
            context.lineTo(ar, y);
            context.lineTo(dep, y);
            dd = 2;
            if (tt == 0) {
                i = 0;
                tt = 1;
                if (y < 19) {
                    i = 4;
                }
            }

        }
        if (i == 3) {
            y = y - 2;
            context.lineTo(dep, y);
            context.lineTo(ar, y);
            y = y - 4;
            context.lineTo(ar, y);
            context.lineTo(dep, y);
            dd = 3;
            tt = 0
            i = 0
            if (y < 19) {
                i = 4;
            }
        }

    }
    context.fill();

}

function webSocketManager() {
    /* websocket = new WebSocket(wsUri); */

    if ('WebSocket' in window) {
        websocket = new WebSocket(wsUri);
        console.log("ws ok")
    } else if ('MozWebSocket' in window) {
        websocket = new MozWebSocket(wsUri);
        console.log("ws ok")
    } else {
        // not supported
        console.log("ws ko")
        return;
    }
    websocket.onopen = function (evt) {
        onOpen(evt)
    };
    websocket.onclose = function (evt) {
        onClose(evt)
    };
    websocket.onmessage = function (evt) {
        onMessage(evt)
    };
    websocket.onerror = function (evt) {
        onError(evt)
    };
}

function wsinit() {
    rb = 0;
    pb = 0;
    cb = 0;
    pos = 0;
    drawPiano();
    webSocketManager();
    drawKeyboard();
    drawPianokeyboard();
}

function onOpen(evt) {
    if (typeof context != 'undefined') {
        context.fillStyle = "#008a00";
        writeToScreen("CONNECTED");
        setTimeout('doSend("status")', 50);
        console.log("Main page")
    }
    console.log("open")
}

function onClose(evt) {
    if (typeof context != 'undefined') {
        context.fillStyle = "#e81010";
        writeToScreen("DISCONNECTED");
    }
    delete websocket;
}

function onMessage(evt) {
    if (typeof context != 'undefined') {
        if (isNaN(evt.data)) {
            if ((evt.data == "Recording") || (evt.data == "Playing")) {
                rb = 1;
                pos = 0;
                context.clearRect(0, 0, output.width, output.height);
                drawPiano();
                drawPianokeyboard();
            }
            context.fillStyle = "white";
            writeToScreen(evt.data);
        } else {
            var note = parseInt(evt.data);
            if (note > 0) {
                context.fillStyle = "red";
                context.fillRect(18, (note - 25) * 2.50, 27, 4);
            } else {
                drawPianokeyboard();
            }
        }
    }
    /* websocket.close(); */
}

function onError(evt) {
    if (typeof context != 'undefined') {
        context.fillStyle = "#e81010";
        writeToScreen('ERROR: ' + evt.data);
    }
    console.log(evt.data)
}

function doSend(message) {
    /*
     * context.fillStyle = "#762086"; writeToScreen("Action: " + message);
     */
    websocket.send(message);
}

function drawCanvas() {
    var canvas = document.getElementById('control_panel')
    if (canvas.getContext) {
        var ctx = canvas.getContext("2d");
        ctx.fillStyle = "rgb(200,0,0)";
        ctx.fillRect(10, 10, 55, 50);
        ctx.fillStyle = "rgba(0, 0, 200, 0.5)";
        ctx.fillRect(30, 30, 55, 50);
    }

}

function buttondown(id) {
    doSend(id);
}

function buttonup(id) {
    doSend("-" + id);
}

function buttonclick(buttonid) {
    if (buttonid == "fullscreen") {
        console.log("fs");
        var doc = window.document;
        var elem = doc.body; //the element you want to make fullscreen

        var requestFullScreen = elem.requestFullscreen || elem.webkitRequestFullScreen || elem.mozRequestFullScreen || elem.msRequestFullscreen;
        var cancelFullScreen = doc.exitFullscreen || doc.webkitExitFullscreen || doc.mozCancelFullScreen || doc.msExitFullscreen;

        if (!(doc.fullscreenElement || doc.mozFullScreenElement || doc.webkitFullscreenElement || doc.msFullscreenElement)) {
            requestFullScreen.call(doc.documentElement);
        } else {
            cancelFullScreen.call(doc);
        }
        return false;
    }
    if (touch == false) {
        console.log("button " + buttonid + " clicked rb= " + rb);

        doSend(buttonid);
        if (buttonid == "stop") {
            if (rb == 1) {
                rb = 0;
            }
            if (pb == 1) {
                pb = 0;
            }
        }
        if (buttonid == "play") {
            if (pb == 0) {
                pb = 1;
            }

        }
        if (buttonid == "record") {
            if (rb == 0) {
                rb = 1;
            }

        }
    }
}

function buttondown(buttonid) {
    if (touch) {
        console.log("button " + buttonid + " touched rb= " + rb);
        if (buttonid == "fullscreen") {
            console.log("fs");
            var doc = window.document;
            var elem = doc.body; //the element you want to make fullscreen

            var requestFullScreen = elem.requestFullscreen || elem.webkitRequestFullScreen || elem.mozRequestFullScreen || elem.msRequestFullscreen;
            var cancelFullScreen = doc.exitFullscreen || doc.webkitExitFullscreen || doc.mozCancelFullScreen || doc.msExitFullscreen;

            if (!(doc.fullscreenElement || doc.mozFullScreenElement || doc.webkitFullscreenElement || doc.msFullscreenElement)) {
                requestFullScreen.call(doc.documentElement);
            } else {
                cancelFullScreen.call(doc);
            }
            return false;
        }
        doSend(buttonid);
        if (buttonid == "stop") {
            if (rb == 1) {
                rb = 0;
            }
            if (pb == 1) {
                pb = 0;
            }
        }
        if (buttonid == "play") {
            if (pb == 0) {
                pb = 1;
            }

        }
        if (buttonid == "record") {
            if (rb == 0) {
                rb = 1;
            }

        }
    }
}

function getevtPos(canva, evt) {
    // get canvas position
    var obj = canva;
    var top = 0;
    var left = 0;
    while (obj && obj.tagName != 'BODY') {
        top += obj.offsetTop;
        left += obj.offsetLeft;
        obj = obj.offsetParent;
    }

    // return relative mouse position
    if (isTouchDevice()) {
        var mouseX = evt.touches[0].clientX - left + window.pageXOffset;
        var mouseY = evt.touches[0].clientY - top + window.pageYOffset;
    } else {
        var mouseX = evt.clientX - left + window.pageXOffset;
        var mouseY = evt.clientY - top + window.pageYOffset;
    }
    return {
        x: mouseX,
        y: mouseY
    };
}

function changenote(ev) {

    /*
     * context.fillStyle = "white"; writeToScreen("note move");
     */
    ev.preventDefault();
    if (down == true) {
        var evtpos = getevtPos(canv, ev);
        ev._x = evtpos.x;
        ev._y = evtpos.y;
        if (ev._y < 1 || ev._y >= 119) {
            noteup(lastev);
            return;
        }
        if (ev._x < 1 || ev._x >= 799) {
            noteup(lastev);
            return;
        }
        if ((ev._y - cur_y) > 0) {
            if (cur_y = 60) {
                if ((ev._x - cur_x) <= 0 || (ev._x - cur_x) > 100) {
                    noteup(lastev);
                    notedown(ev);
                    return;
                }
            } else {
                if ((ev._x - cur_x) <= 0 || (ev._x - cur_x) > 50) {
                    noteup(lastev);
                    notedown(ev);
                    return;
                }
            }
        } else {
            if ((ev._x - cur_x) <= 0 || (ev._x - cur_x) > 50) {
                noteup(lastev);
                notedown(ev);
                return;
            }
        }
    }
};

function noteup(ev) {

    ev.preventDefault();
    down = false;
    canvcontext.fillStyle = "white";
    ev._x = lastev._x;
    ev._y = lastev._y;
    if (ev._y > 60) {
        if (ev._x < 100) {
            doSend("-84");
            canvcontext.fillRect(0, 60, 99, 100)
            canvcontext.fillRect(0, 0, 62, 60)
        } else if (ev._x < 200) {
            doSend("-86");
            canvcontext.fillRect(101, 60, 98, 100)
            canvcontext.fillRect(137, 0, 25, 60)
        } else if (ev._x < 300) {
            doSend("-88");
            canvcontext.fillRect(201, 60, 98, 100)
            canvcontext.fillRect(237, 0, 62, 60)
        } else if (ev._x < 400) {
            doSend("-89");
            canvcontext.fillRect(301, 60, 98, 100)
            canvcontext.fillRect(301, 0, 62, 60)
        } else if (ev._x < 500) {
            doSend("-91");
            canvcontext.fillRect(401, 60, 98, 100)
            canvcontext.fillRect(437, 0, 25, 60)
        } else if (ev._x < 600) {
            doSend("-93");
            canvcontext.fillRect(501, 60, 98, 100)
            canvcontext.fillRect(537, 0, 25, 60)
        } else if (ev._x < 700) {
            doSend("-95");
            canvcontext.fillRect(601, 60, 98, 100)
            canvcontext.fillRect(637, 0, 62, 60)
        } else {
            doSend("-96");
            canvcontext.fillRect(701, 60, 99, 100)
            canvcontext.fillRect(701, 0, 63, 60)
        }
    } else {
        if (ev._x < 62) {
            doSend("-84");
            canvcontext.fillRect(0, 60, 99, 100)
            canvcontext.fillRect(0, 0, 62, 60)
        } else if (ev._x < 137) {
            doSend("-85")
            canvcontext.fillStyle = "black"
            canvcontext.fillRect(62, 0, 75, 60)
        } else if (ev._x < 162) {
            doSend("-86")
            canvcontext.fillRect(101, 60, 98, 100)
            canvcontext.fillRect(137, 0, 25, 60)
        } else if (ev._x < 237) {
            doSend("-87")
            canvcontext.fillStyle = "black"
            canvcontext.fillRect(162, 0, 75, 60)
        } else if (ev._x < 300) {
            doSend("-88")
            canvcontext.fillRect(201, 60, 98, 100)
            canvcontext.fillRect(237, 0, 62, 60)
        } else if (ev._x < 362) {
            doSend("-89")
            canvcontext.fillRect(301, 60, 98, 100)
            canvcontext.fillRect(301, 0, 62, 60)
        } else if (ev._x < 437) {
            doSend("-90")
            canvcontext.fillStyle = "black"
            canvcontext.fillRect(362, 0, 75, 60)
        } else if (ev._x < 462) {
            doSend("-91")
            canvcontext.fillRect(401, 60, 98, 100)
            canvcontext.fillRect(437, 0, 25, 60)
        } else if (ev._x < 537) {
            doSend("-92")
            canvcontext.fillStyle = "black"
            canvcontext.fillRect(462, 0, 75, 60)
        } else if (ev._x < 562) {
            doSend("-93")
            canvcontext.fillRect(501, 60, 98, 100)
            canvcontext.fillRect(537, 0, 25, 60)
        } else if (ev._x < 637) {
            doSend("-94")
            canvcontext.fillStyle = "black"
            canvcontext.fillRect(562, 0, 75, 60)
        } else if (ev._x < 700) {
            doSend("-95")
            canvcontext.fillRect(601, 60, 98, 100)
            canvcontext.fillRect(637, 0, 62, 60)
        } else if (ev._x < 762) {
            doSend("-96")
            canvcontext.fillRect(701, 60, 99, 100)
            canvcontext.fillRect(701, 0, 63, 60)
        } else {
            doSend("-97")
            canvcontext.fillStyle = "black"
            canvcontext.fillRect(762, 0, 75, 60)
        }
    }
};


function notedown(ev) {

    console.log("down");
    ev.preventDefault();
    down = true
    canvcontext.fillStyle = "red"
    var evtpos = getevtPos(canv, ev);
    ev._x = evtpos.x;
    ev._y = evtpos.y;
    console.log(ev._y);
    lastev = ev;
    /*
     * context.fillStyle = "white"; writeToScreen("note down");
     * writeToScreen("X= " + ev._x.toString()); writeToScreen("Y= " +
     * ev._y.toString());
     */
    if (ev._y > 60) {
        cur_y = 60;
        if (ev._x < 100) {
            doSend("84");
            canvcontext.fillRect(0, 60, 99, 100);
            canvcontext.fillRect(0, 0, 62, 60);
            cur_x = 0;
        } else if (ev._x < 200) {
            doSend("86");
            canvcontext.fillRect(101, 60, 98, 100);
            canvcontext.fillRect(137, 0, 25, 60);
            cur_x = 100;
        } else if (ev._x < 300) {
            doSend("88");
            canvcontext.fillRect(201, 60, 98, 100);
            canvcontext.fillRect(237, 0, 62, 60);
            cur_x = 200;
        } else if (ev._x < 400) {
            doSend("89");
            canvcontext.fillRect(301, 60, 98, 100);
            canvcontext.fillRect(301, 0, 62, 60);
            cur_x = 300;
        } else if (ev._x < 500) {
            doSend("91");
            canvcontext.fillRect(401, 60, 98, 100);
            canvcontext.fillRect(437, 0, 25, 60);
            cur_x = 400;
        } else if (ev._x < 600) {
            doSend("93");
            canvcontext.fillRect(501, 60, 98, 100);
            canvcontext.fillRect(537, 0, 25, 60);
            cur_x = 500;
        } else if (ev._x < 700) {
            doSend("95");
            canvcontext.fillRect(601, 60, 98, 100);
            canvcontext.fillRect(637, 0, 62, 60);
            cur_x = 600;
        } else {
            doSend("96");
            canvcontext.fillRect(701, 60, 99, 100);
            canvcontext.fillRect(701, 0, 63, 60);
            cur_x = 700;
        }
    } else {
        cur_y = 0
        if (ev._x < 62) {
            doSend("84");
            canvcontext.fillRect(0, 60, 99, 100);
            canvcontext.fillRect(0, 0, 62, 60);
            cur_x = 0;
        } else if (ev._x < 137) {
            doSend("85");
            canvcontext.fillRect(62, 0, 75, 60);
            cur_x = 61;
        } else if (ev._x < 162) {
            doSend("86");
            canvcontext.fillRect(101, 60, 98, 100);
            canvcontext.fillRect(137, 0, 25, 60);
            cur_x = 100;
        } else if (ev._x < 237) {
            doSend("87");
            canvcontext.fillRect(162, 0, 75, 60);
            cur_x = 161;
        } else if (ev._x < 300) {
            doSend("88");
            canvcontext.fillRect(201, 60, 98, 100);
            canvcontext.fillRect(237, 0, 62, 60);
            cur_x = 200;
        } else if (ev._x < 362) {
            doSend("89");
            canvcontext.fillRect(301, 60, 98, 100)
            canvcontext.fillRect(301, 0, 62, 60)
            cur_x = 300;
        } else if (ev._x < 437) {
            doSend("90")
            canvcontext.fillRect(362, 0, 75, 60);
            cur_x = 361;
        } else if (ev._x < 462) {
            doSend("91");
            canvcontext.fillRect(401, 60, 98, 100);
            canvcontext.fillRect(437, 0, 25, 60);
            cur_x = 400;
        } else if (ev._x < 537) {
            doSend("92");
            canvcontext.fillRect(462, 0, 75, 60);
            cur_x = 462;
        } else if (ev._x < 562) {
            doSend("93");
            canvcontext.fillRect(501, 60, 98, 100);
            canvcontext.fillRect(537, 0, 25, 60);
            cur_x = 500;
        } else if (ev._x < 637) {
            doSend("94");
            canvcontext.fillRect(562, 0, 75, 60);
            cur_x = 561;
        } else if (ev._x < 700) {
            doSend("95");
            canvcontext.fillRect(601, 60, 98, 100);
            canvcontext.fillRect(637, 0, 62, 60);
            cur_x = 600;
        } else if (ev._x < 762) {
            doSend("96");
            canvcontext.fillRect(701, 60, 99, 100);
            canvcontext.fillRect(701, 0, 63, 60);
            cur_x = 700;
        } else {
            doSend("97")
            canvcontext.fillRect(762, 0, 75, 60);
            cur_x = 761;
        }
    }
};

// Config Page utilities

function setData(moddata) {

    console.log(moddata);
    if (moddata == "alc" | moddata == "debug") {
        changelist[moddata] = Math.abs(changelist[moddata] - 1);
    } else {
        changelist[moddata] = document.getElementById(moddata).value;
    }
    switchEditButtons(1);
    console.log(changelist[moddata]);
};

function getConf() {

    getInputKeys();
    touch = isTouchDevice();
    //	console.log("get_conf");
    pumpmax = 0;
    var req = new XMLHttpRequest();
    var params = 'client=web&action=config&command=getconf';
    req.onreadystatechange = function () {
        if ((req.readyState == 4) && (req.status == 200)) {
            var data = eval("(" + req.responseText + ")");
            sets = document.getElementById("configparams");
            childs = sets.childNodes;
            z = childs.length
            for (var y = 0; y < z; y++) {
                sets.removeChild(childs[0]);
            }
            var lab5 = document.createElement("label");
            /* lab5.for ="debug"; */
            lab5.innerHTML = "Debug";
            sets.appendChild(lab5);
            var dbg = document.createElement("input");
            dbg.id = "debug";
            dbg.type = "checkbox";
            dbg.value = data.debug;
            dbg.setAttribute("onClick", "setData(\"debug\")");
            if (data.debug == 1) {
                changelist['debug'] = 1;
                dbg.checked = "True";
            } else {
                changelist['debug'] = 0;
            }
            sets.appendChild(dbg);
            var lab0 = document.createElement("label");
            /* lab0.for ="alc"; */
            lab0.innerHTML = "Alcool ?";
            sets.appendChild(lab0);
            var alc = document.createElement("input");
            alc.id = "alc";
            alc.type = "checkbox";
            alc.value = data.alc;
            alc.setAttribute("onClick", "setData(\"alc\")");
            if (data.alc == 1) {
                changelist['alc'] = 1;
                alc.checked = "True";
            } else {
                changelist['alc'] = 0;
            }
            sets.appendChild(alc);
            var lab1 = document.createElement("label");
            /* lab1.for ="dep"; */
            lab1.innerHTML = "Pump offset :";
            sets.appendChild(lab1);
            var dep = document.createElement("input");
            dep.id = "dep";
            dep.type = "number";
            dep.size = "3";
            dep.step = "1";
            dep.value = data.dep;
            dep.setAttribute("onBlur", "setData(\"dep\")");
            sets.appendChild(dep);
            lab2 = document.createElement("label");
            /* lab2.for ="complex"; */
            lab2.innerHTML = "Complexity index :";
            sets.appendChild(lab2);
            var complex = document.createElement("input");
            complex.id = "complexind";
            complex.type = "number";
            complex.size = "3";
            complex.step = "0.1";
            complex.value = data.complexind;
            complex.setAttribute("onBlur", "setData(\"complexind\")");
            sets.appendChild(complex);
            lab3 = document.createElement("label");
            /* lab3.for ="tristesse"; */
            lab3.innerHTML = "Sadness index :";
            sets.appendChild(lab3);
            var tristesse = document.createElement("input");
            tristesse.id = "tristind"
            tristesse.type = "number";
            tristesse.size = "3";
            tristesse.step = "0.1";
            tristesse.value = data.tristind;
            tristesse.setAttribute("onBlur", "setData(\"tristind\")");
            sets.appendChild(tristesse);
            lab4 = document.createElement("label");
            /* lab4.for ="nervous"; */
            lab4.innerHTML = "Nervosity index :";
            sets.appendChild(lab4);
            var nervous = document.createElement("input");
            nervous.id = "nervind";
            nervous.type = "number";
            nervous.size = "3";
            nervous.step = "0.1";
            nervous.value = data.nervind;
            nervous.setAttribute("onBlur", "setData(\"nervind\")");
            sets.appendChild(nervous);
            lab5 = document.createElement("label");
            /* lab5.for ="factor"; */
            lab5.innerHTML = "Qty ratio :";
            sets.appendChild(lab5);
            var factor = document.createElement("input");
            factor.id = "factor";
            factor.type = "number";
            factor.size = "3";
            factor.step = "0.1";
            factor.value = data.factor;
            factor.setAttribute("onBlur", "setData(\"factor\")");
            sets.appendChild(factor);
            listIn = document.getElementById("midiInList");
            listIn.options.length = 0;
            for (var i = 0; i < data.inports.length; i++) {
                var message = data.inports[i][0] + ":" + data.inports[i][1] +
                    " " + data.inports[i][2];
                var pre = document.createElement("option");
                pre.value = i
                pre.innerHTML = message;
                listIn.appendChild(pre)
            }
            listOut = document.getElementById("midiOutList");
            listOut.options.length = 0;
            for (var i = 0; i < data.outports.length; i++) {
                var message = data.outports[i][0] + ":" + data.outports[i][1] +
                    " " + data.outports[i][2];
                var pre = document.createElement("option");
                pre.value = i
                pre.innerHTML = message;
                listOut.appendChild(pre)
            }
            table = document.getElementById("tableSystem");
            childs = table.childNodes;
            z = childs.length;
            for (var y = 0; y < z; y++) {
                table.removeChild(childs[0]);
            }
            for (var i = 0; i < data.systemports.length; i++) {
                with(data.systemports[i]) {
                    // newPumpLine(name, deg, pump, time)
                    newSysLine(num, type, description, bus, channel, ratio,
                        funct, avail)
                }

            }
            //			newsysLine();
            // switchEditButtons(0);

        }
        switchEditButtons(0);
        updatedrows = [];
        deleted = [];
    };
    console.log(Uri);
    req.open('POST', Uri);
    console.log("post");
    req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    req.setRequestHeader("Content-length", params.length);
    console.log(params);
    req.send(params);
    webSocketManager();
};

function newSysLine(num, type, description, bus, channel, ratio, funct, avail) {
    //	console.log(avail);
    var table = document.getElementById("tableSystem");
    var childs = table.getElementsByTagName("tr");
    var z = childs.length;
    var row = document.createElement("tr");
    row.setAttribute("id", "r" + z);
    var c = 0;
    var cell = document.createElement("td");
    if (num == undefined) {
        var ipt = document.createElement("input");
        ipt.setAttribute("value", pumpmax + 1);
    } else {
        var ipt = document.createElement("div");
        ipt.setAttribute("contenteditable", false);
        txt = document.createTextNode(num);
        if (num > pumpmax) {
            pumpmax = num;
        }
        ipt.appendChild(txt);
    }
    ipt.setAttribute("tabindex", "0");
    ipt.setAttribute("id", z + "".concat(c));
    c += 1;
    ipt.setAttribute("onBlur", "changedCell(\"".concat("r" + z + "\")"));
    // ipt.setAttribute("onBlur", "yo");
    cell.appendChild(ipt);
    row.appendChild(cell);
    var cell = document.createElement("td");
    var par = document.createElement("p");
    var lab = document.createElement("label");
    lab.setAttribute("class", "custom-select");
    var ipt = document.createElement("select");
    ipt.setAttribute("contenteditable", false);
    ipt.setAttribute("tabindex", "0");
    ipt.setAttribute("onBlur", "changedCell(\"".concat("r" + z + "\")"));
    ipt.setAttribute("id", z + "".concat(c));
    ipt.setAttribute("name", "".concat(z + c));
    c += 1;
    if (type == undefined) {
        var defval = "fake_gpio";
    } else {
        var defval = type;
    }
    for (var i = 0; i < sysvalues.length; i++) {
        var opt = document.createElement("option");
        opt.setAttribute("value", sysvalues[i]);
        opt.appendChild(document.createTextNode(sysvalues[i]));
        if (sysvalues[i] == defval) {
            opt.setAttribute("selected", "selected");
        }
        ipt.appendChild(opt)
    }
    lab.appendChild(ipt);
    par.appendChild(lab);
    cell.appendChild(par);
    row.appendChild(cell);
    var cell = document.createElement("td");
    var ipt = document.createElement("input");
    ipt.setAttribute("tabindex", "0");
    ipt.setAttribute("onBlur", "changedCell(\"".concat("r" + z + "\")"));
    ipt.setAttribute("id", z + "".concat(c));
    c += 1;
    if (description == undefined) {
        ipt.setAttribute("value", "New");
    } else {
        ipt.setAttribute("value", description);
    }
    cell.appendChild(ipt);
    row.appendChild(cell);
    var cell = document.createElement("td");
    var ipt = document.createElement("input");
    ipt.setAttribute("tabindex", "0");
    ipt.setAttribute("onBlur", "changedCell(\"".concat("r" + z + "\")"));
    ipt.setAttribute("id", z + "".concat(c));
    c += 1;
    if (bus == undefined) {
        ipt.setAttribute("value", "0x20");
    } else {
        ipt.setAttribute("value", bus);
    }
    cell.appendChild(ipt);
    row.appendChild(cell);
    var cell = document.createElement("td");
    var ipt = document.createElement("input");
    ipt.setAttribute("type", "number");
    ipt.setAttribute("tabindex", "0");
    ipt.setAttribute("onBlur", "changedCell(\"".concat("r" + z + "\")"));
    ipt.setAttribute("id", z + "".concat(c));
    c += 1;
    if (channel == undefined) {
        ipt.setAttribute("value", pumpmax);
        pumpmax += 1;
    } else {
        ipt.setAttribute("value", channel);
    }
    cell.appendChild(ipt);
    row.appendChild(cell);
    var cell = document.createElement("td");
    var ipt = document.createElement("input");
    ipt.setAttribute("type", "number");
    ipt.setAttribute("tabindex", "0");
    ipt.setAttribute("onBlur", "changedCell(\"".concat("r" + z + "\")"));
    ipt.setAttribute("id", z + "".concat(c));
    c += 1;
    if (ratio == undefined) {
        ipt.setAttribute("value", "1.0");
    } else {
        ipt.setAttribute("value", ratio);
    }
    cell.appendChild(ipt);
    row.appendChild(cell);
    var cell = document.createElement("td");
    var ipt = document.createElement("input");
    ipt.setAttribute("tabindex", "0");
    ipt.setAttribute("onBlur", "changedCell(\"".concat("r" + z + "\")"));
    ipt.setAttribute("id", z + "".concat(c));
    c += 1;
    if (funct == undefined) {
        ipt.setAttribute("value", "None");
    } else {
        ipt.setAttribute("value", funct);
    }
    cell.appendChild(ipt);
    row.appendChild(cell);
    var cell = document.createElement("td");
    cell.setAttribute("contenteditable", false);
    //	var btn = document.createElement("Button");
    //	btn.setAttribute("contenteditable", false);
    cell.setAttribute("id", num);
    cell.setAttribute("style", "background-color: green; -moz-user-select: none; -webkit-user-select: none; -ms-user-select:none; user-select: none; width: 80px;");
    cell.setAttribute("unselectable", "on")
    cell.setAttribute("onselectstart", "return false;")
    if (touch) {
        cell.setAttribute("onTouchStart", "sysTest(1, ".concat(num + ")"));
        cell.setAttribute("onTouchEnd", "sysTest(0, ".concat(num + ")"));
    } else {
        cell.setAttribute("onMouseDown", "sysTest(1, ".concat(num + ")"));
        //		cell.setAttribute("onMouseDown", "doSend(\"test ".concat(" " + num
        //				+ "\")"));
        cell.setAttribute("onMouseUp", "sysTest(0, ".concat(num + ")"));
    }
    txt = document.createTextNode("Test");
    cell.appendChild(txt);
    //	cell.appendChild(btn);
    row.appendChild(cell);
    table.appendChild(row);
};

function sysTest(type, row) {
    //	console.log(type);
    //	console.log(row);
    if (type == 1) {
        doSend("test ".concat(" " + row));
        var cell = document.getElementById(row);
        cell.setAttribute("style",
            "background-color: red; -moz-user-select: none; -webkit-user-select: none; -ms-user-select:none; user-select: one; width: 80px;");
    } else {
        doSend("test ".concat("-" + row));
        var cell = document.getElementById(row);
        cell.setAttribute(
            "style",
            "background-color: green; -moz-user-select: none; -webkit-user-select: none; -ms-user-select:none; user-select: one; width: 80px;");
    }


}

function setConf() {

    req = new XMLHttpRequest();
    parms = {};
    parms.client = "web";
    parms.action = "config";
    parms.command = "setconf";
    var rows = []
    for (var i = 0; i < updatedrows.length; i++) {
        key = updatedrows[i];
        console.log(key);
        var t = document.getElementById(key);
        var y = 0;
        console.log(t);
        var pcell = document.getElementById(key).getElementsByTagName("div");
        var tcell = document.getElementById(key).getElementsByTagName("select");
        var type = tcell[0].value;
        var icells = document.getElementById(key).getElementsByTagName("input");
        if (pcell[0] != undefined) {
            var pump = pcell[0].innerHTML;
            //			updrow.pump = pump;
        } else {
            y += 1;
            var pump = icells[0].value;
        }
        if ((pump != undefined) && (icells[0 + y].innerHTML != "New")) {
            updrow = {};
            updrow.pump = pump;
            updrow.type = type;
            updrow.description = icells[0 + y].value;
            updrow.bus = icells[1 + y].value;
            updrow.chan = icells[2 + y].value;
            updrow.ratio = icells[3 + y].value;
            updrow.fct = icells[4 + y].value;
            rows.push(updrow);
        }
    }
    changelist['rows'] = rows;
    parms.params = changelist;
    req.onreadystatechange = function () {
        if ((req.readyState == 4) && (req.status == 200)) {
            var data = eval("(" + req.responseText + ")");
            if (data.updated == "1") {
                console.log("update = OK");
                getConf();
            } else {
                alert("This relay is in use");
                updatedrows = [];
                getConf();
            }
        }

    };
    params = JSON.stringify(parms);
    req.open('POST', Uri);
    req.setRequestHeader("Content-type", "application/json");
    req.setRequestHeader("Content-length", params.length);
    console.log(params);
    req.send(params);
};

// Ingredients page utilities

function delPump(row, name) {
    if (updatedrows.indexOf(row) == -1) {
        var tabbody = document.getElementById("ingredients");
        console.log(row);
        console.log(name);
        var n = tabbody.childNodes[parseInt(row)];
        tabbody.removeChild(n);
        deleted.push(name);
        switchEditButtons(1);
    }

};

function switchEditButtons(enable) {
    if (enable == 0) {
        chbut = document.getElementById("chgbuttons").getElementsByTagName(
            "button");
        for (var i = 0; i < chbut.length; i++) {
            chbut[i].setAttribute("disabled", "1");
        }
    } else {
        chbut = document.getElementById("chgbuttons").getElementsByTagName(
            "button");
        for (var i = 0; i < chbut.length; i++) {
            chbut[i].removeAttribute("disabled");
        }
    }

}

function chronometer(centi) {
    var chrono = document.getElementById("chrono");
    centi = centi + 100; // incrémentation des centièmes de seconde
    chrono.innerHTML = centi;
    tim = setTimeout('chronometer(' + centi + ')', 100);
};

function startchrono(pump) { // fonction qui remet les compteurs à 0
    running = 1;
    var centi = 0;
    req = new XMLHttpRequest();
    params = 'client=web&action=pump&command=b' + pump;
    req.onreadystatechange = function () {
        console.log(req.responseText)
        if ((req.readyState == 4) && (req.status == 200)) {
            if (req.responseText == '0') {
                var btn = document.getElementById(pump);
                btn.setAttribute("style", "background: red;color: white;")
                chronometer(centi);
            }
        }
    }
    req.open('POST', Uri);
    req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    req.setRequestHeader("Content-length", params.length);
    req.send(params);
}

function stopchrono(row) {
    var lin = document.getElementById(row);
    var pump = lin.getElementsByTagName("input")[1].value;
    if (running == 1) {
        var req = new XMLHttpRequest();
        var params = 'client=web&action=pump&command=s' + pump;
        req.onreadystatechange = function () {
            console.log(req.responseText)
            if ((req.readyState == 4) && (req.status == 200)) {
                if (req.responseText == '0') {
                    clearTimeout(tim);
                    btn = document.getElementById(pump);
                    btn.setAttribute("style", "color: black;")
                    running = 0;
                }
            }
        }
        req.open('POST', Uri);
        req.setRequestHeader("Content-type",
            "application/x-www-form-urlencoded");
        req.setRequestHeader("Content-length", params.length);
        req.send(params);
    } else {
        startchrono(pump);
    }

}

function saveRow(row) {
    var lin = document.getElementById(row);
    var cells = lin.getElementsByTagName("input");
    cells[2].value = document.getElementById("chrono").innerHTML;
    if (updatedrows.indexOf(row) == -1) {
        // console.log(row)
        updatedrows.push(row);
        switchEditButtons(1);
    }

}

/*
 * function writeToScreen(message) { var pre = document.createElement("p");
 * pre.style.wordWrap = "break-word"; pre.innerHTML = message;
 * output.appendChild(pre); }
 */

function setRow(num) {
    lin = document.getElementById("r" + num);
    req = new XMLHttpRequest();
    params = '@client=web&@action=config&@command=setIngredients(' + jsondata + ')';
}

function changedCell(row) {
    //	console.log("kikouu" + row);
    //	console.log(updatedrows)
    if (updatedrows.indexOf(row) == -1) {
        //		console.log(row);
        updatedrows.push(row);
        switchEditButtons(1);
    }
}

function getPumps() {
    getInputKeys();
    var lists = ["alcools"]
    var alclist = []
    req = new XMLHttpRequest();
    params = 'client=web&action=config&command=getIngredients';
    req.onreadystatechange = function () {
        /* console.log(req.responseText) */
        if ((req.readyState == 4) && (req.status == 200)) {
            updatedrows = []
            deleted = []
            var data = eval("(" + req.responseText + ")");
            var alcool = document.getElementById("alcools");
            tabbody = document.getElementById("ingredients");
            childs = tabbody.childNodes;
            z = childs.length
            for (var y = 0; y < z; y++) {
                tabbody.removeChild(childs[0]);
            }
            for (var i = 0; i < data.Ingredients.length; i++) {
                if (data.Ingredients[i].name != 'EMPTY') {
                    with(data.Ingredients[i]) {
                        // newPumpLine(name, deg, pump, time)
                        newPumpLine(id, name, deg, pump, qty, time)
                    }
                }

            }
            for (var k = 0; k < alclist.length; k++) {
                var opt = document.createElement("option");
                opt.value = alclist[k];
                console.log(opt.value)
                alcool.appendChild(opt);
            }

        }
        switchEditButtons(0);

    };
    req.open('POST', Uri);
    req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    req.setRequestHeader("Content-length", params.length);
    req.send(params);
};

function sendPumps() {

    var updated = [];
    if (updatedrows.length > 0) {
        for (var i = 0; i < updatedrows.length; i++) {
            key = updatedrows[i];
            console.log(key);
            rw = document.getElementById(key).getElementsByTagName("input");
            if (rw.length > 4) {
                name = rw[0].value;
                console.log(name);
                if (name != 'New') {
                    var updrow = {};
                    updrow.name = name;
                    updrow.alcool = rw[1].value;
                    updrow.pump = rw[2].value;
                    updrow.time = rw[3].value;
                    updrow.qty = rw[4].value;
                    updated.push(updrow);
                }
            } else {
                name = document.getElementById(key).getElementsByTagName("div")[0].innerHTML;
                console.log(name);
                var updrow = {};
                updrow.name = name;
                updrow.alcool = rw[0].value;
                updrow.pump = rw[1].value;
                updrow.time = rw[2].value;
                updrow.qty = rw[3].value;
                updated.push(updrow);
            }
        }
        req = new XMLHttpRequest();
        parms = {};
        parms.client = "web";
        parms.action = "config";
        parms.command = "setIngredients";
        if (updated.length > 0) {
            parms.params = updated;
        } else {
            parms.params = "0"
        }
        req.onreadystatechange = function () {
            if ((req.readyState == 4) && (req.status == 200)) {
                var data = eval("(" + req.responseText + ")");
                if (data.updated == "1") {
                    console.log("update = OK");
                    getPumps();
                } else {
                    console.log("update = KO");
                    alert("The choosen pump is not configured !");
                }
            }

        };
        params = JSON.stringify(parms);
        console.log(parms);
        req.open('POST', Uri);
        req.setRequestHeader("Content-type", "application/json");
        req.setRequestHeader("Content-length", params.length);
        req.send(params);
    }
    if (deleted.length > 0) {
        req = new XMLHttpRequest();
        parms = {};
        var updated = []
        for (var i = 0; i < deleted.length; i++) {
            var updrow = {};
            updrow.id = deleted[i];
            updated.push(updrow);
        }
        parms.client = "web";
        parms.action = "config";
        parms.command = "delIngredients";

        parms.params = updated;
        req.onreadystatechange = function () {
            if ((req.readyState == 4) && (req.status == 200)) {
                var data = eval("(" + req.responseText + ")");
                if (data.updated == "1") {
                    console.log("update = OK");
                }
                getPumps();
            }

        };
        params = JSON.stringify(parms);
        console.log(parms);
        req.open('POST', Uri);
        req.setRequestHeader("Content-type", "application/json");
        req.setRequestHeader("Content-length", params.length);
        req.send(params);
    }

};

function newPumpLine(id, name, deg, pump, qty, tim) {
    tabbody = document.getElementById("ingredients");
    childs = tabbody.getElementsByTagName("tr");
    z = childs.length;
    row = document.createElement("tr");
    row.setAttribute("id", "r" + z);
    var c = 0
    cell = document.createElement("td");
    if (name == undefined) {
        ipt = document.createElement("input");
        ipt.setAttribute("tabindex", "0");
        ipt.setAttribute("class", "desc");
        ipt.setAttribute("onBlur", "changedCell(\"".concat("r" + z + "\")"));
        ipt.setAttribute("value", "New");
    } else {
        ipt = document.createElement("div");
        ipt.setAttribute("contenteditable", false);
        ipt.setAttribute("class", "desc");
        ipt.setAttribute("onBlur", "changedCell(\"".concat("r" + z + "\")"));
        txt = document.createTextNode(name);
        ipt.appendChild(txt);
    }
    c += 1;
    cell.appendChild(ipt);
    row.appendChild(cell);
    cell = document.createElement("td");
    var ipt = document.createElement("input");
    ipt.setAttribute("type", "number");
    ipt.setAttribute("tabindex", "0");
    ipt.setAttribute("id", z + "".concat(c));
    c += 1;
    ipt.setAttribute("onBlur", "changedCell(\"".concat("r" + z + "\")"));
    if (deg == undefined) {
        ipt.setAttribute("value", 0);
    } else {
        ipt.setAttribute("value", deg);
    }
    cell.appendChild(ipt);
    row.appendChild(cell);
    cell = document.createElement("td");
    var ipt = document.createElement("input");
    ipt.setAttribute("type", "number");
    ipt.setAttribute("tabindex", "0");
    ipt.setAttribute("id", z + "".concat(c));
    c += 1;
    ipt.setAttribute("onBlur", "changedCell(\"".concat("r" + z + "\")"));
    if (pump == undefined) {
        ipt.setAttribute("value", 0);
    } else {
        ipt.setAttribute("value", pump);
    }
    cell.appendChild(ipt);
    row.appendChild(cell);
    cell = document.createElement("td");
    var ipt = document.createElement("input");
    ipt.setAttribute("type", "number");
    ipt.setAttribute("tabindex", "0");
    ipt.setAttribute("id", z + "".concat(c));
    c += 1;
    ipt.setAttribute("onBlur", "changedCell(\"".concat("r" + z + "\")"));
    if (tim == undefined) {
        ipt.setAttribute("value", 0);
    } else {
        ipt.setAttribute("value", tim);
    }
    cell.appendChild(ipt);
    row.appendChild(cell);
    cell = document.createElement("td");
    var ipt = document.createElement("input");
    ipt.setAttribute("type", "number");
    ipt.setAttribute("tabindex", "0");
    ipt.setAttribute("id", z + "".concat(c));
    c += 1;
    ipt.setAttribute("onBlur", "changedCell(\"".concat("r" + z + "\")"));
    if (qty == undefined) {
        ipt.setAttribute("value", 100);
    } else {
        ipt.setAttribute("value", qty);
    }
    cell.appendChild(ipt);
    row.appendChild(cell);
    var cell = document.createElement("td");
    cell.setAttribute("contenteditable", false);
    var btn = document.createElement("button");
    btn.setAttribute("id", pump);
    btn.setAttribute("onClick", "stopchrono(\"".concat("r" + z + "\")"));
    var txt = document.createTextNode("Start/Stop");
    btn.appendChild(txt);
    cell.appendChild(btn);
    row.appendChild(cell);
    var cell = document.createElement("td");
    cell.setAttribute("contenteditable", false);
    var btn = document.createElement("button");
    btn.setAttribute("onClick", "saveRow(\"".concat("r" + z + "\")"));
    var txt = document.createTextNode("Save");
    btn.appendChild(txt);
    cell.appendChild(btn);
    row.appendChild(cell);
    var cell = document.createElement("td");
    cell.setAttribute("contenteditable", false);
    var btn = document.createElement("button");
    btn.setAttribute("onClick", "delPump(".concat(z + ", ".concat(id) + ")"));
    var txt = document.createTextNode("X");
    btn.appendChild(txt);
    cell.appendChild(btn);
    row.appendChild(cell);
    tabbody.appendChild(row);
};

// Recipe Page Utilities

function testRow(row, name) {
    req = new XMLHttpRequest();
    params = 'client=web&action=cocktail&command=' + name;
    req.onreadystatechange = function () {
        console.log(req.responseText)
    }
    req.open('POST', Uri);
    req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    req.setRequestHeader("Content-length", params.length);
    req.send(params);
};

function delCocktail(row, name) {
    if (updatedrows.indexOf(row) == -1) {
        var tabbody = document.getElementById("recipes");
        console.log(row);
        console.log(name);
        var n = tabbody.childNodes[parseInt(row)];
        tabbody.removeChild(n);
        deleted.push(name);
        switchEditButtons(1);
    }

};

function sendRecipes() {
    if (updatedrows.length > 0) {
        var updated = []
        for (var i = 0; i < updatedrows.length; i++) {
            key = updatedrows[i];
            console.log(key);
            rw = document.getElementById(key).getElementsByTagName("input");
            var x = 0;
            console.log(rw.length);
            if (rw.length > 5) {
                name = rw[0].value;
            } else {
                x += 1;
                name = document.getElementById("name" + key).innerHTML;
            }
            console.log(name);
            if (name != undefined) {
                var updrow = {};
                updrow.name = name;
                updrow.description = rw[1 - x].value;
                updrow.score1 = rw[2 - x].value;
                updrow.score2 = rw[3 - x].value;
                updrow.score3 = rw[4 - x].value;
                updrow.id = rw[5 - x].value;
                updated.push(updrow);
            }
        }
        req = new XMLHttpRequest();
        parms = {};
        parms.client = "web";
        parms.action = "config";
        parms.command = "setCocktails";
        parms.params = updated;
        req.onreadystatechange = function () {
            if ((req.readyState == 4) && (req.status == 200)) {
                var data = eval("(" + req.responseText + ")");
                if (data.updated == "1") {
                    console.log("update = OK");

                }
                getRecipes();
            }

        };
        params = JSON.stringify(parms);
        console.log(parms);
        req.open('POST', Uri);
        req.setRequestHeader("Content-type", "application/json");
        req.setRequestHeader("Content-length", params.length);
        req.send(params);
    }
    if (deleted.length > 0) {
        req = new XMLHttpRequest();
        parms = {};
        var updated = []
        for (var i = 0; i < deleted.length; i++) {
            var updrow = {};
            updrow.id = deleted[i];
            updated.push(updrow);
        }
        parms.client = "web";
        parms.action = "config";
        parms.command = "delCocktails";

        parms.params = updated;
        req.onreadystatechange = function () {
            if ((req.readyState == 4) && (req.status == 200)) {
                var data = eval("(" + req.responseText + ")");
                if (data.updated == "1") {
                    console.log("update = OK");
                }
                getRecipes();
            }

        };
        params = JSON.stringify(parms);
        console.log(parms);
        req.open('POST', Uri);
        req.setRequestHeader("Content-type", "application/json");
        req.setRequestHeader("Content-length", params.length);
        req.send(params);
    }

};

function ingList() {

    req = new XMLHttpRequest();
    params = 'client=web&action=config&command=getinglist';
    req.onreadystatechange = function () {
        console.log('?');
        if ((req.readyState == 4) && (req.status == 200)) {
            console.log('!');
            data = eval("(" + req.responseText + ")");
            console.log(data);
            inglist = data.list;
            console.log(inglist.length);
        }
    }
    req.open('POST', Uri);
    req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    req.setRequestHeader("Content-length", params.length);
    req.send(params);
}

function getIng(cocktail, cock_nam) {
    console.log("getIng: " + cocktail);
    req = new XMLHttpRequest();
    params = 'client=web&action=config&command=getcocking&param=' + cocktail;
    req.onreadystatechange = function () {
        if ((req.readyState == 4) && (req.status == 200)) {
            getInputKeys()
            popup = 1;
            data = eval("(" + req.responseText + ")");
            inglist = data.list;
            var editcock = document.getElementById("ing");
            var childs = editcock.childNodes;
            var z = childs.length
            for (var y = 0; y < z; y++) {
                editcock.removeChild(childs[0]);
            }
            num = 0;
            document.getElementById("popup_title").innerHTML = "Edit ".concat(cock_nam);
            var row = document.createElement("form");
            row.setAttribute("id", "c".concat(cocktail));
            row.setAttribute("action", Uri);
            row.setAttribute("method", "post");
            row.setAttribute("target", "_parent");
            editcock.appendChild(row);
            //			row.setAttribute("enctype", "application/json")
            for (var i = 0; i < data.ingredients.length; i++) {
                with(data.ingredients[i]) {
                    newIngLine("c".concat(cocktail), id, name, qty);
                }
            }
            //			var smt = document.createElement("input");
            //			smt.setAttribute("type", "submit");
            //			smt.setAttribute("formation", Uri);
            //			row.appendChild(smt);
            var btn = document.createElement("button");
            btn.setAttribute("id", "add");
            var txt = document.createTextNode("Add");
            btn.appendChild(txt);
            btn.setAttribute("OnClick", "newIngLine(\"c".concat(cocktail + "\", 0, \"New\", 0);"));
            btn.setAttribute("type", "button")
            editcock.appendChild(btn);
            var btn = document.createElement("button");
            btn.setAttribute("id", "post");
            var txt = document.createTextNode("Save");
            btn.appendChild(txt);
            btn.setAttribute("OnClick", "postIng(\"c".concat(cocktail + "\");"));
            //			btn.setAttribute("type", "button")
            editcock.appendChild(btn);
            // newIngLine(editcock, 0, 'New', 0);
            console.log(inglist);
        }
    }
    req.open('POST', Uri);
    req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    req.setRequestHeader("Content-length", params.length);
    req.send(params);
};

function postIng(row_id) {
    console.log("row".concat(row_id));
    f = document.getElementById(row_id);
    //	inf = new FormData(f);
    ////	inf = new FormData();
    //	inf.append("client", "web");
    //	inf.append("action", "config");
    //	inf.append("command", "setrecipe");
    var hid = document.createElement("Input");
    hid.setAttribute("type", "hidden");
    hid.setAttribute("name", "client");
    hid.setAttribute("value", "web");
    f.appendChild(hid);
    var hid = document.createElement("Input");
    hid.setAttribute("type", "hidden");
    hid.setAttribute("name", "action");
    hid.setAttribute("value", "config");
    f.appendChild(hid);
    var hid = document.createElement("Input");
    hid.setAttribute("type", "hidden");
    hid.setAttribute("name", "command");
    hid.setAttribute("value", "setrecipe");
    f.appendChild(hid);
    var hid = document.createElement("Input");
    hid.setAttribute("type", "hidden");
    hid.setAttribute("name", "cocktail_id");
    hid.setAttribute("value", row_id.substr(1, row_id.length));
    f.appendChild(hid);
    f.submit();
    popup = 0;
    //	var xhr = new XMLHttpRequest();
    //	xhr.open("POST", Uri);  
    //	xhr.send(inf);
}

function newIngLine(row_id, id, name, qty) {
    num += 1;
    //	console.log(id + " " + name + " " + qty);
    var row = document.getElementById(row_id);
    //	row.setAttribute("id", id);
    var d = document.createElement("div");
    var lab = document.createElement("label");
    lab.setAttribute("for", id);
    txt = document.createTextNode(num);
    lab.appendChild(txt);
    d.appendChild(lab);
    var sel = document.createElement("select");
    sel.setAttribute("name", "ing ".concat(num));
    for (var i = 0; i < inglist[0].length; i++) {
        var opt = inglist[0][i];
        var el = document.createElement("option");
        el.setAttribute("id", inglist[1][i])
        if (inglist[1][i] == id) {
            el.setAttribute("selected", "selected");
        }
        el.textContent = opt;
        el.value = inglist[1][i];
        sel.appendChild(el);
    }
    d.appendChild(sel);
    var lab = document.createElement("label");
    lab.setAttribute("for", "qt ".concat(num));
    txt = document.createTextNode("Quantity");
    lab.appendChild(txt);
    d.appendChild(lab);
    var qt = document.createElement("input");
    qt.setAttribute("name", "qty ".concat(num));
    qt.setAttribute("type", "number");
    qt.setAttribute("id", "qt".concat(id));
    qt.setAttribute("value", qty);
    d.appendChild(qt);
    row.appendChild(d);
    //	editcock.appendChild(row);
};

function getRecipes() {

    getInputKeys();
    req = new XMLHttpRequest();
    params = 'client=web&action=config&command=getCocktails';
    req.onreadystatechange = function () {
        /* console.log(req.responseText) */
        if ((req.readyState == 4) && (req.status == 200)) {
            var data = eval("(" + req.responseText + ")");
            tabbody = document.getElementById("recipes");
            childs = tabbody.childNodes;
            z = childs.length
            for (var y = 0; y < z; y++) {
                tabbody.removeChild(childs[0]);
            }
            deleted = [];
            updatedrows = [];
            for (var i = 0; i < data.Cocktails.length; i++) {
                with(data.Cocktails[i]) {
                    newRecipeLine(id, name, description, available, score1,
                        score2, score3);
                }
            }
        }
        switchEditButtons(0);
    };
    req.open('POST', Uri);
    req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    req.setRequestHeader("Content-length", params.length);
    req.send(params);
};


function newRecipeLine(id, name, description, available, score1, score2, score3) {
    tabbody = document.getElementById("recipes");
    childs = tabbody.getElementsByTagName("tr");
    z = childs.length;
    var c = 0
    y = childs.length;
    row = document.createElement("tr");
    row.setAttribute("id", "r".concat(z));
    cell = document.createElement("td");
    if (name == undefined) {
        var ipt = document.createElement("input");
        ipt.setAttribute("tabindex", "0");
        ipt.setAttribute("class", "desc");
        ipt.setAttribute("onBlur", "changedCell(\"".concat("r" + z + "\")"));
        ipt.setAttribute("value", "New");
    } else {
        ipt = document.createElement("a");
        ipt.setAttribute("contenteditable", false);
        ipt.setAttribute("href", "#edit_form");
        var arg = "getIng(".concat(id + ", \"" + name + "\")");
        ipt.setAttribute("onClick", arg);
        txt = document.createTextNode(name);
        ipt.appendChild(txt);
    }
    ipt.setAttribute("id", "name".concat("r" + z));
    c += 1
    cell.appendChild(ipt);
    row.appendChild(cell);
    var cell = document.createElement("td");
    var ipt = document.createElement("input");
    ipt.setAttribute("class", "desc");
    ipt.setAttribute("tabindex", "0");
    if (description == undefined) {
        ipt.setAttribute("value", "New");
    } else {
        ipt.setAttribute("value", description);
    }
    ipt.setAttribute("id", "desc".concat("r" + z));
    c += 1
    cell.appendChild(ipt);
    row.appendChild(cell);
    var cell = document.createElement("td");
    var ipt = document.createElement("div");
    ipt.setAttribute("contenteditable", false);
    ipt.setAttribute("tabindex", "0");
    //	ipt.setAttribute("onBlur", "changedCell(\"".concat("r"+z + "\")"));
    if (available == undefined) {
        txt = document.createTextNode("unknown");
    } else {
        txt = document.createTextNode(available);
    }
    ipt.appendChild(txt);
    ipt.setAttribute("id", "avail".concat("r" + z));
    c += 1
    cell.appendChild(ipt);
    row.appendChild(cell);
    var cell = document.createElement("td");
    var ipt = document.createElement("input");
    ipt.setAttribute("tabindex", "0");
    ipt.setAttribute("type", "number");
    ipt.setAttribute("onBlur", "changedCell(\"".concat("r" + z + "\")"));
    if (score1 == undefined) {
        ipt.setAttribute("value", 0);
    } else {
        ipt.setAttribute("value", score1);
    }
    ipt.setAttribute("id", "sc1".concat("r" + z));
    c += 1
    cell.appendChild(ipt);
    row.appendChild(cell);
    var cell = document.createElement("td");
    var ipt = document.createElement("input");
    ipt.setAttribute("tabindex", 0);
    ipt.setAttribute("type", "number");
    ipt.setAttribute("onBlur", "changedCell(\"".concat("r" + z + "\")"));
    if (score2 == undefined) {
        ipt.setAttribute("value", "0");
    } else {
        ipt.setAttribute("value", score2);
    }
    ipt.setAttribute("id", "sc2".concat("r" + z));
    c += 1
    cell.appendChild(ipt);
    row.appendChild(cell);
    var cell = document.createElement("td");
    var ipt = document.createElement("input");
    ipt.setAttribute("tabindex", 0);
    ipt.setAttribute("type", "number");
    ipt.setAttribute("onBlur", "changedCell(\"".concat("r" + z + "\")"));
    if (score3 == undefined) {
        ipt.setAttribute("value", 0);
    } else {
        ipt.setAttribute("value", score3);
    }
    ipt.setAttribute("id", "sc3".concat("r" + z));
    c += 1
    cell.appendChild(ipt);
    row.appendChild(cell);
    var ipt = document.createElement("input");
    ipt.setAttribute("hidden", "hidden");
    if (id == undefined) {
        ipt.setAttribute("value", 0);
    } else {
        ipt.setAttribute("value", id);
    }
    ipt.setAttribute("id", "cockid".concat("r" + z));
    row.appendChild(ipt);
    var cell = document.createElement("td");
    cell.setAttribute("contenteditable", false);
    var btn = document.createElement("button");
    btn.setAttribute("style", "width: 30px;")
    btn.setAttribute("onClick", "delCocktail(".concat(z + ", ".concat(id) + ")"));
    txt = document.createTextNode("X");
    if (id == undefined) {
        btn.setAttribute("disabled", "disabled");
    }
    btn.appendChild(txt);
    cell.appendChild(btn);
    row.appendChild(cell);
    var cell = document.createElement("td");
    cell.setAttribute("contenteditable", false);
    var btn = document.createElement("button");
    btn.setAttribute("style", "width: 30px;")
    btn.setAttribute("onClick", "testRow(".concat(z + ", ".concat(id) + ")"));
    txt = document.createTextNode("T");
    if (id == undefined) {
        btn.setAttribute("disabled", "disabled");
    }
    btn.appendChild(txt);
    cell.appendChild(btn);
    row.appendChild(cell);
    tabbody.appendChild(row);
};
