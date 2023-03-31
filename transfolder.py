import sys
import os


def evaluate_item(file, lang_tgt):
    print(file, lang_tgt)
    os.system(f'python ./LTranslate/translate.py {file} {lang_tgt}')


def main(argv):
    path, lang_tgt = argv

    list_of_files = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        if not dirpath.endswith(('tags', '_drafts', 'search')):
            for filename in filenames:
                if filename.endswith('.md') and filename != '404.md':
                    file = os.sep.join([dirpath, filename])
                    list_of_files.append(file)

    for file in list_of_files:
        evaluate_item(file, lang_tgt)


if __name__ == "__main__":
    main(sys.argv[1:])
