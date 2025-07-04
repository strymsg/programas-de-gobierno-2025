from langchain_text_splitters import MarkdownHeaderTextSplitter
import os
import re

def list_markdown_files(directory: str):
    """Returns the list of all markdown files in a given directory"""
    files = []
    for filename in os.listdir(directory):
        if filename.endswith(".md"):
            files.append(filename)
    return files


def load_markdown_files(directory: str) -> str:
    """Combine all .md files in directory into a single string"""
    combined = ""
    for filename in os.listdir(directory):
        if filename.endswith(".md"):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as f:
                # Remove special characters to reduce token noise
                cleaned = re.sub(r'[^\w\s.,;:!?()\-]', '', f.read())
                combined += f"--- {filename} ---\n{cleaned}\n\n"
    return combined


def get_markdown_file(directory: str, filename: str, clean=True) -> dict:
    """Given a directory and filename, returns its name and content"""
    filedict = {}
    
    with open(os.path.join(directory, filename), 'r', encoding='utf-8') as f:
        # Remove special characters to reduce token noise
        if clean:
            cleaned = re.sub(r'[^\w\s.,;:!?()\-]', '', f.read())
            filedict['content'] = cleaned
        else:
            filedict['content'] = f.read()
        filedict['name'] = filename
    return filedict


def get_markdown_sections(content: str):
    """Gets the markdown content as documents splited by their headers"""
    headers_to_split_on = [
        ("#", "H1"),
        ("##", "H2"),
        ("###", "H3"),
        ("####", "H4"),
        ("#####", "H5"),
        ("######", "H6"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on)
    return markdown_splitter.split_text(content)
