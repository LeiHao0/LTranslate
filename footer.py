import os
import glob

# cd to python script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))


fld = ["_posts", "about", "books"]


string_to_add = '\n\n>Powered by OpenAI, gpt-3.5-turbo-0301'

for fd in fld:
    path = f'../en/source/{fd}'

    for file in sorted(os.listdir(path), reverse=True):

        if file.endswith(".md"):
            filename = os.path.join(path, file)
            with open(filename, 'a') as file:  # open the file in append mode
                file.write(string_to_add)  # add the string to the end of the file

