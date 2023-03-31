import yaml
import sys

import os
import openai

import concurrent.futures
import time
import random

OPENAI_API_KEY = "OPENAI_API_KEY"
TO_LANGUAGE = "TO_LANGUAGE"


def load_conf():
    with open('conf.yml', 'r') as file:
        conf = yaml.load(file, Loader=yaml.FullLoader)
        os.environ[OPENAI_API_KEY] = conf[OPENAI_API_KEY]


def split_file_by_char_num(file_path, c=1000):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        split_lines = []
        text = ''
        for line in lines:
            text += line
            if len(text) >= c:
                split_lines.append(text)
                text = ''
        if text != '':
            split_lines.append(text)

        joined_lines = [''.join(sublist) for sublist in split_lines]
        return joined_lines


def write_md(file_path, content: str):
    with open(file_path, "w") as file:
        file.write(content)


def call_openai(file_content):

    log = f'{len(file_content)} characters, {len(file_content)/1024} kb\n'
    print(log)

    # sleep 1s - 3s
    time.sleep(random.randint(1, 3))
    return file_content

    lang = os.getenv(TO_LANGUAGE)
    openai.api_key = os.getenv(OPENAI_API_KEY)
    content = f'Translate markdown text to {lang}. Keep whitespace and newlines. Keep the same markdown syntax. Only return translated result in the same markdown format.'

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                            messages=[
                                                {"role": "system",
                                                    "content": content},
                                                {"role": "user",
                                                    "content": file_content},
                                            ])
    content = response['choices'][0]['message']['content']
    return content


def call_openai_async(inputs):
    file, file_chunks = inputs

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(call_openai, file_chunks))

        translated_text = '\n\n'.join(results)
        print(f"translated a {file} to {len(translated_text)}")

        # write_md(file, translated_text)
        return translated_text


def translate_file(file):
    file_chunks = split_file_by_char_num(file)
    content = call_openai_async((file, file_chunks))

    return content


def translate_files(files):
    inputs = [(file, split_file_by_char_num(file)) for file in files]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(call_openai_async, inputs))
        return results


def read_all_md_files(path='.'):
    files = []
    for file in os.listdir(path):
        if file.endswith(".md"):
            file_path = os.path.join(path, file)
            files.append(file_path)
    return files


if __name__ == "__main__":
    load_conf()

    args = sys.argv[1:]
    lang = 'en'
    if len(args) > 1:
        # de, en, id, ja, ko, ru, vi, tw
        lang_dict = {
            "de": "German",
            "en": "English",
            "id": "Indonesian",
            "ja": "Japanese",
            "ko": "Korean",
            "ru": "Russian",
            "vi": "Vietnamese",
            "tw": "Chinese (Traditional)",
        }
        lang = args[1]
        os.environ[TO_LANGUAGE] = lang_dict[lang]
    else:
        print('please input language code, like de, en, id, ja, ko, ru, vi, tw')
    if len(args) > 0:
        path = args[0]
        if os.path.isdir(path):
            files = read_all_md_files(path)
            translate_files(files)
        elif os.path.isfile(path):
            translate_file(path)
