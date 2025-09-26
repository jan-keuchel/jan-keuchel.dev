#!/usr/bin/env python3
import os
import yaml
import datetime

# Directories
POSTS_DIR = "_posts"
BOOKS_DIR = "_books"
LECTURES_DIR = "_lecture-notes"
PROJECTS_DIR = "_projects"

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

def create_file(path, frontmatter):
    if os.path.exists(path):
        print(f"File {path} already exists!")
        return
    with open(path, "w") as f:
        f.write(frontmatter + "\n")
    print(f"Created {path}")

# Main program
def main():
    item_type = input("Type (book, lecture, blog, project): ").strip().lower()
    if item_type not in ["book", "lecture", "blog", "project"]:
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
        frontmatter += "desc: [description of the file]\n"
        frontmatter += "published: [Date of publishing]\n"
        frontmatter += "---"
        create_file(file_path, frontmatter)

    elif item_type == "lecture":
        file_path = os.path.join(LECTURES_DIR, f"{slug}.md")
        frontmatter = f"---\n"
        frontmatter += f"title: {title}\n"
        frontmatter += "desc: [description of the file]\n"
        frontmatter += "published: [Date of publishing]\n"
        frontmatter += "logo: /assets/images/[Logo-name.png]\n"
        frontmatter += "source_url: [https://source-of-the-lecture.com/lecture-page]\n"
        frontmatter += "---"
        create_file(file_path, frontmatter)

    elif item_type == "blog":
        today = datetime.date.today().strftime("%Y-%m-%d")
        file_path = os.path.join(POSTS_DIR, f"{today}-{slug}.md")
        frontmatter = "---\n"
        frontmatter += f"title: {title}\n"
        frontmatter += "desc: [description of the file]\n"
        frontmatter += "published: [Date of publishing]\n"
        frontmatter += "---"
        create_file(file_path, frontmatter)

    elif item_type == "project":
        file_path = os.path.join(PROJECTS_DIR, f"{slug}.md")
        frontmatter = "---\n"
        frontmatter += f"title: {title}\n"
        frontmatter += "desc: [description of the file]\n"
        frontmatter += "published: [Date of publishing]\n"
        frontmatter += "---"
        create_file(file_path, frontmatter)
if __name__ == "__main__":
    main()
