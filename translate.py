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


def split_file_by_char_num(file_path, c=888):
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

    # log = f'from {len(file_content)} chars, {len(file_content)/1024} kb\n'
    # print(log)
    
    # time.sleep(random.randint(1, 3))
    # return file_content

    lang = os.getenv(TO_LANGUAGE)
    openai.api_key = os.getenv(OPENAI_API_KEY)
    content = f'Translate text to {lang}. Keep whitespace and newlines. Keep the same markdown syntax. Only return translated result with the same markdown format.'

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
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

        translated_text = '\n\n'.join(results) + '\n\n>Powered by OpenAI, gpt-3.5-turbo-0301'

        write_md(to_file, translated_text)
        return translated_text


def translate_file(file, to):
    file_chunks = split_file_by_char_num(file)
    content = call_openai_async((file, to, file_chunks))

    return content


def translate_files(files, to):
    inputs = [(file, to, split_file_by_char_num(file)) for file in files]

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
        "ar": "Arabic",
        "de": "German",
        "en": "English",
        "fr": "French",
        "id": "Indonesian",
        "ja": "Japanese",
        "ko": "Korean",
        "ru": "Russian",
        "vi": "Vietnamese",
        "tw": "Chinese (Traditional)",
        "zh": "Chinese (Simplified)",
    }
    os.environ[TO_LANGUAGE] = lang_dict[lang]

    if os.path.isdir(ori):
        files = read_all_md_files(ori)
        translate_files(files, to)
    elif os.path.isfile(ori):
        translate_file(ori, to)


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
