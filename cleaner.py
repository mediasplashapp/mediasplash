import re


def clean(filename):
    text = ""
    with open(filename, "r", encoding="utf-8") as f:
        text = f.read()
    text = re.sub(r"\{.*?\}", "", text)
    text = re.sub(r"\<.*?\>", "", text)
    text = re.sub(r"\<.*?\>", "", text)
    text = text.replace(r"\N", "")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
