import sqlite3
from path import PATH
import graphviz
from PyPDF2 import PdfFileReader
import os
import pickle

VERSION = 2.0
ARTPATH = PATH + "Article/"
ARTICLEFILE = "article.db"
CONFIGFILE = ".config"
TABLES = [
    """
    CREATE TABLE IF NOT EXISTS articles (
        article_id integer PRIMARY KEY autoincrement,
        filename text NOT NULL,
        title text NOT NULL,
        author text NOT NULL,
        pages integer NOT NULL,
        cur_page integer DEFAULT 0,
        summary text)
    """,

    """
    CREATE TABLE IF NOT EXISTS projects (
    project_id integer PRIMARY KEY autoincrement,
    name text UNIQUE NOT NULL)
    """,

    """
    CREATE TABLE IF NOT EXISTS articles_project (
    article_project_id integer PRIMARY KEY autoincrement,
    article_id integer NOT NULL,
    project_id integer NOT NULL,
    CONSTRAINT article_id FOREIGN KEY (article_id) REFERENCES articles(article_id),
    CONSTRAINT project_id FOREIGN KEY (project_id) REFERENCES projects(project_id))
    """,

    """
    CREATE TABLE IF NOT EXISTS depends (
        depend_id integer PRIMARY KEY autoincrement,
        article_id integer NOT NULL,
        child_id integer NOT NULL,
        comment text,
        project_id integer NOT NULL,
        CONSTRAINT project_id FOREIGN KEY (project_id) REFERENCES projects(project_id))
    """,

    """
    CREATE TABLE IF NOT EXISTS tasks (
    task_id integer PRIMARY KEY autoincrement,
    comment text NOT NULL,
    project_id integer NOT NULL,
    CONSTRAINT project_id FOREIGN KEY (project_id) REFERENCES projects(project_id))
    """]

NODE = lambda index, title, author, ratio, main_url: f"""
N{index} [
shape=plain
label=<
    <table cellborder="0" cellspacing="5">
        <tr><td colspan="2">{title}</td></tr>
        <tr><td colspan="2">{author}</td></tr>
        <tr>
            <td border="1" width="50" bgcolor="#6da8ce;{min(ratio + 0.01, 1):.2f}:white"></td>
            <td color="white">{ratio * 100:.0f}%</td>
        </tr>
    </table>
>
URL = "{main_url}/{index}"
]
"""


