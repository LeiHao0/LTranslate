import os
from google_trans_new import google_translator

# https://github.com/lushan88a/google_trans_new

translator = google_translator()

filename = 'test1.md'
lang_src = 'zh-cn'
lang_tgt = 'en'


def translate(text):
    return translator.translate(text)


def markdown(lines):
    transText = ""
    skip = False
    for line in lines:
        transLine = ""
        l = line.lstrip(' ')
        leadingSpaces = len(line) - len(l)
        if l.strip() == '<!--more-->' or not l.strip():
            transLine = l
        elif l.startswith(('```', '$$')):
            skip = not skip
            transLine = l
        elif l.startswith('- '):
            transLine = '- ' + translate(l[1:])
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


def test():
    transText = markdown(file2Lines())
    trans2File(transText)


test()
