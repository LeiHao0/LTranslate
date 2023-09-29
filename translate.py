import requests
from retrying import retry
import tiktoken
import yaml
import sys

import os
import openai

import concurrent.futures
import time
import random

OPENAI_API_KEY = "OPENAI_API_KEY"

max_workers = 1


def load_conf():
    with open('LTranslate/conf.yml', 'r') as file:
        conf = yaml.load(file, Loader=yaml.FullLoader)
        os.environ[OPENAI_API_KEY] = conf[OPENAI_API_KEY]


def write_md(file_path, content: str):
    with open(file_path, "w") as file:
        file.write(content)


def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
            return file_content
    except FileNotFoundError:
        print("File not found.")
    except PermissionError:
        print("Permission denied to read the file.")
    except Exception as e:
        print("An error occurred:", str(e))
        return None


def count_token(content):
    return num_tokens_from_string(content, "cl100k_base")


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    num_tokens = len(encoding.encode(string))
    return num_tokens


def call_openai(file_content, lang):
    tokens = count_token(file_content)
    model = "gpt-3.5-turbo-16k" if tokens > 2000 else "gpt-3.5-turbo"
    print("tokens: ", tokens, "model: ", model)

    content = f'Fix this markdown document syntax error, then translate  to {lang}.'

    openai.api_key = os.getenv(OPENAI_API_KEY)

    response = openai.ChatCompletion.create(model=model,
                                            messages=[
                                                {"role": "system",
                                                    "content": content},
                                                {"role": "user",
                                                    "content": file_content},
                                            ])
    content = response['choices'][0]['message']['content']
    return content


def translate_file_to(inputs):
    file, to, lang = inputs
    print("translate_file_to: ", file, to, lang)
    text = translate_file(file, lang)
    text = text + '\n\n>Translated by gpt-3.5-turbo'
    write_md(to, text)
    return text


def translate_file(file, lang):
    content = read_file(file)
    if content:
        translated_text = call_openai(content, lang)

    return translated_text


def read_md_paths(path='.'):
    files = []
    for file in sorted(os.listdir(path), reverse=True):
        if file.endswith(".md"):
            file_path = os.path.join(path, file)
            files.append(file_path)
    return files


def translate(ori, to, lang='en'):
    load_conf()
    lang_dict = {
        "en": "English",
        "id": "Indonesian",
        "ja": "Japanese",
        "ko": "Korean",
        "vi": "Vietnamese",
        "tw": "Chinese (Traditional)",
    }

    if os.path.isdir(ori):
        md_paths = read_md_paths(ori)
        lang = lang_dict[lang]
        inputs = [(md, os.path.join(to, os.path.basename(md)), lang)
                  for md in md_paths]
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = executor.map(translate_file_to, inputs)
        return results

    elif os.path.isfile(ori):
        text = translate_file_to((ori, to, lang))
        return text


if __name__ == "__main__":
    load_conf()

    args = sys.argv[1:]
    if len(args) == 0:
        print("Please provide the file path or directory path")
        # sys.exit(1)
    elif len(args) == 1:
        print("Please provide the lang")
    elif len(args) == 2:
        ori, to = args
        translate(ori, to)
    elif len(args) == 3:
        ori, to, lang = args
        translate(ori, to, lang)
