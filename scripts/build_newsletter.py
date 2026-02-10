import os
import yaml
import markdown
from jinja2 import Environment, FileSystemLoader
import re


CONTENT_DIR = "content"
TEMPLATE_DIR = "templates"
DIST_DIR = "dist"
BASE_IMAGE_URL = "https://quentin1500.github.io/newsletter-brocconotte/"

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

def load_meta(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def md_to_html(path):
    with open(path, "r") as f:
        return markdown.markdown(f.read())

def absolutize_image_paths(html, issue):
    def repl(match):
        before = match.group(1)  # attributs avant src (ex: alt="image")
        src = match.group(2)      # valeur du src
        after = match.group(3)    # tout après le src (ex: /)
        if src.startswith("http"):
            absolute_url = src
        else:
            absolute_url = f'{BASE_IMAGE_URL}content/{issue}/{src}'
        return f'<img{before} src="{absolute_url}"{after}>'

    return re.sub(r'<img([^>]*?) src="([^"]+)"([^>]*)>', repl, html)

def build_newsletter(issue):
    issue_path = os.path.join(CONTENT_DIR, issue)
    meta = load_meta(os.path.join(issue_path, "meta.yml"))

    intro = md_to_html(os.path.join(issue_path, "intro.md"))

    articles_html = ""
    for file in sorted(os.listdir(issue_path)):
        if file.startswith("article") and file.endswith(".md"):
            article_html = md_to_html(os.path.join(issue_path, file))
            article_html = absolutize_image_paths(article_html, issue)
            articles_html += article_html

    template = env.get_template("newsletter.html")
    html = template.render(
        title=meta["title"],
        date=meta["date"],
        intro=intro,
        articles=articles_html
    )

    os.makedirs(DIST_DIR, exist_ok=True)
    output_path = os.path.join(DIST_DIR, f"{issue}.html")
    with open(output_path, "w") as f:
        f.write(html)

    print(f"Newsletter générée : {output_path}")

if __name__ == "__main__":
    issues = sorted(os.listdir(CONTENT_DIR))
    build_newsletter(issues[-1])  # dernière édition
