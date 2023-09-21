#!/usr/bin/env python3

import os
import shutil
import subprocess
from translate import translate


def ignore_posts_folder(dir, files):
    """Ignore the .git, "_posts", "about", "books" folder"""
    return [f for f in files if f == ".git" or f == "_posts" or f == "about" or f == "books"]


def ignore_git_folder(dir, files):
    return [f for f in files if f == ".git"]


def copy_to_lang(languages):
    # Copy directories
    for l in languages:
        # shutil.rmtree(l, ignore_errors=True)
        shutil.copytree("cn", l, dirs_exist_ok=True,
                        ignore=ignore_posts_folder)
        with open(f"{l}/_config.yml", "r") as f:
            config = f.read()
            config = config.replace("zh-CN", l)
            config = config.replace("/cn/", f"/{l}/")
        with open(f"{l}/_config.yml", "w") as f:
            f.write(config)

        shutil.copy("cn/source/404.md", f"{l}/source/404.md")
        with open(f"{l}/source/404.md", "r") as f:
            content = f.read()
            if l == "en":
                content = content.replace("/cn/", "/")
            else:
                content = content.replace("/cn/", f"/{l}/")
        with open(f"{l}/source/404.md", "w") as f:
            f.write(content)

    # Translate using LTranslate
    for l in languages:
        fld = ["_posts", "about", "books"]
        for f in fld:
            ori = f"cn/source/{f}"
            to = f"{l}/source/{f}"
            os.makedirs(to, exist_ok=True)
            print(f"Translating {ori} to {to}")
            translate(ori, to, l)

    # cp en to root
    dirs_to_copy = ["node_modules", "scaffolds", "source", "themes"]
    files_to_copy = ["_config.next.yml", "_config.yml", "db.json",
                     "package-lock.json", "package.json", "yarn.lock"]

    for d in dirs_to_copy:
        shutil.rmtree(d, ignore_errors=True)
        shutil.copytree(f"en/{d}", d, dirs_exist_ok=True,
                        ignore=ignore_git_folder)
    for f in files_to_copy:
        shutil.copy(f"en/{f}", f)
    with open("_config.yml", "r") as f:
        config = f.read()
        config = config.replace("/en/", "/")
    with open("_config.yml", "w") as f:
        f.write(config)

    # delete en folder
    # shutil.rmtree("en", ignore_errors=True)


if __name__ == "__main__":
    # cd to python script directory
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    # cd to ../
    os.chdir("..")
    print(os.getcwd())
    langs = ["en", "ja", "ko", "vi", "tw"]
    copy_to_lang(langs)
    # langs = ["de", "id", "ar", "fr", "ru", "tw"]
    # langs = ["de", "id", "ar", "fr", "ru"]
    # copy_to_lang(langs)
