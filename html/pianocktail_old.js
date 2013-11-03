/**
 * Javascript utility functions for the Pianocktail
 * @author Bertrand Verdu
 */

var rb = 0;
var pb = 0;
var cb = 0;
var pos = 0;
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
var Uri = "http://" + hostname + ":" + port + "/";
var wsUri = "ws://" + hostname + ":" + port + "/ws";
var output;
var websocket;
var down = false;
var cur_x;
var cur_y;
var lastev;
var changelist = {};
var updatedrows = [];
var deleted = [];

// common utilities

function eventFire(el, etype){
	  if (el.fireEvent) {
	    (el.fireEvent('on' + etype));
	    console.log('on'+etype);
	  } else {
	    var evObj = document.createEvent('Events');
	    console.log(etype);
	    evObj.initEvent(etype, true, false);
	    el.dispatchEvent(evObj);
	  }
	}

function getInputKeys(){
document.addEventListener('keydown', function (event) {
  var esc = event.which == 27,
      nl = event.which == 13,
//      tb = event.which == 9,
      el = event.target;
      console.log(el);
      d = el.getAttribute('Id');
      r = el.getAttribute('onBlur');
      console.log("keydown");
      console.log("d= "+d);
      console.log("r= "+r);

  if (r) {
    if (esc) {
      // restore state
      document.execCommand('undo');
      console.log("esc")
      //el.blur();
    } else if (nl) {
      // save
      eval(r);

      // we could send an ajax request to update the field
      /*
      $.ajax({
        url: window.location.toString(),
        data: data,
        type: 'post'
      });
      */
      console.log("validate: "+r)
      el.blur();
//      event.preventDefault();
    }
//    else if (tb){
//    	var t = d.charAt(1);
//    	var m = new Number(t);
//    	var y = m +1;
//    	console.log(d.slice(0,-1));
//    	var n = d.slice(0,-1).concat(y);
//    	console.log(n);
//    	next_cell = document.getElementById(n);
//    	event.preventDefault();
//    	eventFire(next_cell, 'click');
//    	
//    }
    else {
    	var rr = new Number(d.charAt(0));
    	console.log("got r"+rr);
    	if (updatedrows.indexOf("r"+rr) == -1) {
    		console.log("updated: r"+rr);
    		updatedrows.push("r"+rr);
//    		el.blur();
//    	    event.preventDefault();
    	}
    	switchEditButtons(1);
    }
  }
}, true);};

//document.getElementById("tableSystem").addEventListener("input", function () {
//	switchEditButtons(1);
//}, false);
//document.getElementById("recipes").addEventListener("input", function () {
//	switchEditButtons(1);
//}, false);
//document.getElementById("recipes").addEventListener("input", function () {
//	switchEditButtons(1);
//}, false);


function log(s) {
  document.getElementById('debug').innerHTML = 'value changed to: ' + s;
}

// Main page utilities

function isTouchDevice() {
	return "ontouchstart" in window;
}


