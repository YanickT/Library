from flask import Flask, render_template, request, redirect, url_for
from backend_sql import BASE, ARTPATH, CONFIG
import os
import sys
import subprocess

app = Flask(__name__)

# ==================================Projects===============================================
get_names = lambda x: x if not x else [e[0] for e in x]


@app.route("/")
def home():
    BASE.sync()
    projects = get_names(BASE.get("projects", "name"))[::-1]
    return render_template('home.html', projects=projects)


@app.route("/remove_project", methods=["POST"])
def remove_project():
    if request.form["project_name"] in get_names(BASE.get("projects", "name")):
        project_id = BASE.get("projects", "project_id", name=request.form["project_name"])[0][0]
        BASE.drop("depends", project_id=project_id)
        BASE.drop("articles_project", project_id=project_id)
        BASE.drop("tasks", project_id=project_id)
        BASE.drop("projects", project_id=project_id)
    return redirect(url_for("home"))


@app.route("/add_project", methods=["POST"])
def add_project():
    if not (request.form["project_name"] in get_names(BASE.get("projects", "name"))):
        BASE.add("projects", (request.form["project_name"]))
    return redirect(url_for("home"))


@app.route("/rename_project", methods=["POST"])
def rename_project():
    if request.form["project_name_old"] in get_names(BASE.get("projects", "name")) and not (
            request.form["project_name_new"] in get_names(BASE.get("projects", "name"))):
        BASE.update("projects", "name", request.form["project_name_new"], name=request.form["project_name_old"])
    return redirect(url_for("home"))


# ==================================Projects===============================================
# ===================================Project===============================================


@app.route("/project/<project_name>", methods=['POST', 'GET'])
def project(project_name):
    solo_graph = BASE.get_solo_graph(project_name, url=f"{project_name}/read")
    main_graph = BASE.get_main_graph(project_name, url=f"{project_name}/read",
                                     dep_url=url_for("dependency", project_name=project_name))
    return render_template("project.html", project_name=project_name, solo_graph=solo_graph, project_home=True,
                           main_graph=main_graph, viewbox=CONFIG[f"{project_name}_viewbox"])


@app.route("/project/<project_name>/add_article/", methods=["GET", "POST"])
def add_article_to_project(project_name):
    if request.method == "POST":
        BASE.reset_project(project_name)
        if "associate" in request.json:
            article_name = ":".join(request.json["associate"].split(":")[:-1])
            article_id = BASE.get("articles", "article_id", title=article_name)[0][0]
            project_id = BASE.get("projects", "project_id", name=project_name)[0][0]
            BASE.add("articles_project", article_id, project_id)
        elif "unassociate" in request.json:
            article_name = ":".join(request.json["unassociate"].split(":")[:-1])
            article_id = BASE.get("articles", "article_id", title=article_name)[0][0]
            project_id = BASE.get("projects", "project_id", name=project_name)[0][0]
            BASE.drop("articles_project", article_id=article_id, project_id=project_id)

    articles = BASE.get("articles", "article_id", "title", "author", "pages", "cur_page")
    proj_articles_solo = BASE.get_project_articles_solo(project_name)
    proj_articles_nonsolo = BASE.get_project_articles_nonsolo(project_name)
    non_associated_articles = [article for article in articles if
                               not (article in proj_articles_nonsolo or article in proj_articles_solo)]

    return render_template("addArticle.html", project_name=project_name,
                           non_associated_articles=non_associated_articles,
                           proj_articles_solo=proj_articles_solo,
                           proj_articles_nonsolo=proj_articles_nonsolo)


@app.route("/project/<project_name>/close", methods=['POST'])
def close(project_name):
    CONFIG(f"{project_name}_viewbox", request.json["viewbox"])
    return "Close"

# ===================================Project===============================================
# ===================================Filesystem============================================
# open_file is taken from:
# https://stackoverflow.com/questions/17317219/is-there-an-platform-independent-equivalent-of-os-startfile
def open_file(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])


@app.route('/oaf')
def open_article_folder():
    open_file(ARTPATH)
    return redirect(url_for("home"))


# ===================================Filesystem============================================
# ===================================Article===============================================


