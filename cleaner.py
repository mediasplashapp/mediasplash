from pysubparser.cleaners import ascii, brackets, formatting, lower_case
import re
def clean(filename):
    text = ""
    with open(filename, "r") as f:
        text = f.read()
    text = re.sub("\{.*?\}", "", text)
    text = re.sub("\<.*?\>", "", text)
    text = re.sub("\<.*?\>", "", text)
    text = text.replace(r"\N", "")
    with open(filename, "w") as f:
        f.write(text)