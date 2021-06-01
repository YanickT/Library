import os
import graphviz
import sqlite3
from PyPDF2 import PdfFileReader
from path import PATH

ARTPATH = PATH + "Article/"
ARTICLEFILE = "article.db"
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

    @staticmethod
    def execute(statement):
        conn = sqlite3.connect(PATH + ARTICLEFILE)
        cur = conn.cursor()
        cur.execute(statement)
        conn.commit()
        conn.close()

    @staticmethod
    def get(statement):
        conn = sqlite3.connect(PATH + ARTICLEFILE)
        cur = conn.cursor()
        cur.execute(statement)
        data = cur.fetchall()
        conn.close()
        return data

    def get_articles(self):
        statement = "SELECT article_id, title, author, pages, cur_page FROM articles"
        return self.get(statement)

    def get_dependency_graph(self, main_url, depend_url):
        articles = self.get_articles()
        graph = graphviz.Digraph()
        graph.graph_attr["nodesep"] = "1"
        graph.graph_attr["ranksep"] = "1"

        # add nodes
        for index, title, author, pages, curpage in articles:
            percentage = curpage / pages
            node = f"""
                N{index} [
                shape=plain
                label=<
                    <table cellborder="0" cellspacing="5">
                        <tr><td colspan="2">{title}</td></tr>
                        <tr><td colspan="2">{author}</td></tr>
                        <tr><td border="1" width="50" bgcolor="#6da8ce;{min(percentage + 0.01, 1):.2f}:white"></td><td color="white">{percentage * 100:.0f}%</td></tr>
                    </table>
                >
                URL = "{main_url}/{index}"
                ]
                """
            graph.body.append(node)

        # add edges
        depends = self.get_dependencies()
        ids = [article[0] for article in articles]
        for index, from_, to_, comment in depends:
            if from_ not in ids or to_ not in ids:
                continue
            graph.edge(f"N{from_}", f"N{to_}", comment, URL=f"{depend_url}/{index}", headport="n", tailport="s")

        return graph.pipe(format='svg').replace(b"\r\n", b"").decode('utf-8')

    def get_pages(self, article):
        statement = f"SELECT pages FROM articles WHERE article_id = {article}"
        pages = self.get(statement)[0][0]
        return pages

    def get_curpage(self, article):
        statement = f"SELECT cur_page FROM articles WHERE article_id = {article}"
        page = self.get(statement)[0][0]
        return page

    def update_curpage(self, article, page):
        statement = f"UPDATE articles SET cur_page = {page} WHERE article_id = {article}"
        self.execute(statement)

    def get_filename(self, article):
        statement = f"SELECT filename FROM articles WHERE article_id = {article}"
        file = self.get(statement)[0][0]
        return file

    def get_author(self, article):
        statement = f"SELECT author FROM articles WHERE article_id = {article}"
        author = self.get(statement)[0][0]
        return author

    def update_author(self, article, author):
        statement = f"UPDATE articles SET author = '{author}' WHERE article_id = {article}"
        self.execute(statement)

    def get_title(self, article):
        statement = f"SELECT title FROM articles WHERE article_id = {article}"
        title = self.get(statement)[0][0]
        return title

    def get_titles(self):
        statement = f"SELECT title FROM articles"
        title = [row[0] for row in self.get(statement)]
        return title

    def update_title(self, article, title):
        statement = f"UPDATE articles SET title = '{title}' WHERE article_id = {article}"
        self.execute(statement)

    def add_file(self, filename, title, author, pages):
        statement = f"INSERT INTO articles VALUES (NULL, '{filename}', '{title}','{author}', '{pages}', 0)"
        self.execute(statement)

    def get_filenames(self):
        statement = f"SELECT filename FROM articles"
        filenames = [row[0] for row in self.get(statement)]
        return filenames

    def get_path(self):
        return ARTPATH

    def drop_file_by_name(self, filename):
        statement = f"SELECT article_id FROM articles WHERE filename = '{filename}'"
        id_ = self.get(statement)[0][0]
        # remove dependencies
        statement = f"DELETE FROM depends WHERE article_id = '{id_}' OR child_id = '{id_}'"
        self.execute(statement)
        # remove article
        statement = f"DELETE FROM articles WHERE filename = '{filename}'"
        self.execute(statement)

    def sync(self):
        files = [file for file in os.listdir(ARTPATH) if file[-4:] == ".pdf"]
        db_files = self.get_filenames()

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

            if infos.title != "":
                title = infos.title
            else:
                title = file[:-4]

            if infos.author != "":
                author = infos.author
            else:
                author = "Unkown author"
            self.add_file(file, title, author, pages)


    def get_tasks(self):
        statement = f"SELECT comment FROM tasks"
        tasks = [row[0] for row in self.get(statement)]
        return tasks

    def add_task(self, task):
        statement = f"INSERT INTO tasks VALUES (NULL, '{task}')"
        self.execute(statement)

    def remove_task(self, task):
        statement = f"DELETE FROM tasks WHERE comment = '{task}'"
        self.execute(statement)


    def add_dependency(self, parent, child, comment=""):
        statement = f"INSERT INTO depends VALUES (NULL, {parent}, {child}, '{comment}')"
        self.execute(statement)

    def get_dependencies(self):
        statement = "SELECT * FROM depends"
        return self.get(statement)

    def get_dependency(self, index):
        statement = f"SELECT * FROM depends WHERE depend_id = {index}"
        return self.get(statement)[0]

    def update_depends_comment(self, index, comment):
        statement = f"UPDATE depends SET comment = '{comment}' WHERE depend_id = {index}"
        self.execute(statement)

    def drop_depend(self, index):
        statement = f"DELETE FROM depends WHERE depend_id = '{index}'"
        self.execute(statement)


BASE = Connection()
BASE.sync()
