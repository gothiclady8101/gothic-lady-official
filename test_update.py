from bs4 import BeautifulSoup

INDEX_FILE = "index.html"

with open(INDEX_FILE, "r", encoding="utf-8") as f:
    content = f.read()

soup = BeautifulSoup(content, 'html.parser')

with open("index_test_output.html", "w", encoding="utf-8") as f:
    f.write(str(soup))
