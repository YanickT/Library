// send dependency to server and add it to other panel
function add_dependency(){
    // check if parent is filled
    var parent = document.getElementById("parent");
    if (parent.innerHTML === ""){
        window.alert("You must choose a parent element!");
        return;
    }

    // check if at least one child is given
    var childs = document.getElementById("child").childNodes;
    if (childs.length == 0){
        window.alert("You must choose at least one child element!");
        return
    }

    // get data
    var parent_id = parent.innerHTML.split(" ")[0].slice(1,-1);
    parent.click();
    var child_ids = [];
    for (var i = 0; i < childs.length; i++){
        child_ids.push(childs[i].innerHTML.split(" ")[0].slice(1,-1));
    }
    // remove childs
    while (childs.length > 0){
        childs[0].click();
    }

    // send data to server
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/dependency", true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({'parent': parent_id, 'childs': child_ids}));

    // reload site
    window.location.replace("/dependency");
}


/*
Item management in the panels
*/

// onclick on articles
function article_onclick() {
    // check if parent is choosen
    var parent = document.getElementById("parent");

    // parent is emtpy
    if (parent.innerHTML === ""){
        parent.innerHTML = this.innerHTML;
        this.parentElement.removeChild(this);
    }
    else {
        var childs = document.getElementById("child");
        var li = document.createElement("li");
        li.appendChild(document.createTextNode(this.innerHTML));
        li.setAttribute("class", "item selected");
        li.onclick = selected_onclick;
        childs.appendChild(li);
        this.parentElement.removeChild(this);
    }
  }

// onclick on selected
function selected_onclick(){
    var article_holder = document.getElementById("article-holder");
    var li = document.createElement("li");
    li.appendChild(document.createTextNode(this.innerHTML));
    li.setAttribute("class", "item article");
    li.onclick = article_onclick;
    article_holder.appendChild(li);

    if (this === document.getElementById("parent")){
        this.innerHTML = "";
    }
    else {
        var parent = this.parentElement;
        parent.removeChild(this);
    }
}

// onclick on depend
function depend_onclick(){
    window.location.replace("/dependency/" + this.id);
}


// ul of articles
var articles = document.getElementsByClassName("article");
var i;
for (i = 0; i < articles.length; i++) {
  articles[i].onclick = article_onclick;
}


// remove item when clicked on and choosen
var selected = document.getElementsByClassName("selected");
var i;
for (i = 0; i < selected.length; i++) {
  selected[i].onclick = selected_onclick;
}

var depends = document.getElementsByClassName("depend");
for (var i = 0; i < depends.length; i++){
    depends[i].onclick = depend_onclick;
}

