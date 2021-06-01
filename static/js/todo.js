// Taken from https://www.w3schools.com/howto/howto_js_todolist.asp and changed

// Create a "close" button and append it to each list item
var items = document.getElementsByClassName("item");
for (var i = 0; i < items.length; i++) {
  var span = document.createElement("SPAN");
  var txt = document.createTextNode("\u00D7");
  span.className = "close";
  span.appendChild(txt);
  items[i].appendChild(span);
}

// Click on a close button to hide the current list item
var close = document.getElementsByClassName("close");
var i;
for (i = 0; i < close.length; i++) {
  close[i].onclick = function() {
    // send remove request to server
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/todo", true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({'remove': this.parentElement.innerHTML.split("<")[0]}));
    this.parentElement.style.display = "none";
  }
}
