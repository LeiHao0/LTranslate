import sys
import os
import concurrent.futures


def evaluate_item(file, lang_src, lang_tgt):
    print(file, lang_src, lang_tgt)
    os.system(
        f'python3 ./LTranslate/translate.py {file} {lang_src} {lang_tgt}')


def main(argv):
    path, lang_src, lang_tgt = argv

    list_of_files = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        if not dirpath.endswith(('tags', '_drafts', 'search')):
            for filename in filenames:
                if filename.endswith('.md') and filename != '404.md':
                    file = os.sep.join([dirpath, filename])
                    list_of_files.append(file)

    with concurrent.futures.ProcessPoolExecutor(max_workers=12) as executor:
        for file in list_of_files:
            executor.submit(evaluate_item, file, lang_src, lang_tgt)


if __name__ == "__main__":
    main(sys.argv[1:])
