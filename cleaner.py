from bs4 import BeautifulSoup
from pysubparser.cleaners import ascii, brackets, formatting, lower_case

def clean(filename):
    text = ""
    with open(filename, "r") as f:
        text = f.read()
    text = brackets.clean(formatting.clean(text))
    with open(filename, "w") as f:
        f.write(text)