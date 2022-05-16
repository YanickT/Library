// adjust size of svgs
window.onload = function () {
    /*var wrapper = document.getElementById("wrapper");
    var width = wrapper.getBoundingClientRect()["width"] - 40;
    var height = wrapper.getBoundingClientRect()["height"];
    var svg = document.getElementsByTagName("svg")[0];
    svg.setAttribute("width", width);
    svg.setAttribute("height", height);*/

    var wrapper_solo = document.getElementById("solo_wrapper");
    var width = wrapper_solo.getBoundingClientRect()["width"] - 40;
    var svg_2 = wrapper_solo.getElementsByTagName("svg")[0];
    svg_2.setAttribute("width", width);
}