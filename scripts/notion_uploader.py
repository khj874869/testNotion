import os


NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

POSTS_DIR = "posts"

def extract_metadata_and_content(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    title = "Untitled"
    content_lines = []
    tags = []
    found_delimiter = False

    for i, line in enumerate(lines):
        if i == 0 and line.startswith("#"):
            title = line.replace("#", "").strip()
            continue
        if line.strip() == '---':
            found_delimiter = True
            continue
        if found_delimiter and line.startswith("tags:"):
            tag_line = line.replace("tags:", "").strip()
            tags = [tag.strip() for tag in tag_line.split(",") if tag.strip()]
            break
        content_lines.append(line)

    content = "".join(content_lines).strip()
    return title, content, tags

def create_notion_page(title, content, tags):
    html_content = markdown.markdown(content)
    children = [{
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": [{"type": "text", "text": {"content": content}}]}
    }]

    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": title}}]},
            "Tags": {"multi_select": [{"name": tag} for tag in tags]},
            "Date": {"date": {"start": datetime.utcnow().isoformat()}}
        },
        "children": children
    }

    res = requests.post("https://api.notion.com/v1/pages", json=data, headers=HEADERS)
    if res.status_code != 200:
        print(f"Failed to create page: {res.text}")
    else:
        print(f"Successfully posted: {title}")

def main():
    for file in os.listdir(POSTS_DIR):
        if file.endswith(".md"):
            path = os.path.join(POSTS_DIR, file)
            title, content, tags = extract_metadata_and_content(path)
            create_notion_page(title, content, tags)

if __name__ == '__main__':
    main()
