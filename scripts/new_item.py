#!/usr/bin/env python3
import os
import yaml
import datetime

# Directories
POSTS_DIR = "_posts"
BOOKS_DIR = "_books"
LECTURES_DIR = "_lecture-notes"
DATA_DIR = "_data"
BOOKS_YML = os.path.join(DATA_DIR, "books.yml")
LECTURES_YML = os.path.join(DATA_DIR, "lecture-notes.yml")

# Helper functions
def slugify(title):
    """Convert a title to lowercase and dash-separated."""
    return title.strip().lower().replace(" ", "-")

def prompt_authors():
    authors = []
    print("Enter authors (blank line to finish):")
    while True:
        author = input("Author: ").strip()
        if not author:
            break
        authors.append(author)
    return authors

def add_to_yaml(file_path, name, link):
    if not os.path.exists(file_path):
        data = []
    else:
        with open(file_path, "r") as f:
            data = yaml.safe_load(f) or []

    # Avoid duplicates
    for entry in data:
        if entry.get("name") == name:
            print(f"Entry '{name}' already exists in {file_path}")
            return

    data.append({"name": name, "link": link})
    with open(file_path, "w") as f:
        yaml.dump(data, f, sort_keys=False)

def create_file(path, frontmatter):
    if os.path.exists(path):
        print(f"File {path} already exists!")
        return
    with open(path, "w") as f:
        f.write(frontmatter + "\n")
    print(f"Created {path}")

# Main program
def main():
    item_type = input("Type (book, lecture, blog): ").strip().lower()
    if item_type not in ["book", "lecture", "blog"]:
        print("Invalid type!")
        return

    title = input("Title: ").strip()
    slug = slugify(title)

    if item_type == "book":
        authors = prompt_authors()
        year = input("Year: ").strip()
        file_path = os.path.join(BOOKS_DIR, f"{slug}.md")
        frontmatter = "---\n"
        frontmatter += f"title: {title}\n"
        frontmatter += "authors:\n"
        for author in authors:
            frontmatter += f"  - {author}\n"
        frontmatter += f"year: {year}\n"
        frontmatter += "---"
        create_file(file_path, frontmatter)
        add_to_yaml(BOOKS_YML, title, f"/books/{slug}")

    elif item_type == "lecture":
        file_path = os.path.join(LECTURES_DIR, f"{slug}.md")
        frontmatter = f"---\ntitle: {title}\n---"
        create_file(file_path, frontmatter)
        add_to_yaml(LECTURES_YML, title, f"/lecture-notes/{slug}")

    elif item_type == "blog":
        today = datetime.date.today().strftime("%Y-%m-%d")
        file_path = os.path.join(POSTS_DIR, f"{today}-{slug}.md")
        frontmatter = f"---\ntitle: {title}\n---"
        create_file(file_path, frontmatter)

if __name__ == "__main__":
    main()
