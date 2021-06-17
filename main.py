from flask import Flask, render_template, send_from_directory, request, redirect, url_for
from administration import BASE, CONFIG
import os
import sys
import subprocess


app = Flask(__name__)


# open_file is taken from:
# https://stackoverflow.com/questions/17317219/is-there-an-platform-independent-equivalent-of-os-startfile
def open_file(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])


@app.route('/')
def home():
    main_graph, solo_graph = BASE.get_dependency_graph("/articles", "/dependency")
    return render_template('home.html', main_graph=main_graph, solo_graph=solo_graph, viewbox=CONFIG["viewbox"])


@app.route('/zoom', methods=['POST'])
def zoom():
    CONFIG("viewbox", request.json["viewbox"])
    return "dummy"


@app.route('/sync')
def sync():
    BASE.sync()
    CONFIG("viewbox", None)
    return redirect(url_for("home"))


@app.route('/update')
def update_page():
    main_graph, solo_graph = BASE.get_dependency_graph("/update", "/dependency")
    return render_template('home_update.html', main_graph=main_graph, solo_graph=solo_graph, viewbox=CONFIG["viewbox"])


@app.route('/update/<article>', methods=['POST', 'GET'])
def update_article(article: int):
    if request.method == "GET":
        return render_template('paper_update.html',
                               title=BASE.get("articles", "title", article_id=int(article))[0][0],
                               author=BASE.get("articles", "author", article_id=int(article))[0][0],
                               pages=BASE.get("articles", "pages", article_id=int(article))[0][0],
                               cur_page=BASE.get("articles", "cur_page", article_id=int(article))[0][0],
                               article=article)
    else:
        BASE.update("articles", "cur_page", int(request.form["page"]), article_id=int(article))
        BASE.update("articles", "title", request.form["title"], article_id=int(article))
        BASE.update("articles", "author", request.form["author"], article_id=int(article))
        return redirect(url_for("update_page"))


@app.route('/articles/<article>')
def get_article(article: int):
    # open if extern connection is made possible (within LAN only)
    if not request.remote_addr == request.host and False:
        return send_from_directory(BASE.get_path(), BASE.get("articles", "filename", article_id=int(article))[0][0])

    open_file(BASE.get_path() + BASE.get("articles", "filename", article_id=int(article))[0][0])
    return redirect(url_for("home"))


@app.route('/todo', methods=['POST', 'GET'])
def todo():
    if request.method == "POST":
        if request.form:
            BASE.add("tasks", request.form["comment"])
        else:
            BASE.drop("tasks", comment=request.json["remove"])

    return render_template('todo.html', tasks=[task[0] for task in BASE.get("tasks", "comment")])


@app.route('/dependency', methods=['POST', 'GET'])
def dependency():
    if request.method == "POST":
        for child in request.json["childs"]:
            BASE.add("depends", int(request.json["parent"]), int(child), "")
    articles = BASE.get("articles", "article_id", "title", "author")
    return render_template('dependency.html', articles=articles, depends=BASE.get("depends", "*"))


@app.route('/dependency/<index>', methods=['POST', 'GET'])
def dependency_edit(index):
    if request.method == "POST":
        if request.form["action"] == "Submit":
            BASE.update("depends", "comment", request.form["comment"], depend_id=int(index))
        elif request.form["action"] == "Delete":
            print("Drop")
            BASE.drop("depends", depend_id=index)

        return redirect(url_for("dependency"))

    depend_id, parent_id, child_id, comment = BASE.get("depends", "*", depend_id=int(index))[0]
    return render_template("dependency_update.html",
                           depend_id=depend_id,
                           comment=comment,
                           title_parent=BASE.get("articles", "title", article_id=int(parent_id))[0][0],
                           author_parent=BASE.get("articles", "author", article_id=int(parent_id))[0][0],
                           title_child=BASE.get("articles", "title", article_id=int(child_id))[0][0],
                           author_child=BASE.get("articles", "author", article_id=int(child_id))[0][0])


@app.route('/add')
def open_article_folder():
    open_file(BASE.get_path())
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run()