class Connection:

    def __init__(self):
        # initialize database if not exists
        for statement in TABLES:
            self.execute(statement)

        self.solo_images = {}
        self.connected_images = {}

    @staticmethod
    def execute(statement):
        try:
            conn = sqlite3.connect(PATH + ARTICLEFILE)
            cur = conn.cursor()
            cur.execute(statement)
            conn.commit()
            conn.close()
        except:
            raise SyntaxError(f"Statement:\n\t{statement}\nfailed.")

    # GENERAL ACTIONS
    def sync(self):
        files = [file for file in os.listdir(ARTPATH) if file[-4:] == ".pdf"]
        db_files = [row[0] for row in self.get("articles", "filename")]

        # check for files in database but not articles
        [self.drop("articles", filename=file) for file in db_files if file not in files]

        # check for articles not in database
        for file in files:
            if file in db_files:
                continue

            with open(ARTPATH + file, 'rb') as f:
                pdf = PdfFileReader(f)
                infos = pdf.getDocumentInfo()
                pages = pdf.getNumPages()

            if infos.title != "" and infos.title is not None:
                title = infos.title
            else:
                title = file[:-4]

            if infos.author != "" and infos.author is not None:
                author = infos.author
            else:
                author = "Unkown author"
            self.add("articles", file, title, author, pages, 0, "")

    # GENERAL ACTIONS

    # BASIC ACTIONS
    @staticmethod
    def get(table, *columns, **conditions):
        conn = sqlite3.connect(PATH + ARTICLEFILE)
        cur = conn.cursor()
        if not conditions:
            cur.execute(f"SELECT {','.join(columns)} FROM {table}")
        else:
            conditions = [
                f"{key} = '{conditions[key]}'" if isinstance(conditions[key], str) else f"{key} = {conditions[key]}" for
                key in conditions]

            cur.execute(f"SELECT {','.join(columns)} FROM {table} WHERE {' AND '.join(conditions)}")
        data = cur.fetchall()
        conn.close()
        return data

    def add(self, table, *data):
        data = [f"'{e}'" if isinstance(e, str) else str(e) for e in data]
        self.execute(f"INSERT INTO {table} VALUES (NULL, {','.join(data)})")

    def drop(self, table, **conditions):
        if not conditions:
            raise ValueError("No condition specified")
        conditions = [
            f"{key} = '{conditions[key]}'" if isinstance(conditions[key], str) else f"{key} = {conditions[key]}" for
            key in conditions]

        self.execute(f"DELETE FROM {table} WHERE {' AND '.join(conditions)}")

    def update(self, table, column, value, **conditions):
        value = f"'{value}'" if isinstance(value, str) else value
        if not conditions:
            raise ValueError("No condition specified")
        conditions = [
            f"{key} = '{conditions[key]}'" if isinstance(conditions[key], str) else f"{key} = {conditions[key]}" for
            key in conditions]
        self.execute(f"UPDATE {table} SET {column} = {value} WHERE {'AND'.join(conditions)}")

    # BASIC ACTIONS

    # PROJECT ACTIONS
    @staticmethod
    def get_project_articles_solo(project_name):
        statement = f"""SELECT articles.article_id, title, author, pages, cur_page FROM articles 
                        JOIN articles_project ap ON articles.article_id = ap.article_id
                        JOIN projects p on ap.project_id = p.project_id
                        WHERE (articles.article_id NOT IN (
                            SELECT article_id FROM depends 
                            JOIN projects ON projects.project_id = depends.project_id
                            WHERE projects.name = '{project_name}')
                        AND articles.article_id NOT IN (
                            SELECT child_id FROM depends 
                            JOIN projects ON projects.project_id = depends.project_id
                            WHERE projects.name = '{project_name}'))
                        AND p.name = '{project_name}'"""
        conn = sqlite3.connect(PATH + ARTICLEFILE)
        cur = conn.cursor()
        cur.execute(statement)
        articles = cur.fetchall()
        conn.close()
        return articles

    @staticmethod
    def get_project_articles_nonsolo(project_name):
        statement = f"""SELECT article_id, title, author, pages, cur_page FROM articles 
                        WHERE article_id IN (
                            SELECT article_id FROM depends 
                            JOIN projects ON projects.project_id = depends.project_id
                            WHERE projects.name = '{project_name}')
                        OR article_id IN (
                            SELECT child_id FROM depends 
                            JOIN projects ON projects.project_id = depends.project_id
                            WHERE projects.name = '{project_name}')
                        """
        conn = sqlite3.connect(PATH + ARTICLEFILE)
        cur = conn.cursor()
        cur.execute(statement)
        articles = cur.fetchall()
        conn.close()
        return articles

    def get_solo_graph(self, project_name, url):
        if (project_name, url) in self.solo_images:
            return self.solo_images[(project_name, url)]

        articles = self.get_project_articles_solo(project_name)

        solo_graph = graphviz.Graph()
        solo_graph.graph_attr["rankdir"] = "LR"
        solo_graph.graph_attr["id"] = "solo_graph"
        for index, title, author, pages, curpage in articles:
            solo_graph.body.append(NODE(index, title, author, curpage / pages, url))

        solo_img = solo_graph.pipe(format='svg').replace(b"\r\n", b"").decode('utf-8')
        # solo_img = solo_img.replace("l_", "solo_l_")
        self.solo_images[(project_name, url)] = solo_img
        return solo_img

    def get_main_graph(self, project_name, url, dep_url):
        if (project_name, url) in self.connected_images:
            return self.connected_images[(project_name, url)]

        articles = self.get_project_articles_nonsolo(project_name)
        project_id = self.get("projects", "project_id", name=project_name)[0][0]
        depends = self.get("depends", "*", project_id=project_id)

        # create the nodes
        graph = graphviz.Digraph()
        graph.graph_attr["nodesep"] = "1"
        graph.graph_attr["ranksep"] = "1"
        graph.graph_attr["id"] = "main_graph"
        for index, title, author, pages, curpage in articles:
            graph.body.append(NODE(index, title, author, curpage / pages, url))

        # add edges
        for index, from_, to_, comment, project_id in depends:
            graph.edge(f"N{from_}", f"N{to_}", comment, URL=f"{dep_url}/{index}", headport="n", tailport="s")

        img = graph.pipe(format='svg').replace(b"\r\n", b"").decode('utf-8')
        self.connected_images[(project_name, url)] = img
        return img

    def reset_project(self, project_name):
        for key in self.solo_images:
            if project_name in key:
                del self.solo_images[key]
                break
        for key in self.connected_images:
            if project_name in key:
                del self.connected_images[key]
                break
    # PROJECT ACTIONS


BASE = Connection()
BASE.sync()


class ConfigHandler:

    def __init__(self):
        # check if config file already exists
        if not os.path.isfile(PATH + CONFIGFILE):
            with open(PATH + CONFIGFILE, "wb") as doc:
                pickle.dump({"version": VERSION}, doc)

    def __getitem__(self, item):
        with open(PATH + CONFIGFILE, "rb") as doc:
            data = pickle.load(doc)

        return data.get(item)

    def __call__(self, key, value):
        with open(PATH + CONFIGFILE, "rb") as doc:
            data = pickle.load(doc)
        with open(PATH + CONFIGFILE, "wb") as doc:
            data[key] = value
            pickle.dump(data, doc)


CONFIG = ConfigHandler()