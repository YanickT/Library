// adjust width of svg
var wrapper = document.getElementById("wrapper");
var width = wrapper.getBoundingClientRect()["width"] - 25;
var height = wrapper.getBoundingClientRect()["height"];
var svg = document.getElementsByTagName("svg")[0];
svg.setAttribute("width", width);
svg.setAttribute("height", height);


// zoom with mouse wheel
const zoomfactor = 0.1;

function zoom(event) {
  event.preventDefault();
  var svg = document.getElementsByTagName("svg")[0];
  if (event["deltaY"] < 0){
      var modi = 1;
  }
  else {
      var modi = -1;
  }

  var viewbox = svg.getAttribute("viewBox");
  var sizes = viewbox.split(" ").map(Number);
  var dw = sizes[2] * modi * zoomfactor;
  var dh = sizes[3] * modi * zoomfactor;
  sizes[2] -= dw;
  sizes[3] -= dh;

  sizes = sizes.map(String);
  svg.setAttribute("viewBox", sizes.join(" "));
}

wrapper.onwheel = zoom;


// move svg with mouse
var position = {x: 0, y: 0};
var run = false;

function move(event) {
    event.preventDefault();
    if (run) {
        var mouse = { x: event.pageX, y: event.pageY };
        var svg = document.getElementsByTagName("svg")[0];
        var viewbox = svg.getAttribute("viewBox");
        var sizes = viewbox.split(" ").map(Number);

        var dx = position["x"] - mouse["x"];
        var dy = position["y"] - mouse["y"];

        sizes[0] += dx;
        sizes[1] += dy;
        sizes = sizes.map(String);

        svg.setAttribute("viewBox", sizes.join(" "));

        position["x"] = mouse["x"];
        position["y"] = mouse["y"];

    }
}

function start(event) {
    event.preventDefault();
    console.log("down");
    position = { x: event.pageX, y: event.pageY };
    document.body.style.cursor = 'move';
    run = true;
}

function end(event) {
    event.preventDefault();
    console.log("up");
    position = { x: event.pageX, y: event.pageY };
    document.body.style.cursor = 'auto'
    run = false;
}

document.onmousemove = move;
svg.onmousedown = start;
svg.onmouseup = end;
