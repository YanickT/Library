// adjust size of svgs
window.onload = function () {
    // adjust main image
    var main_wrapper = document.getElementById("main_wrapper");
    var width = main_wrapper.getBoundingClientRect()["width"] - 40;
    var height = main_wrapper.getBoundingClientRect()["height"] - 40;
    var svg = main_wrapper.getElementsByTagName("svg")[0];
    svg.setAttribute("width", width);
    svg.setAttribute("height", height);

    // adjust solo image size
    var wrapper_solo = document.getElementById("solo_wrapper");
    var width = wrapper_solo.getBoundingClientRect()["width"] - 40;
    var svg_2 = wrapper_solo.getElementsByTagName("svg")[0];
    svg_2.setAttribute("width", width);

    // make main image moveable
    document.onmousemove = move;
    svg.onmousedown = start;
    document.onmouseup = end;
    main_wrapper.onwheel = zoom;
}

// save current zoom when closing window
window.onbeforeunload = function () {
    var svg = document.getElementsByTagName("svg")[0];
    var viewbox = svg.getAttribute("viewBox");

    var xhr = new XMLHttpRequest();
    xhr.open("POST", document.URL + "/close", true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({'viewbox': viewbox}));

};


/* other functions */
// move svg with mouse
var position = {x: 0, y: 0};
var run = false;

function move(event) {
    event.preventDefault();
    if (run) {
        var mouse = {x: event.pageX, y: event.pageY};
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
    position = {x: event.pageX, y: event.pageY};
    document.body.style.cursor = 'move';
    run = true;
}

function end(event) {
    event.preventDefault();
    position = {x: event.pageX, y: event.pageY};
    document.body.style.cursor = 'auto'
    run = false;
}


// zoom with mouse wheel
const zoomfactor = 0.1;

function zoom(event) {
    event.preventDefault();
    var svg = document.getElementsByTagName("svg")[0];
    if (event["deltaY"] < 0) {
        var modi = 1;
    } else {
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


// zoom window at correct position at the start
function zoom_section(viewbox){
    if (viewbox !== null){
        console.log(viewbox)
        var main_wrapper = document.getElementById("main_wrapper");
        var svg = main_wrapper.getElementsByTagName("svg")[0];
        svg.setAttribute("viewBox", viewbox);
    }
}