from flask import Flask, render_template, send_from_directory, request, redirect, url_for
from administration import BASE
import os

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html', chart_output=BASE.get_dependency_graph("/articles", "/dependency"))


@app.route('/sync')
def sync():
    BASE.sync()
    return redirect(url_for("home"))


@app.route('/update')
def update_page():
    return render_template('home_update.html', chart_output=BASE.get_dependency_graph("/update", "/dependency"))


@app.route('/update/<article>', methods=['POST', 'GET'])
def update_article(article: int):
    if request.method == "GET":
        return render_template('paper_update.html',
                               title=BASE.get_title(article),
                               author=BASE.get_author(article),
                               pages=BASE.get_pages(article),
                               cur_page=BASE.get_curpage(article),
                               article=article)
    else:
        BASE.update_curpage(article, request.form["page"])
        BASE.update_title(article, request.form["title"])
        BASE.update_author(article, request.form["author"])
        return redirect(url_for("update_page"))


@app.route('/articles/<article>')
def get_article(article: int):
    # open if extern connection is made possible (within LAN only)
    if not request.remote_addr == request.host and False:
        return send_from_directory(BASE.get_path(), BASE.get_filename(article))

    os.startfile(BASE.get_path() + BASE.get_filename(article))
    return redirect(url_for("home"))


@app.route('/todo', methods=['POST', 'GET'])
def todo():
    if request.method == "POST":
        if request.form:
            BASE.add_task(request.form["comment"])
        else:
            BASE.remove_task(request.json["remove"])

    return render_template('todo.html', tasks=BASE.get_tasks())


@app.route('/dependency', methods=['POST', 'GET'])
def dependency():
    if request.method == "POST":
        for child in request.json["childs"]:
            BASE.add_dependency(int(request.json["parent"]), int(child))
    articles = BASE.get_articles()
    id_title = [(article[0], article[1], article[2]) for article in articles]
    return render_template('dependency.html', articles=id_title, depends=BASE.get_dependencies())


@app.route('/dependency/<index>', methods=['POST', 'GET'])
def dependency_edit(index):
    if request.method == "POST":
        if request.form["action"] == "Submit":
            BASE.update_depends_comment(index, request.form["comment"])
        elif request.form["action"] == "Delete":
            BASE.drop_depend(index)

        return redirect(url_for("dependency"))

    depend_id, parent_id, child_id, comment = BASE.get_dependency(index)
    return render_template("dependency_update.html",
                           depend_id=depend_id,
                           comment=comment,
                           title_parent=BASE.get_title(parent_id),
                           author_parent=BASE.get_author(parent_id),
                           title_child=BASE.get_title(child_id),
                           author_child=BASE.get_author(child_id))


if __name__ == "__main__":
    app.run()


# GENERELLE IDEEN
# TODO: Reiter "Add Paper" für Download from Arxiv usw. (Nur einfügen der URL)
# TODO: Reiter für die Bildung von Flussclustern Seperieren von Strukturen


# IN UPDATE PAPER MACHEN:
# TODO: Reiter Zusammenfassungen: Darin sollen die Wichtigsten Inhalte der Paper dargestellt werden (wenn draufklick)
# TODO: Außerdem Fragen....
