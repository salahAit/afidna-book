
import os
import subprocess
import glob

SOURCE_DIR = "/home/msi/Desktop/book"
BUILD_DIR = "/home/msi/Desktop/book/latex_build"
PREAMBLE_PATH = os.path.join(BUILD_DIR, "preamble.tex")
TITLEPAGE_PATH = os.path.join(BUILD_DIR, "titlepage.tex")
MAIN_TEX_PATH = os.path.join(BUILD_DIR, "main.tex")
OUTPUT_PDF_NAME = "book.pdf"

def get_markdown_files():
    files = []
    # Walk through the directory to find markdown files
    for root, dirs, filenames in os.walk(SOURCE_DIR):
        if "latex_build" in root:
            continue
        for filename in filenames:
            if filename.endswith(".md") and filename != "TABLE_OF_CONTENTS.md":
                full_path = os.path.join(root, filename)
                files.append(full_path)
    
    # Sort files to ensure correct order
    # This might need adjustment based on exact naming convention, 
    # but generally alphabetic sort on full path works if naming is consistent
    files.sort()
    return files

import re

def convert_md_to_tex(md_file, output_tex_file):
    # Read original content
    with open(md_file, "r") as f:
        content = f.read()

    # Pre-process content: Remove redundant "Chapter X:" from H1 headers
    # Matches "# Chapter 1: Title" -> "# Title"
    content = re.sub(r'^#\s+Chapter\s+\d+:\s*', '# ', content, flags=re.MULTILINE)

    # Write to temp file
    temp_md = md_file + ".temp"
    with open(temp_md, "w") as f:
        f.write(content)

    try:
        cmd = ["pandoc", temp_md, "-o", output_tex_file, "--top-level-division=chapter", "--listings"]
        subprocess.run(cmd, check=True)
    finally:
        if os.path.exists(temp_md):
            os.remove(temp_md)

def generate_main_tex(tex_files):
    with open(MAIN_TEX_PATH, "w") as f:
        f.write("\\documentclass[12pt, a4paper]{report}\n")
        
        # Input preamble
        f.write(f"\\input{{{os.path.basename(PREAMBLE_PATH)}}}\n")
        f.write("\\begin{document}\n")
        
        # Input title page
        f.write(f"\\input{{{os.path.basename(TITLEPAGE_PATH)}}}\n")
        
        f.write("\\tableofcontents\n")
        f.write("\\newpage\n")
        
        for tex_file in tex_files:
            # Use relative path for input to keep clean
            rel_path = os.path.basename(tex_file)
             # Removing extension for input command is standard but explicit extension works too.
             # We will put all converted tex files in BUILD_DIR so just basename is enough
            f.write(f"\\input{{{rel_path}}}\n")
            
        f.write("\\end{document}\n")

def main():
    if not os.path.exists(BUILD_DIR):
        os.makedirs(BUILD_DIR)

    print("Finding markdown files...")
    md_files = get_markdown_files()
    tex_files = []

    print(f"Found {len(md_files)} files.")
    for md_file in md_files:
        print(f"Processing: {md_file}")
        # Create a flat list of tex files in build dir
        # To avoid name collisions if any, we could prepend parent dir name, 
        # but let's assume unique filenames for now or append index.
        base_name = os.path.basename(md_file).replace(".md", ".tex")
        # Prepend part/folder name to ensure uniqueness and easier debugging
        parent_dir = os.path.basename(os.path.dirname(md_file))
        if parent_dir and parent_dir != "book":
             base_name = f"{parent_dir}_{base_name}"
        
        output_tex = os.path.join(BUILD_DIR, base_name)
        convert_md_to_tex(md_file, output_tex)
        tex_files.append(output_tex)

    print("Generating main.tex...")
    generate_main_tex(tex_files)

    print("Compiling PDF...")
    # Run pdflatex twice for TOC
    subprocess.run(["xelatex", "-interaction=nonstopmode", "main.tex"], cwd=BUILD_DIR, check=True)
    subprocess.run(["xelatex", "-interaction=nonstopmode", "main.tex"], cwd=BUILD_DIR, check=True)
    
    print(f"Build complete. Check {os.path.join(BUILD_DIR, OUTPUT_PDF_NAME)}")

if __name__ == "__main__":
    main()
