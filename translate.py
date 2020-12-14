import getopt
import sys
import os
from google_trans_new import google_translator
# https://github.com/lushan88a/google_trans_new

# translate.py filename lang_src lang_tgt

# lang:

# https://cloud.google.com/translate/docs/languages

translator = google_translator()


def translate(text):
    return translator.translate(text, lang_src=lang_src, lang_tgt=lang_tgt)


def markdown(lines):
    transText = ""
    skip = False
    for line in lines:
        transLine = ""
        l = line.lstrip(' ')
        leadingSpaces = len(line) - len(l)
        if l.strip() == '<!--more-->' or l.strip() == '---' or l.strip() == '':
            transLine = l
        elif l.startswith('title: '):
            transLine = 'title: ' + translate(l[6:])
        elif l.startswith(('$$', '![](', 'type: ', 'date: ', 'update: ', 'updated: ', 'permalink: ', 'tags: ', 'mathjax: ')):
            transLine = l
        elif l.startswith(('```', '{% ', '<details>', '</details>')):
            skip = not skip
            transLine = l
        elif l.startswith('1. '):
            transLine = '1. ' + translate(l[3:])
        elif l.startswith('> '):
            transLine = '> ' + translate(l[1:])
        elif l.startswith('- '):
            transLine = '- ' + translate(l[1:])
        elif l.startswith('# '):
            transLine = '# ' + translate(l[1:])
        elif l.startswith('## '):
            transLine = '## ' + translate(l[2:])
        elif l.startswith('### '):
            transLine = '### ' + translate(l[3:])
        elif l.startswith('#### '):
            transLine = '#### ' + translate(l[4:])
        elif l.startswith('type: '):
            transLine = 'type: ' + translate(l[5:])
        else:
            if skip:
                transLine = l
            else:
                transLine = translate(l)
        for k, v in {'【': '[', '（': '(', '）': ')', '【': ']'}.items():
            transLine = transLine.replace(k, v)

        transLine = ' '*leadingSpaces + transLine + '\n'
        # print(line, ' -> ', transLine)
        transText += transLine

    # print('\n\n', '-'*80, '\n\n', transText)
    return transText


def file2Lines():
    f = open(filename, 'r')
    lines = [line.rstrip('\n') for line in f]
    f.close()
    return lines


def trans2File(transText):
    f = open(filename, 'w')
    f.write(transText)
    f.close()


def main(argv):
    global filename, lang_src, lang_tgt
    filename, lang_src, lang_tgt = argv

    trans2File(markdown(file2Lines()))


if __name__ == "__main__":
    main(sys.argv[1:])
