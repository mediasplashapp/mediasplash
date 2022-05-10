from bs4 import BeautifulSoup
def clean(filename):
    text = ""
    with open(filename, "r") as f:
        text = f.read()
    text = BeautifulSoup(text).get_text()
    with open(filename, "w") as f:
        f.write(text)