// Main page utils

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
	if (isTouchDevice()) {
		//writeToScreen("touch");
		canv.addEventListener('touchstart', notedown, true);
		canv.addEventListener('touchend', noteup, true);
		canv.addEventListener('touchmove', changenote, true);
	} else {
		//writeToScreen("desktop");
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
	/*websocket = new WebSocket(wsUri);*/

	if ('WebSocket' in window) {
		websocket = new WebSocket(wsUri);
		console.log("ws ok")
	} else if ('MozWebSocket' in window) {
		websocket = new MozWebSocket(wsUri);
		console.log("ws ok")
	} else {
		//not supported
		console.log("ws ko")
		return;
	}
	websocket.onopen = function(evt) {
		onOpen(evt)
	};
	websocket.onclose = function(evt) {
		onClose(evt)
	};
	websocket.onmessage = function(evt) {
		onMessage(evt)
	};
	websocket.onerror = function(evt) {
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
	context.fillStyle = "#008a00";
	writeToScreen("CONNECTED");
	setTimeout('doSend("status")', 50);
	console.log("open")
}

function onClose(evt) {
	context.fillStyle = "#e81010";
	writeToScreen("DISCONNECTED");
}

function onMessage(evt) {
	if (isNaN(evt.data)) {
		if ((evt.data == "Recording")||(evt.data == "Playing")) {
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
	/*   websocket.close();*/
}

function onError(evt) {
	context.fillStyle = "#e81010";
	writeToScreen('ERROR: ' + evt.data);
}

function doSend(message) {
	/*context.fillStyle = "#762086";
	 writeToScreen("Action: " + message);*/
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
	doSend(id)
}

function buttonup(id) {
	doSend("-" + id)
}

function buttonclick(buttonid) {
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
		x : mouseX,
		y : mouseY
	};
}

function changenote(ev) {
	/*context.fillStyle = "white";
	 writeToScreen("note move");*/
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
			if ( cur_y = 60) {
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
}

function notedown(ev) {
	ev.preventDefault();
	down = true
	canvcontext.fillStyle = "red"
	var evtpos = getevtPos(canv, ev);
	ev._x = evtpos.x;
	ev._y = evtpos.y;
	lastev = ev;
	/*context.fillStyle = "white";
	 writeToScreen("note down");
	 writeToScreen("X= " + ev._x.toString());
	 writeToScreen("Y= " + ev._y.toString());*/
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

}

function noteup(ev) {
	ev.preventDefault();
	down = false;
	canvcontext.fillStyle = "white";
	/*context.fillStyle = "white";
	writeToScreen("noteup");*/
	//var evtpos = getevtPos(canv, ev);
	ev._x = lastev._x;
	ev._y = lastev._y;
	/*writeToScreen("X= " + ev._x.toString());
	 writeToScreen("Y= " + ev._y.toString());*/
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

}

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
}

//function getConf() {
//	console.log("get_conf")
//	req = new XMLHttpRequest();
//	params = 'client=web&action=config&command=getconf';
//	req.onreadystatechange = function() {
//		if ((req.readyState == 4) && (req.status == 200)) {
//			var data = eval("(" + req.responseText + ")");
//			sets = document.getElementById("configparams");
//			childs = sets.childNodes;
//			z = childs.length
//			for (var y = 0; y < z; y++) {
//				sets.removeChild(childs[0]);
//			}
//			lab5 = document.createElement("label");
//			/*lab5.for ="debug";*/
//			lab5.innerHTML = "Debug";
//			sets.appendChild(lab5);
//			var dbg = document.createElement("input");
//			dbg.id = "debug";
//			dbg.type = "checkbox";
//			dbg.value = data.debug;
//			dbg.setAttribute("onClick", "setData(\"debug\")");
//			if (data.debug == 1) {
//				changelist['debug'] = 1;
//				dbg.checked = "True";
//			} else {
//				changelist['debug'] = 0;
//			}
//			sets.appendChild(dbg);
//			lab0 = document.createElement("label");
//			/*lab0.for ="alc";*/
//			lab0.innerHTML = "Alcool ?";
//			sets.appendChild(lab0);
//			var alc = document.createElement("input");
//			alc.id = "alc";
//			alc.type = "checkbox";
//			alc.value = data.alc;
//			alc.setAttribute("onClick", "setData(\"alc\")");
//			if (data.alc == 1) {
//				changelist['alc'] = 1;
//				alc.checked = "True";
//			} else {
//				changelist['alc'] = 0;
//			}
//			sets.appendChild(alc);
//			lab1 = document.createElement("label");
//			/*lab1.for ="dep";*/
//			lab1.innerHTML = "Pump offset :";
//			sets.appendChild(lab1);
//			var dep = document.createElement("input");
//			dep.id = "dep";
//			dep.type = "number";
//			dep.size = "3";
//			dep.step = "1";
//			dep.value = data.dep;
//			dep.setAttribute("onBlur", "setData(\"dep\")");
//			sets.appendChild(dep);
//			lab2 = document.createElement("label");
//			/*lab2.for ="complex";*/
//			lab2.innerHTML = "Complexity index :";
//			sets.appendChild(lab2);
//			var complex = document.createElement("input");
//			complex.id = "complexind";
//			complex.type = "number";
//			complex.size = "3";
//			complex.step = "0.1";
//			complex.value = data.complexind;
//			complex.setAttribute("onBlur", "setData(\"complexind\")");
//			sets.appendChild(complex);
//			lab3 = document.createElement("label");
//			/*lab3.for ="tristesse";*/
//			lab3.innerHTML = "Sadness index :";
//			sets.appendChild(lab3);
//			var tristesse = document.createElement("input");
//			tristesse.id = "tristind"
//			tristesse.type = "number";
//			tristesse.size = "3";
//			tristesse.step = "0.1";
//			tristesse.value = data.tristind;
//			tristesse.setAttribute("onBlur", "setData(\"tristind\")");
//			sets.appendChild(tristesse);
//			lab4 = document.createElement("label");
//			/*lab4.for ="nervous";*/
//			lab4.innerHTML = "Nervosity index :";
//			sets.appendChild(lab4);
//			var nervous = document.createElement("input");
//			nervous.id = "nervind";
//			nervous.type = "number";
//			nervous.size = "3";
//			nervous.step = "0.1";
//			nervous.value = data.nervind;
//			nervous.setAttribute("onBlur", "setData(\"nervind\")");
//			sets.appendChild(nervous);
//			lab5 = document.createElement("label");
//			/*lab5.for ="factor";*/
//			lab5.innerHTML = "Qty ratio :";
//			sets.appendChild(lab5);
//			var factor = document.createElement("input");
//			nervous.id = "factor";
//			nervous.type = "number";
//			nervous.size = "3";
//			nervous.step = "0.1";
//			nervous.value = data.factor;
//			nervous.setAttribute("onBlur", "setData(\"factor\")");
//			sets.appendChild(nervous);
//			listIn = document.getElementById("midiInList");
//			listIn.options.length = 0;
//			for (var i = 0; i < data.inports.length; i++) {
//				var message = data.inports[i][0] + ":" + data.inports[i][1] + " " + data.inports[i][2];
//				var pre = document.createElement("option");
//				pre.value = i
//				pre.innerHTML = message;
//				listIn.appendChild(pre)
//			}
//			listOut = document.getElementById("midiOutList");
//			listOut.options.length = 0;
//			for (var i = 0; i < data.outports.length; i++) {
//				var message = data.outports[i][0] + ":" + data.outports[i][1] + " " + data.outports[i][2];
//				var pre = document.createElement("option");
//				pre.value = i
//				pre.innerHTML = message;
//				listOut.appendChild(pre)
//			}
//		}
//
//	};
//	console.log(Uri);
//	req.open('POST', Uri);
//	console.log("post");
//	req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
//	req.setRequestHeader("Content-length", params.length);
//	console.log(params);
//	req.send(params);
//};

function getConf() {
	webSocketManager();
	getInputKeys();
	console.log("get_conf");
	pumpmax = 0;
	req = new XMLHttpRequest();
	params = 'client=web&action=config&command=getconf';
	req.onreadystatechange = function() {
		if ((req.readyState == 4) && (req.status == 200)) {
			var data = eval("(" + req.responseText + ")");
			sets = document.getElementById("configparams");
			childs = sets.childNodes;
			z = childs.length
			for (var y = 0; y < z; y++) {
				sets.removeChild(childs[0]);
			}
			lab5 = document.createElement("label");
			/*lab5.for ="debug";*/
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
			lab0 = document.createElement("label");
			/*lab0.for ="alc";*/
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
			lab1 = document.createElement("label");
			/*lab1.for ="dep";*/
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
			/*lab2.for ="complex";*/
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
			/*lab3.for ="tristesse";*/
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
			/*lab4.for ="nervous";*/
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
			/*lab5.for ="factor";*/
			lab5.innerHTML = "Qty ratio :";
			sets.appendChild(lab5);
			var factor = document.createElement("input");
			nervous.id = "factor";
			nervous.type = "number";
			nervous.size = "3";
			nervous.step = "0.1";
			nervous.value = data.factor;
			nervous.setAttribute("onBlur", "setData(\"factor\")");
			sets.appendChild(nervous);
			listIn = document.getElementById("midiInList");
			listIn.options.length = 0;
			for (var i = 0; i < data.inports.length; i++) {
				var message = data.inports[i][0] + ":" + data.inports[i][1] + " " + data.inports[i][2];
				var pre = document.createElement("option");
				pre.value = i
				pre.innerHTML = message;
				listIn.appendChild(pre)
			}
			listOut = document.getElementById("midiOutList");
			listOut.options.length = 0;
			for (var i = 0; i < data.outports.length; i++) {
				var message = data.outports[i][0] + ":" + data.outports[i][1] + " " + data.outports[i][2];
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
				with (data.systemports[i]) {
						//newPumpLine(name, deg, pump, time)
					newsysLine(num, type, description, bus,
							channel, ratio, funct, avail)
				}

			}
			newsysLine();
//			switchEditButtons(0);
			
		}
		switchEditButtons(0);
		updatedrows = [];
	};
	console.log(Uri);
	req.open('POST', Uri);
	console.log("post");
	req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	req.setRequestHeader("Content-length", params.length);
	console.log(params);
	req.send(params);
};
function newsysLine(num, type, description, bus,
							channel, ratio, funct, avail){
	table = document.getElementById("tableSystem");
	childs = table.getElementsByTagName("tr");
	z = childs.length;
	row = document.createElement("tr");
	row.setAttribute("id", "r"+z);
	var c = 0;
	cell = document.createElement("td");
	ipt = document.createElement("div");
	ipt.setAttribute("tabindex", "0");
	ipt.setAttribute("id", z+"".concat(c));
	c += 1;
	ipt.setAttribute("onBlur", "changedCell(\"".concat("r"+z + "\")"));
//	ipt.setAttribute("onBlur", "yo");
	if (num == undefined) {
		txt = document.createTextNode(pumpmax+1);
		pumpmax += 1;
	} else {
		txt = document.createTextNode(num);
		if (num > pumpmax){
			pumpmax = num;
		}
	}
	ipt.appendChild(txt);
	cell.appendChild(ipt);
	row.appendChild(cell);
	var cell = document.createElement("td");
	var ipt = document.createElement("div");
	ipt.setAttribute("tabindex", "0");
	ipt.setAttribute("onBlur", "changedCell(\"".concat("r"+z + "\")"));
	ipt.setAttribute("id", z+"".concat(c));
	c += 1;
	if (type == undefined) {
		txt = document.createTextNode("New");
	} else {
		txt = document.createTextNode(type);
	}
	ipt.appendChild(txt);
	cell.appendChild(ipt);
	row.appendChild(cell);
	var cell = document.createElement("td");
	var ipt = document.createElement("div");
	ipt.setAttribute("tabindex", "0");
	ipt.setAttribute("onBlur", "changedCell(\"".concat("r"+z + "\")"));
	ipt.setAttribute("id", z+"".concat(c));
	c += 1;
	if (description == undefined) {
		txt = document.createTextNode("New");
	} else {
		txt = document.createTextNode(description);
	}
	ipt.appendChild(txt);
	cell.appendChild(ipt);
	row.appendChild(cell);
	var cell = document.createElement("td");
	var ipt = document.createElement("div");
	ipt.setAttribute("tabindex", "0");
	ipt.setAttribute("onBlur", "changedCell(\"".concat("r"+z + "\")"));
	ipt.setAttribute("id", z+"".concat(c));
	c += 1;
	if (bus == undefined) {
		txt = document.createTextNode("New");
	} else {
		txt = document.createTextNode(bus);
	}
	ipt.appendChild(txt);
	cell.appendChild(ipt);
	row.appendChild(cell);
	var cell = document.createElement("td");
	var ipt = document.createElement("div");
	ipt.setAttribute("tabindex", "0");
	ipt.setAttribute("onBlur", "changedCell(\"".concat("r"+z + "\")"));
	ipt.setAttribute("id", z+"".concat(c));
	c += 1;
	if (channel == undefined) {
		txt = document.createTextNode(pumpmax);
	} else {
		txt = document.createTextNode(channel);
	}
	ipt.appendChild(txt);
	cell.appendChild(ipt);
	row.appendChild(cell);
	var cell = document.createElement("td");
	var ipt = document.createElement("div");
	ipt.setAttribute("tabindex", "0");
	ipt.setAttribute("onBlur", "changedCell(\"".concat("r"+z + "\")"));
	ipt.setAttribute("id", z+"".concat(c));
	c += 1;
	if (ratio == undefined) {
		txt = document.createTextNode("1.0");
	} else {
		txt = document.createTextNode(ratio);
	}
	ipt.appendChild(txt);
	cell.appendChild(ipt);
	row.appendChild(cell);
	var cell = document.createElement("td");
	var ipt = document.createElement("div");
	ipt.setAttribute("tabindex", "0");
	ipt.setAttribute("onBlur", "changedCell(\"".concat("r"+z + "\")"));
	ipt.setAttribute("id", z+"".concat(c));
	c += 1;
	if (funct == undefined) {
		txt = document.createTextNode("None");
	} else {
		txt = document.createTextNode(funct);
	}
	ipt.appendChild(txt);
	cell.appendChild(ipt);
	row.appendChild(cell);
	var cell = document.createElement("td");
	cell.setAttribute("contenteditable", false);
	var btn = document.createElement("button");
	btn.setAttribute("id", num);
	if (isTouchDevice()) {
		btn.setAttribute("onTouchStart", "doSend(\"test ".concat(" "+num + "\")"));
		btn.setAttribute("onTouchEnd", "doSend(\"test ".concat("-"+num + "\")"));
	}
	else {
	btn.setAttribute("onMouseDown", "doSend(\"test ".concat(" "+num + "\")"));
	btn.setAttribute("onMouseUp", "doSend(\"test ".concat("-"+num + "\")"));
	}
	txt = document.createTextNode("Test");
	btn.appendChild(txt);
	cell.appendChild(btn);
	row.appendChild(cell);
	table.appendChild(row);	
};

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
		console.log(t);
		var rw = document.getElementById(key).getElementsByTagName("div");
		pump = rw[0].innerHTML;
		console.log(pump);
		if ((pump != undefined)&&(rw[0].innerHTML != "New")) {
			updrow = {};
			updrow.pump = pump;
			updrow.type = rw[1].innerHTML;
			updrow.description = rw[2].innerHTML;
			updrow.bus = rw[3].innerHTML;
			updrow.chan = rw[4].innerHTML;
			updrow.ratio = rw[5].innerHTML;
			updrow.fct = rw[6].innerHTML;
			rows.push(updrow);
		}
	}
	changelist['rows'] = rows;
	parms.params = changelist;
	req.onreadystatechange = function() {
		if ((req.readyState == 4) && (req.status == 200)) {
			var data = eval("(" + req.responseText + ")");
			if (data.updated == "1") {
				console.log("update = OK");
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

// pumps page utilities

function switchEditButtons(enable) {
	if (enable == 0) {
		chbut = document.getElementById("chgbuttons").getElementsByTagName("button");
		for (var i = 0; i < chbut.length; i++) {
			chbut[i].setAttribute("disabled", "1");
		}
	} else {
		chbut = document.getElementById("chgbuttons").getElementsByTagName("button");
		for (var i = 0; i < chbut.length; i++) {
			chbut[i].removeAttribute("disabled");
		}
	}

}

function chronometer() {
	centi = centi + 100;
	//incrémentation des centièmes de seconde
	chrono.innerHTML = centi;
	tim = setTimeout('chronometer()', 100);
}

function startchrono(pump) { //fonction qui remet les compteurs à 0
	chrono = document.getElementById("chrono");
	running = 1;
	centi = 0;
	req = new XMLHttpRequest();
	params = 'client=web&action=pump&command=b' + pump;
	req.onreadystatechange = function() {
		console.log(req.responseText)
		if ((req.readyState == 4) && (req.status == 200)) {
			if (req.responseText == '0') {
				btn = document.getElementById(pump);
				btn.setAttribute("style", "background: red;color: white;")
				chronometer();
			}
		}
	}
	req.open('POST', Uri);
	req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	req.setRequestHeader("Content-length", params.length);
	req.send(params);
}

function stopchrono(row) {
	lin = document.getElementById(row);
	var pump = lin.getElementsByTagName("div")[2].innerHTML;
	if (running == 1) {
		req = new XMLHttpRequest();
		params = 'client=web&action=pump&command=s' + pump;
		req.onreadystatechange = function() {
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
		req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
		req.setRequestHeader("Content-length", params.length);
		req.send(params);
	} 
	else {
		startchrono(pump);
	}

}

function saveRow(row) {
	lin = document.getElementById(row);
	cells = lin.getElementsByTagName("div");
	cells[3].innerHTML = document.getElementById("chrono").innerHTML;
	if (updatedrows.indexOf(row) == -1) {
		//console.log(row)
		updatedrows.push(row);
		switchEditButtons(1);
	}

}

/*function writeToScreen(message) {
 var pre = document.createElement("p");
 pre.style.wordWrap = "break-word";
 pre.innerHTML = message;
 output.appendChild(pre);
 }*/

function setRow(num) {
	lin = document.getElementById("r" + num);
	req = new XMLHttpRequest();
	params = '@client=web&@action=config&@command=setpumps(' + jsondata + ')';
}

function changedCell(row) {
	console.log("kikouu"+row);
	console.log(updatedrows)
	if (updatedrows.indexOf(row) == -1) {
		console.log(row);
		updatedrows.push(row);
//		switchEditButtons(1);
	}
}

function getPumps() {
	getInputKeys();
	var lists = ["alcools"]
	var alclist = []
	req = new XMLHttpRequest();
	params = 'client=web&action=config&command=getpumps';
	req.onreadystatechange = function() {
		/*console.log(req.responseText)*/
		if ((req.readyState == 4) && (req.status == 200)) {
			updatedrows = []
			var data = eval("(" + req.responseText + ")");
			var alcool = document.getElementById("alcools");
			tabbody = document.getElementById("pumps");
			childs = tabbody.childNodes;
			z = childs.length
			for (var y = 0; y < z; y++) {
				tabbody.removeChild(childs[0]);
			}
			for (var i = 0; i < data.pumps.length; i++) {
				if (data.pumps[i].name != 'EMPTY') {
					with (data.pumps[i]) {
						//newPumpLine(name, deg, pump, time)
						newPumpLine(name, deg, pump, qty, time)
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
	var updated = []
	for (var i = 0; i < updatedrows.length; i++) {
		key = updatedrows[i];
		console.log(key);
		rw = document.getElementById(key).getElementsByTagName("div");
		name = rw[0].innerHTML;
		console.log(name);
		if (name != undefined) {
			updrow = {};
			updrow.name = name;
			updrow.alcool = rw[1].innerHTML;
			updrow.pump = rw[2].innerHTML;
			updrow.time = rw[3].innerHTML;
			updrow.qty = rw[4].innerHTML;
			updated.push(updrow);
		}
	}
	req = new XMLHttpRequest();
	parms = {};
	parms.client = "web";
	parms.action = "config";
	parms.command = "setpumps";
	if (updated.length > 0) {
		parms.params = updated;
	} else {
		parms.params = "0"
	}
	req.onreadystatechange = function() {
		if ((req.readyState == 4) && (req.status == 200)) {
			var data = eval("(" + req.responseText + ")");
			if (data.updated == "1") {
				console.log("update = OK");
				getPumps();
			}
			else
				{
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
};

//function newPumpLine(name, deg, pump, tim) {
//	tabbody = document.getElementById("pumps");
//	childs = tabbody.getElementsByTagName("tr");
//	z = "r" + childs.length;
//	row = document.createElement("tr");
//	row.setAttribute("id", z)
//	cell = document.createElement("td");
//	ipt = document.createElement("div");
//	ipt.setAttribute("tabindex", "0");
//	ipt.setAttribute("onBlur", "changedCell(\"".concat(z + "\")"));
//	if (name == undefined) {
//		txt = document.createTextNode("New");
//	} else {
//		txt = document.createTextNode(name);
//	}
//	ipt.appendChild(txt);
//	cell.appendChild(ipt);
//	row.appendChild(cell);
//	var cell = document.createElement("td");
//	var ipt = document.createElement("div");
//	ipt.setAttribute("tabindex", "0");
//	ipt.setAttribute("onBlur", "changedCell(\"".concat(z + "\")"));
//	if (deg == undefined) {
//		txt = document.createTextNode("0");
//	} else {
//		txt = document.createTextNode(deg);
//	}
//	ipt.appendChild(txt);
//	cell.appendChild(ipt);
//	row.appendChild(cell);
//	var cell = document.createElement("td");
//	var ipt = document.createElement("div");
//	ipt.setAttribute("tabindex", "0");
//	ipt.setAttribute("onBlur", "changedCell(\"".concat(z + "\")"));
//	if (pump == undefined) {
//		txt = document.createTextNode("999");
//	} else {
//		txt = document.createTextNode(pump);
//	}
//	ipt.appendChild(txt);
//	cell.appendChild(ipt);
//	row.appendChild(cell);
//	var cell = document.createElement("td");
//	var ipt = document.createElement("div");
//	ipt.setAttribute("tabindex", "0");
//	ipt.setAttribute("onBlur", "changedCell(\"".concat(z + "\")"));
//	if (tim == undefined) {
//		txt = document.createTextNode("0");
//	} else {
//		txt = document.createTextNode(tim);
//	}
//	ipt.appendChild(txt);
//	cell.appendChild(ipt);
//	row.appendChild(cell);
//	var cell = document.createElement("td");
//	cell.setAttribute("contenteditable", false);
//	var btn = document.createElement("button");
//	btn.setAttribute("id", pump);
//	btn.setAttribute("onClick", "stopchrono(\"".concat(z + "\")"));
//	txt = document.createTextNode("Start/Stop");
//	btn.appendChild(txt);
//	cell.appendChild(btn);
//	row.appendChild(cell);
//	var cell = document.createElement("td");
//	cell.setAttribute("contenteditable", false);
//	var btn = document.createElement("button");
//	btn.setAttribute("onClick", "saveRow(\"".concat(z + "\")"));
//	txt = document.createTextNode("Save");
//	btn.appendChild(txt);
//	cell.appendChild(btn);
//	row.appendChild(cell);
//	tabbody.appendChild(row);
//};
function newPumpLine(name, deg, pump, qty, tim) {
	tabbody = document.getElementById("pumps");
	childs = tabbody.getElementsByTagName("tr");
	z = childs.length;
	row = document.createElement("tr");
	row.setAttribute("id", "r"+z);
	var c = 0
	cell = document.createElement("td");
	ipt = document.createElement("div");
	ipt.setAttribute("tabindex", "0");
	ipt.setAttribute("id", z+"".concat(c));
	c += 1;
	ipt.setAttribute("onBlur", "changedCell(\"".concat("r"+z + "\")"));
	if (name == undefined) {
		txt = document.createTextNode("New");
	} else {
		txt = document.createTextNode(name);
	}
	ipt.appendChild(txt);
	cell.appendChild(ipt);
	row.appendChild(cell);
	var c = 0
	cell = document.createElement("td");
	ipt = document.createElement("div");
	ipt.setAttribute("tabindex", "0");
	ipt.setAttribute("id", z+"".concat(c));
	c += 1;
	ipt.setAttribute("onBlur", "changedCell(\"".concat("r"+z + "\")"));
	if (deg == undefined) {
		txt = document.createTextNode("0");
	} else {
		txt = document.createTextNode(deg);
	}
	ipt.appendChild(txt);
	cell.appendChild(ipt);
	row.appendChild(cell);
	var c = 0
	cell = document.createElement("td");
	ipt = document.createElement("div");
	ipt.setAttribute("tabindex", "0");
	ipt.setAttribute("id", z+"".concat(c));
	c += 1;
	ipt.setAttribute("onBlur", "changedCell(\"".concat("r"+z + "\")"));
	if (pump == undefined) {
		txt = document.createTextNode("999");
	} else {
		txt = document.createTextNode(pump);
	}
	ipt.appendChild(txt);
	cell.appendChild(ipt);
	row.appendChild(cell);
	var c = 0
	cell = document.createElement("td");
	ipt = document.createElement("div");
	ipt.setAttribute("tabindex", "0");
	ipt.setAttribute("id", z+"".concat(c));
	c += 1;
	ipt.setAttribute("onBlur", "changedCell(\"".concat("r"+z + "\")"));
	if (tim == undefined) {
		txt = document.createTextNode("0");
	} else {
		txt = document.createTextNode(tim);
	}
	ipt.appendChild(txt);
	cell.appendChild(ipt);
	row.appendChild(cell);
	var c = 0
	cell = document.createElement("td");
	ipt = document.createElement("div");
	ipt.setAttribute("tabindex", "0");
	ipt.setAttribute("id", z+"".concat(c));
	c += 1;
	ipt.setAttribute("onBlur", "changedCell(\"".concat("r"+z + "\")"));
	if (qty == undefined) {
		txt = document.createTextNode("100");
	} else {
		txt = document.createTextNode(qty);
	}
	ipt.appendChild(txt);
	cell.appendChild(ipt);
	row.appendChild(cell);
	var cell = document.createElement("td");
	cell.setAttribute("contenteditable", false);
	var btn = document.createElement("button");
	btn.setAttribute("id", pump);
	btn.setAttribute("onClick", "stopchrono(\"".concat("r"+z + "\")"));
	txt = document.createTextNode("Start/Stop");
	btn.appendChild(txt);
	cell.appendChild(btn);
	row.appendChild(cell);
	var cell = document.createElement("td");
	cell.setAttribute("contenteditable", false);
	var btn = document.createElement("button");
	btn.setAttribute("onClick", "saveRow(\"".concat("r"+z + "\")"));
	txt = document.createTextNode("Save");
	btn.appendChild(txt);
	cell.appendChild(btn);
	row.appendChild(cell);
	tabbody.appendChild(row);
};
function switchEditButtons(enable) {
	if (enable == 0) {
		chbut = document.getElementById("chgbuttons").getElementsByTagName("button");
		for (var i = 0; i < chbut.length; i++) {
			chbut[i].setAttribute("disabled", "1");
		}
	} else {
		chbut = document.getElementById("chgbuttons").getElementsByTagName("button");
		for (var i = 0; i < chbut.length; i++) {
			chbut[i].removeAttribute("disabled");
		}
	}

};

function testRow(row, name) {
	req = new XMLHttpRequest();
	params = 'client=web&action=pump&command=t' + name;
	req.onreadystatechange = function() {
		console.log(req.responseText)
	}
	req.open('POST', Uri);
	req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	req.setRequestHeader("Content-length", params.length);
	req.send(params);
};

function delRow(row, name) {
	if (updatedrows.indexOf(row) == -1) {
		tabbody = document.getElementById("recipes");
		tabbody.removeChild(tabbody.childNodes[row]);
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
			rw = document.getElementById(key).getElementsByTagName("div");
			name = rw[0].innerHTML;
			console.log(name);
			console.log(rw.length);
			if (name != undefined) {
				updrow = {};
				updrow.name = name;
				updrow.qte1 = rw[2].innerHTML;
				updrow.ing1 = rw[3].innerHTML;
				updrow.qte2 = rw[4].innerHTML;
				updrow.ing2 = rw[5].innerHTML;
				updrow.qte3 = rw[6].innerHTML;
				updrow.ing3 = rw[7].innerHTML;
				updrow.qte4 = rw[8].innerHTML;
				updrow.ing4 = rw[9].innerHTML;
				updrow.qte5 = rw[10].innerHTML;
				updrow.ing5 = rw[11].innerHTML;
				updrow.qte6 = rw[12].innerHTML;
				updrow.ing6 = rw[13].innerHTML;
				updrow.tristesse = rw[14].innerHTML;
				updrow.nerf = rw[15].innerHTML;
				updated.push(updrow);
			}
		}
		req = new XMLHttpRequest();
		parms = {};
		parms.client = "web";
		parms.action = "config";
		parms.command = "setrecipes";
		parms.params = updated;
		req.onreadystatechange = function() {
			if ((req.readyState == 4) && (req.status == 200)) {
				var data = eval("(" + req.responseText + ")");
				if (data.updated == "1") {
					console.log("update = OK");
					getRecipes();
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
		parms.client = "web";
		parms.action = "config";
		parms.command = "delrecipes";
		parms.params = deleted;
		req.onreadystatechange = function() {
			if ((req.readyState == 4) && (req.status == 200)) {
				var data = eval("(" + req.responseText + ")");
				if (data.updated == "1") {
					console.log("update = OK");
					getRecipes();
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

};

function ingList(){
	
	req = new XMLHttpRequest();
	params = 'client=web&action=config&command=getinglist';
	req.onreadystatechange = function() {
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

function getIng(cocktail) {
	console.log("getIng: "+cocktail);
	req = new XMLHttpRequest();
	params = 'client=web&action=config&command=getcocking&param='+cocktail;
	req.onreadystatechange = function() {
		if ((req.readyState == 4) && (req.status == 200)) {
			data = eval("(" + req.responseText + ")");
			inglist = data.list;
			editcock = document.getElementById("ing");
			childs = editcock.childNodes;
			z = childs.length
			for (var y = 0; y < z; y++) {
				editcock.removeChild(childs[0]);
			}
			num = 0
			for (var i = 0; i < data.ingredients.length; i++){
				with (data.ingredients[i]) {
					newIngLine(editcock, id, name, qty);
				}
			}
			var btn = document.getElementById("addbtn");
			btn.setAttribute("OnClick", "newIngLine(editcock, 0, \"New\", 0)");
//			newIngLine(editcock, 0, 'New', 0);
			console.log(inglist);
			}
		}
	req.open('POST', Uri);
	req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	req.setRequestHeader("Content-length", params.length);
	req.send(params);
};

function newIngLine(editcock, id, name, qty){
	num += 1;
	console.log(id+" "+name+" "+qty);
	var row = document.createElement("form");
	row.setAttribute("id", id);
	var lab = document.createElement("label");
	lab.setAttribute("for", id);
	txt = document.createTextNode(num);
	lab.appendChild(txt);
	row.appendChild(lab);
	var sel = document.createElement("select");
	for(var i = 0; i < inglist[0].length; i++) {
	    var opt = inglist[0][i];
	    var el = document.createElement("option");
	    el.setAttribute("id", inglist[1][i])
	    if (inglist[1][i] == id){
	    	el.setAttribute("selected", "selected");
	    }
	    el.textContent = opt;
	    el.value = opt;
	    el.value = opt;
	    sel.appendChild(el);
	}
	row.appendChild(sel);
	editcock.appendChild(row);
};

function getRecipes() {
	getInputKeys();
	req = new XMLHttpRequest();
	params = 'client=web&action=config&command=getrecipes';
	req.onreadystatechange = function() {
		/*console.log(req.responseText)*/
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
			for (var i = 0; i < data.recipes.length; i++) {
				with (data.recipes[i]) {
					newRecipeLine(id, name, description, available, score1, score2, score3);
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
	z = "r" + childs.length;
	y = childs.length;
	row = document.createElement("tr");
	row.setAttribute("id", z)
	cell = document.createElement("td");
	ipt = document.createElement("a");
	ipt.setAttribute("contenteditable", false);
	ipt.setAttribute("href", "#edit_form");
	ipt.setAttribute("onClick", "getIng(\"".concat(id + "\")"));
	if (name == undefined) {
		txt = document.createTextNode("New");
	} else {
		txt = document.createTextNode(name);
	}
	ipt.appendChild(txt);
	cell.appendChild(ipt);
	row.appendChild(cell);
	var cell = document.createElement("td");
	var ipt = document.createElement("div");
	ipt.setAttribute("tabindex", "0");
	if (description == undefined) {
		txt = document.createTextNode("new");
	} else {
		txt = document.createTextNode(description);
	}
	ipt.appendChild(txt);
	cell.appendChild(ipt);
	row.appendChild(cell);
	var cell = document.createElement("td");
	var ipt = document.createElement("div");
	ipt.setAttribute("tabindex", "0");
	ipt.setAttribute("onBlur", "changedCell(\"".concat(z + "\")"));
	if (available == undefined) {
		txt = document.createTextNode("unknown");
	} else {
		txt = document.createTextNode(available);
	}
	ipt.appendChild(txt);
	cell.appendChild(ipt);
	row.appendChild(cell);
	var cell = document.createElement("td");
	var ipt = document.createElement("div");
	ipt.setAttribute("tabindex", "0");
	ipt.setAttribute("onBlur", "changedCell(\"".concat(z + "\")"));
	if (score1 == undefined) {
		txt = document.createTextNode("0");
	} else {
		txt = document.createTextNode(score1);
	}
	ipt.appendChild(txt);
	cell.appendChild(ipt);
	row.appendChild(cell);
	var cell = document.createElement("td");
	var ipt = document.createElement("div");
	ipt.setAttribute("tabindex", "0");
	ipt.setAttribute("onBlur", "changedCell(\"".concat(z + "\")"));
	if (score2 == undefined) {
		txt = document.createTextNode("0");
	} else {
		txt = document.createTextNode(score2);
	}
	ipt.appendChild(txt);
	cell.appendChild(ipt);
	row.appendChild(cell);
	var cell = document.createElement("td");
	var ipt = document.createElement("div");
	ipt.setAttribute("tabindex", "0");
	ipt.setAttribute("onBlur", "changedCell(\"".concat(z + "\")"));
	if (score3 == undefined) {
		txt = document.createTextNode("0");
	} else {
		txt = document.createTextNode(score3);
	}
	ipt.appendChild(txt);
	cell.appendChild(ipt);
	row.appendChild(cell);
	var cell = document.createElement("td");
	cell.setAttribute("contenteditable", false);
	var btn = document.createElement("button");
	btn.setAttribute("style", "width: 30px;")
	btn.setAttribute("onClick", "delRow(\"".concat(id + "\")"));
	txt = document.createTextNode("X");
	btn.appendChild(txt);
	cell.appendChild(btn);
	row.appendChild(cell);
	var cell = document.createElement("td");
	cell.setAttribute("contenteditable", false);
	var btn = document.createElement("button");
	btn.setAttribute("style", "width: 30px;")
	btn.setAttribute("onClick", "testRow(\"".concat(id + "\")"));
	txt = document.createTextNode("T");
	btn.appendChild(txt);
	cell.appendChild(btn);
	row.appendChild(cell);
	tabbody.appendChild(row);
};

//function getRecipes() {
//	getInputKeys();
//	req = new XMLHttpRequest();
//	params = 'client=web&action=config&command=getrecipes';
//	req.onreadystatechange = function() {
//		/*console.log(req.responseText)*/
//		if ((req.readyState == 4) && (req.status == 200)) {
//			var data = eval("(" + req.responseText + ")");
//			tabbody = document.getElementById("recipes");
//			childs = tabbody.childNodes;
//			z = childs.length
//			for (var y = 0; y < z; y++) {
//				tabbody.removeChild(childs[0]);
//			}
//			deleted = [];
//			updatedrows = [];
//			for (var i = 0; i < data.recipes.length; i++) {
//				with (data.recipes[i]) {
//					var alc = "No";
//					if (alcool == 1) {
//						var alc = "Yes";
//					}
//					ing = [qte1, ing1, qte2, ing2, qte3, ing3, qte4, ing4, qte5, ing5, qte6, ing6];
//					newRecipeLine(name, alc, ing, tristesse, complex, nerf);
//				}
//			}
//		}
//		switchEditButtons(0);
//	};
//	req.open('POST', Uri);
//	req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
//	req.setRequestHeader("Content-length", params.length);
//	req.send(params);
//};
//function newRecipeLine(name, alc, ing, sad, comp, nerv) {
//	tabbody = document.getElementById("recipes");
//	childs = tabbody.getElementsByTagName("tr");
//	z = "r" + childs.length;
//	y = childs.length;
//	row = document.createElement("tr");
//	row.setAttribute("id", z)
//	cell = document.createElement("td");
//	ipt = document.createElement("div");
//	ipt.setAttribute("tabindex", "0");
//	ipt.setAttribute("onBlur", "changedCell(\"".concat(z + "\")"));
//	if (name == undefined) {
//		txt = document.createTextNode("New");
//	} else {
//		txt = document.createTextNode(name);
//	}
//	ipt.appendChild(txt);
//	cell.appendChild(ipt);
//	row.appendChild(cell);
//	var cell = document.createElement("td");
//	var ipt = document.createElement("div");
//	ipt.setAttribute("tabindex", "0");
//	ipt.setAttribute("contenteditable", false);
//	if (alc == undefined) {
//		txt = document.createTextNode("N/A");
//	} else {
//		txt = document.createTextNode(alc);
//	}
//	ipt.appendChild(txt);
//	cell.appendChild(ipt);
//	row.appendChild(cell);
//	for (var i = 0; i < 12; i++) {
//		var cell = document.createElement("td");
//		var ipt = document.createElement("div");
//		ipt.setAttribute("tabindex", "0");
//		ipt.setAttribute("onBlur", "changedCell(\"".concat(z + "\")"));
//		if (ing == undefined) {
//			if (i / 2 == Math.round(i / 2)) {
//				txt = document.createTextNode("0");
//			} else {
//				txt = document.createTextNode("/");
//			}
//		} else {
//			txt = document.createTextNode(ing[i]);
//		}
//		ipt.appendChild(txt);
//		cell.appendChild(ipt);
//		row.appendChild(cell);
//	}
//	var cell = document.createElement("td");
//	var ipt = document.createElement("div");
//	ipt.setAttribute("tabindex", "0");
//	ipt.setAttribute("onBlur", "changedCell(\"".concat(z + "\")"));
//	if (sad == undefined) {
//		txt = document.createTextNode("0");
//	} else {
//		txt = document.createTextNode(sad);
//	}
//	ipt.appendChild(txt);
//	cell.appendChild(ipt);
//	row.appendChild(cell);
//	var cell = document.createElement("td");
//	var ipt = document.createElement("div");
//	ipt.setAttribute("tabindex", "0");
//	ipt.setAttribute("onBlur", "changedCell(\"".concat(z + "\")"));
//	if (nerv == undefined) {
//		txt = document.createTextNode("0");
//	} else {
//		txt = document.createTextNode(nerv);
//	}
//	ipt.appendChild(txt);
//	cell.appendChild(ipt);
//	row.appendChild(cell);
//	var cell = document.createElement("td");
//	cell.setAttribute("contenteditable", false);
//	var btn = document.createElement("button");
//	btn.setAttribute("style", "width: 30px;")
//	btn.setAttribute("onClick", "delRow(\"".concat(y + "\",\"" + name + "\")"));
//	txt = document.createTextNode("X");
//	btn.appendChild(txt);
//	cell.appendChild(btn);
//	row.appendChild(cell);
//	var cell = document.createElement("td");
//	cell.setAttribute("contenteditable", false);
//	var btn = document.createElement("button");
//	btn.setAttribute("style", "width: 30px;")
//	btn.setAttribute("onClick", "testRow(\"".concat(y + "\",\"" + name + "\")"));
//	txt = document.createTextNode("T");
//	btn.appendChild(txt);
//	cell.appendChild(btn);
//	row.appendChild(cell);
//	tabbody.appendChild(row);
//};
