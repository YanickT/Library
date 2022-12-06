import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb
import tkinter.filedialog as fd
import importlib
import os


class Widget:

    def __init__(self):
        self.path = None

        self.root = tk.Tk()
        self.root.title("Setup assistance")
        self.root.geometry("250x320")
        self.root.minsize(500, 320)
        self.root.maxsize(500, 320)

        # REQUIREMENTS
        frame_requirements = ttk.Frame(self.root, borderwidth=1, relief="groove")
        frame_requirements.pack(pady=5, padx=5, fill=tk.X)
        ttk.Label(frame_requirements, text="REQUIREMENTS:", anchor="w").pack(padx=5, pady=5, fill=tk.X)

        checks = []
        requirements = self.get_requirements()
        for req in requirements:
            checks.append(tk.Checkbutton(frame_requirements, text=f"{req}"))
            checks[-1].pack(padx=1, pady=1, fill=tk.X)

        # FILES
        frame_options = ttk.Frame(self.root, borderwidth=1, relief="groove")
        frame_options.pack(pady=5, padx=5, fill=tk.X)
        ttk.Label(frame_options, text="FILES:", anchor="w").pack(padx=5, pady=5, fill=tk.X)

        self.path_label = ttk.Label(frame_options, text="please select path", anchor="w")
        self.path_label.pack(padx=5, pady=5, fill=tk.X)
        self.path_articles = ttk.Label(frame_options, text="please select path", anchor="w")
        self.path_articles.pack(padx=5, pady=5, fill=tk.X)
        self.path_db = ttk.Label(frame_options, text="please select path", anchor="w")
        self.path_db.pack(padx=5, pady=5, fill=tk.X)

        ttk.Button(frame_options, text="Select path", command=self.choose_path).pack(padx=5, pady=5, fill=tk.X)
        ttk.Button(frame_options, text="Create folders", command=self.create_folders).pack(padx=5, pady=5, fill=tk.X)

        for i, req in enumerate(requirements):
            if self.check_requirement(req):
                checks[i].select()
            else:
                checks[i].deselect()
            checks[i].config(state="disabled")
        self.root.mainloop()

    @staticmethod
    def get_requirements():
        with open(f"{os.path.dirname(os.path.realpath(__file__))}/requirements.txt", "r") as doc:
            reqs = doc.readlines()
        return [req.replace("\n", "") for req in reqs]

    @staticmethod
    def check_requirement(name):
        result = importlib.util.find_spec(name) is not None
        if not result:
            mb.showerror(title=f"Requirement {name}", message=f"Requirement {name} not satisfied")
        return result

    def create_folders(self):
        if self.path is None:
            mb.showerror(title=f"Select path", message="Choose a path first")
            return

        os.mkdir(f"{self.path}/Library")
        os.mkdir(f"{self.path}/Library/Article/")
        with open(f"{os.path.dirname(os.path.realpath(__file__))}/path.py", "w") as doc:
            doc.write(f"PATH = '{self.path}/Library/'")
        self.root.quit()
        self.root.destroy()

    def choose_path(self):
        self.path = fd.askdirectory()
        self.path_label.config(text=f"{self.path}/Library")
        self.path_articles.config(text=f"{self.path}/Library/Article/")
        self.path_db.config(text=f"{self.path}/Library/article.db")


if __name__ == "__main__":
    Widget()
