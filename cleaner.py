import re

def remove_empty_lines(string_with_empty_lines):
    lines = string_with_empty_lines.split("\n")
    non_empty_lines = [line for line in lines if line.strip() != ""]
    string_without_empty_lines = ""
    for line in non_empty_lines:
        string_without_empty_lines += line + "\n"
    return string_without_empty_lines
def clean(filename):
    text = ""
    with open(filename, "r", encoding= "utf_8_sig") as f:
        text = f.read()
    text = remove_empty_lines(text)
    text = re.sub(r"\{.*?\}", "", text)
    text = re.sub(r"\<.*?\>", "", text)
    text = re.sub(r"\<.*?\>", "", text)
    text = text.replace(r"\N", "")
    with open(filename, "w", encoding = "utf_8_sig") as f:
        f.write(text)
