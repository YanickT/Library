import os
import sqlite3
import pickle
from path import PATH
import graphviz
from PyPDF2 import PdfFileReader

ARTPATH = PATH + "Article/"
ARTICLEFILE = "article.db"
CONFIGFILE = ".config"
STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS articles (
        article_id integer PRIMARY KEY autoincrement,
        filename text NOT NULL,
        title text NOT NULL,
        author text NOT NULL,
        pages integer NOT NULL,
        cur_page integer DEFAULT 0)
    """,
    """
    CREATE TABLE IF NOT EXISTS depends (
        depend_id integer PRIMARY KEY autoincrement,
        article_id integer NOT NULL,
        child_id integer NOT NULL,
        comment text)
    """,
    """
    CREATE TABLE IF NOT EXISTS tasks (
    task_id integer PRIMARY KEY autoincrement,
    comment text NOT NULL)
    """]


class Connection:

    def __init__(self):
        for statement in STATEMENTS:
            self.execute(statement)

        self.images = {}

    @staticmethod
    def execute(statement):
        conn = sqlite3.connect(PATH + ARTICLEFILE)
        cur = conn.cursor()
        cur.execute(statement)
        conn.commit()
        conn.close()

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
            cur.execute(f"SELECT {','.join(columns)} FROM {table} WHERE {'AND'.join(conditions)}")
        data = cur.fetchall()
        conn.close()
        return data

    def drop(self, table, **conditions):
        self.images = {}
        if not conditions:
            raise ValueError("No condition specified")
        conditions = [
            f"{key} = '{conditions[key]}'" if isinstance(conditions[key], str) else f"{key} = {conditions[key]}" for
            key in conditions]
        self.execute(f"DELETE FROM {table} WHERE {'AND'.join(conditions)}")

    def add(self, table, *data):
        self.images = {}
        data = [f"'{e}'" if isinstance(e, str) else str(e) for e in data]
        self.execute(f"INSERT INTO {table} VALUES (NULL, {','.join(data)})")

    def update(self, table, column, value, **conditions):
        self.images = {}
        value = f"'{value}'" if isinstance(value, str) else value
        if not conditions:
            raise ValueError("No condition specified")
        conditions = [
            f"{key} = '{conditions[key]}'" if isinstance(conditions[key], str) else f"{key} = {conditions[key]}" for
            key in conditions]
        self.execute(f"UPDATE {table} SET {column} = {value} WHERE {'AND'.join(conditions)}")

    def get_path(self):
        return ARTPATH

    def sync(self):
        self.images = {}

        files = [file for file in os.listdir(ARTPATH) if file[-4:] == ".pdf"]
        db_files = [row[0] for row in self.get("articles", "filename")]

        # check for files in database but not articles
        [self.drop_file_by_name(file) for file in db_files if file not in files]

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
            self.add("articles", file, title, author, pages, 0)

    def drop_file_by_name(self, filename):
        id_ = self.get("articles", "article_id", filename=filename)[0][0]
        # remove dependencies
        statement = f"DELETE FROM depends WHERE article_id = '{id_}' OR child_id = '{id_}'"
        self.execute(statement)
        # remove article
        statement = f"DELETE FROM articles WHERE filename = '{filename}'"
        self.execute(statement)

    def get_dependency_graph(self, main_url, depend_url):
        if (main_url, depend_url) not in self.images:
            self.create_images(main_url, depend_url)
        return tuple(self.images[main_url, depend_url])

    def create_images(self, main_url, depend_url):
        articles = self.get("articles", "article_id", "title", "author", "pages", "cur_page")
        main_graph = graphviz.Digraph()
        main_graph.graph_attr["nodesep"] = "1"
        main_graph.graph_attr["ranksep"] = "1"
        main_graph.graph_attr["id"] = "main_graph"

        solo_graph = graphviz.Graph()
        solo_graph.graph_attr["rankdir"] = "LR"
        solo_graph.graph_attr["id"] = "solo_graph"

        depends = self.get("depends", "*")

        connected_articles = [(e[1], e[2]) for e in depends]
        if depends:
            connected_articles = tuple(zip(*connected_articles))
            connected_articles = list(connected_articles[0]) + list(connected_articles[1])

        # add nodes
        for index, title, author, pages, curpage in articles:
            ratio = curpage / pages
            node = f"""
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
            if index in connected_articles:
                main_graph.body.append(node)
            else:
                solo_graph.body.append(node)

        # add edges
        ids = [article[0] for article in articles]
        for index, from_, to_, comment in depends:
            if from_ not in ids or to_ not in ids:
                continue
            main_graph.edge(f"N{from_}", f"N{to_}", comment, URL=f"{depend_url}/{index}", headport="n", tailport="s")

        main_img = main_graph.pipe(format='svg').replace(b"\r\n", b"").decode('utf-8')
        solo_img = solo_graph.pipe(format='svg').replace(b"\r\n", b"").decode('utf-8')

        # necessary to prevent id duplicates. Quick and dirty there has to be a proper way!
        solo_img = solo_img.replace("l_", "solo_l_")
        self.images[(main_url, depend_url)] = [main_img, solo_img]


class ConfigHandler:

    def __init__(self):
        # check if config file already exists
        if not os.path.isfile(PATH + CONFIGFILE):
            with open(PATH + CONFIGFILE, "wb") as doc:
                pickle.dump({}, doc)

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


BASE = Connection()
BASE.sync()

CONFIG = ConfigHandler()
