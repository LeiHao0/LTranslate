import os
from translate import translate

files = [
    "cn/source/_posts/xx.md",
]


os.chdir(os.path.dirname(os.path.realpath(__file__)))
# cd to ../
os.chdir("..")

l = 'en'
for f in files:
    fn = os.path.basename(f)
    to = f"{l}/source/_posts/{fn}"
    translate(f, to, l)
