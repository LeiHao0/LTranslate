import yaml
import sys

import os
import openai

import concurrent.futures
import time
import random

OPENAI_API_KEY = "OPENAI_API_KEY"
TO_LANGUAGE = "TO_LANGUAGE"

max_workers = 3

def load_conf():
    with open('conf.yml', 'r') as file:
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


def call_openai(file_content, lang):
    
    openai.api_key = os.getenv(OPENAI_API_KEY)
    content = f'Fix this markdown document syntax error, then translate  to {lang}.'

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo-16k",
                                            messages=[
                                                {"role": "system",
                                                    "content": content},
                                                {"role": "user",
                                                    "content": file_content},
                                            ])
    content = response['choices'][0]['message']['content']

    log = f'from {len(file_content)} chars to {len(content)} chars\n'
    print(log)
    return content


def call_openai_async(inputs):
    file, to, file_chunks = inputs

    filename = os.path.basename(file)
    to_file = os.path.join(to, filename)

    if os.path.isfile(to_file):
        print(f'{to_file} already exists')
        return

    print(f'Processing {file} to {to_file} ...')

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(call_openai, file_chunks))

        translated_text = '\n\n'.join(results) + '\n\n>Powered by OpenAI, gpt-3.5-turbo-16k'

        write_md(to_file, translated_text)
        return translated_text


def translate_file(file, to, lang):
    content = read_file(file)
    if content:
        translated_text = call_openai(content, lang)
        write_md(to, translated_text)

    return translated_text

def translate_files(files, to, lang):
    inputs = [(file, lang, translate_file(file, lang)) for file in files]

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(call_openai_async, inputs))
        return results


def read_all_md_files(path='.'):
    files = []
    for file in sorted(os.listdir(path), reverse=True):
        if file.endswith(".md"):
            file_path = os.path.join(path, file)
            files.append(file_path)
    return files


def translate(ori, to, lang):
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
        files = read_all_md_files(ori)
        translate_files(ori, to, lang)
    elif os.path.isfile(ori):
        translate_file(ori, to, lang)


if __name__ == "__main__":
    load_conf()

    args = sys.argv[1:]
    if len(args) == 0:
        print("Please provide the file path or directory path")
        # sys.exit(1)
    elif len(args) == 2:
        ori, to = args
        translate(ori, to)
    elif len(args) == 3:
        ori, to, lang = args
        translate(ori, to, lang)