@app.route('/project/<project_name>/update')
def update_page(project_name):
    BASE.reset_project(project_name)
    solo_graph = BASE.get_solo_graph(project_name, url=f"update/")
    main_graph = BASE.get_main_graph(project_name, url=f"update/",
                                     dep_url=url_for("dependency", project_name=project_name))
    return render_template("project.html", project_name=project_name, solo_graph=solo_graph, project_home=False,
                           main_graph=main_graph, viewbox=CONFIG[f"{project_name}_viewbox"])


@app.route('/project/<project_name>/update/<article>', methods=['POST', 'GET'])
def update_article(project_name, article: int):
    if request.method == "GET":
        return render_template('paper_update.html',
                               title=BASE.get("articles", "title", article_id=int(article))[0][0],
                               author=BASE.get("articles", "author", article_id=int(article))[0][0],
                               pages=BASE.get("articles", "pages", article_id=int(article))[0][0],
                               cur_page=BASE.get("articles", "cur_page", article_id=int(article))[0][0],
                               article=article,
                               summary=BASE.get("articles", "summary", article_id=int(article))[0][0],
                               project_name=project_name)
    elif request.method == "POST":
        BASE.reset_project(project_name)
        BASE.update("articles", "title", request.form["title"], article_id=int(article))
        BASE.update("articles", "author", request.form["author"], article_id=int(article))
        BASE.update("articles", "cur_page", request.form["page"], article_id=int(article))
        BASE.update("articles", "summary", request.form["summary"], article_id=int(article))
        return redirect(url_for("update_page", project_name=project_name))


@app.route('/project/<project_name>/read/<article>')
def open_article(project_name, article: int):
    open_file(ARTPATH + BASE.get("articles", "filename", article_id=int(article))[0][0])
    return redirect(url_for("project", project_name=project_name))


# ===================================Article===============================================
# =====================================TO_DO===============================================

@app.route('/project/<project_name>/todo', methods=['POST', 'GET'])
def todo(project_name):
    project_id = BASE.get("projects", "project_id", name=project_name)[0][0]
    if request.method == "POST":
        if request.form:
            BASE.add("tasks", request.form["comment"], project_id)
        else:
            BASE.drop("tasks", comment=request.json["remove"])

    tasks = [task[0] for task in BASE.get("tasks", "comment", project_id=project_id)]
    return render_template("todo.html", tasks=tasks, project_name=project_name)


# =====================================TO_DO===============================================
# ==================================DEPENDENCY=============================================

@app.route('/project/<project_name>/dependency', methods=['POST', 'GET'])
def dependency(project_name):
    project_id = BASE.get("projects", "project_id", name=project_name)[0][0]
    if request.method == "POST":
        BASE.reset_project(project_name)
        for child in request.json["childs"]:
            BASE.add("depends", int(request.json["parent"]), int(child), "", project_id)
    proj_articles = BASE.get_project_articles_solo(project_name) + BASE.get_project_articles_nonsolo(project_name)
    proj_articles = [article[:3] for article in proj_articles]
    depends = BASE.get("depends", "depend_id, article_id, child_id, comment", project_id=project_id)
    return render_template("dependency.html", articles=proj_articles, depends=depends, project_name=project_name)


@app.route('/project/<project_name>/dependency/<index>', methods=['POST', 'GET'])
def dependency_edit(project_name, index):
    if request.method == "POST":
        BASE.reset_project(project_name)
        if request.form["action"] == "Submit":
            BASE.update("depends", "comment", request.form["comment"], depend_id=int(index))
        elif request.form["action"] == "Delete":
            BASE.drop("depends", depend_id=index)

        return redirect(url_for("dependency", project_name=project_name))

    depend_id, parent_id, child_id, comment = \
        BASE.get("depends", "depend_id, article_id, child_id, comment", depend_id=int(index))[0]
    return render_template("dependency_update.html",
                           project_name=project_name,
                           depend_id=depend_id,
                           comment=comment,
                           title_parent=BASE.get("articles", "title", article_id=int(parent_id))[0][0],
                           author_parent=BASE.get("articles", "author", article_id=int(parent_id))[0][0],
                           title_child=BASE.get("articles", "title", article_id=int(child_id))[0][0],
                           author_child=BASE.get("articles", "author", article_id=int(child_id))[0][0])


# ==================================DEPENDENCY=============================================

if __name__ == "__main__":
    app.run()
