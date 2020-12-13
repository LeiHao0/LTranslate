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
        if l.strip() == '<!--more-->' or not l.strip():
            transLine = l
        elif l.startswith(('```', '{% ', '<details>')):
            skip = not skip
            transLine = l
        elif l.startswith('- '):
            transLine = '- ' + translate(l[1:])
        elif l.startswith('$$'):
            transLine = l
        else:
            if skip:
                transLine = l
            else:
                transLine = translate(l)
        transLine = ' '*leadingSpaces + transLine + '\n'
        print(line, ' -> ', transLine)
        transText += transLine

    print('\n\n', '-'*80, '\n\n', transText)
    return transText


def file2Lines():
    return [line.rstrip('\n') for line in open(filename)]


def trans2File(transText):
    f = open(os.path.splitext(filename)[0]+"_" + lang_tgt + ".md", 'w')
    f.write(transText)
    f.close()


def main(argv):
    global filename, lang_src, lang_tgt
    filename, lang_src, lang_tgt = argv
    trans2File(markdown(file2Lines()))


if __name__ == "__main__":
    main(sys.argv[1:])
