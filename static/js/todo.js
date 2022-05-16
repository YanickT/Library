// Taken from https://www.w3schools.com/howto/howto_js_todolist.asp and changed

window.onload = function () {
  // Click on a close button to hide the current list item
  var close = document.getElementsByClassName("item");
  for (i = 0; i < close.length; i++) {
    close[i].onclick = function() {
      // send remove request to server
      var xhr = new XMLHttpRequest();
      xhr.open("POST", document.URL, true);
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.send(JSON.stringify({'remove': this.innerHTML}));
      this.style.display = "none";
    }
  }
}


