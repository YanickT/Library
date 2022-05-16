window.onload = function () {
    // add onlick-function to items
    var articles = document.getElementsByClassName("item");
    var i;
    for (i = 0; i < articles.length; i++) {
      articles[i].onclick = article_onclick;
    }

    var articles = document.getElementsByClassName("grey-item");
    var i;
    for (i = 0; i < articles.length; i++) {
      articles[i].onclick = blocked_article_onclick;
    }
}


function article_onclick() {
    // get ul
    var non_asso_articles = document.getElementById("non_asso_articles");
    var asso_articles = document.getElementById("asso_articles");

    // setup request
    var url = document.URL;
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');

    // check if article is associated
    var asso_elements = asso_articles.getElementsByTagName("li");
    for (var i = 0; i < asso_elements.length; i++){
        if (asso_elements[i] === this){
            // create new li in non_asso_articles
            var li = document.createElement("li");
            li.appendChild(document.createTextNode(this.innerHTML));
            li.setAttribute("class", "item");
            li.onclick = article_onclick;
            non_asso_articles.appendChild(li);

            // send request
            xhr.send(JSON.stringify({'unassociate': this.innerHTML}));
            break;
        }
    }

    // check if article is associated
    var non_asso_elements = non_asso_articles.getElementsByTagName("li");
    for (var i = 0; i < non_asso_elements.length; i++){
        if (non_asso_elements[i] === this){
            // create new li in non_asso_articles
            var li = document.createElement("li");
            li.appendChild(document.createTextNode(this.innerHTML));
            li.setAttribute("class", "item");
            li.onclick = article_onclick;
            asso_articles.appendChild(li);

            // send request
            xhr.send(JSON.stringify({'associate': this.innerHTML}));
            break;
        }
    }

    // finally remove article
    this.parentElement.removeChild(this);
  }



function blocked_article_onclick(){
    alert("Article has dependencies! Remove them and try again.");
}
