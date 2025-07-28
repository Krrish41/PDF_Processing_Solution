import os
import json
from pathlib import Path
import pdfplumber
import re

def extract_title(page):
    """
    Extract full largest font-size line, most centered on first page as title.
    """
    words = page.extract_words(extra_attrs=["size", "x0", "x1", "top"])
    if not words:
        return ""

    # Group words by line using top coordinate (rounded)
    lines = {}
    for w in words:
        y = round(w['top'], 1)
        lines.setdefault(y, []).append(w)

    # Determine max font size in page
    max_size = max(float(w["size"]) for w in words)

    candidate_lines = []
    page_width = page.width

    for y, line_words in lines.items():
        # Check if line font sizes are all near max_size (within 0.1)
        sizes = [float(w["size"]) for w in line_words]
        if all(abs(s - max_size) <= 0.1 for s in sizes):
            # Get line text
            line_text = " ".join(w["text"] for w in line_words).strip()
            # Compute horizontal center of line
            avg_center = sum((w["x0"] + w["x1"]) / 2 for w in line_words) / len(line_words)
            dist_center = abs(avg_center - page_width / 2)
            candidate_lines.append((dist_center, line_text))

    if not candidate_lines:
        return ""

    # Pick line closest to horizontal center
    candidate_lines.sort(key=lambda x: x[0])
    # Return the full text of the most centered largest font line as title
    return candidate_lines[0][1]

def assign_heading_level(text, size, size_to_level):
    """
    Assign heading level using font size and numeric prefix patterns:
    - If font size maps to H1: check if text starts with pattern "1.", "2.", etc. for H1,
      "1.1", "2.1", etc. for H2, else fallback on size_to_level.
    """
    # Check numbering prefixes:
    # H1: starts with "1.", "2.", "3." etc. (level 1)
    # H2: starts with "1.1", "2.2", "3.3" etc. (level 2)
    # H3: starts with "1.1.1", etc. (level 3)
    num_prefix = re.match(r"^(\d+(\.\d+){0,2})\s", text)
    if num_prefix:
        parts = num_prefix.group(1).split(".")
        num_level = len(parts)  # number of parts determine heading depth
        if num_level == 1:
            return "H1"
        elif num_level == 2:
            return "H2"
        elif num_level == 3:
            return "H3"
    # Otherwise, fallback on font size
    return size_to_level.get(round(size, 1), None)

def extract_headings(pdf):
    font_sizes = set()
    page_word_data = []

    for page_num, page in enumerate(pdf.pages, 1):
        words = page.extract_words(extra_attrs=["size", "top"])
        page_word_data.append((page_num, words))
        font_sizes.update(round(float(w['size']), 1) for w in words)

    sorted_sizes = sorted(list(font_sizes), reverse=True)

    # Map font sizes to levels
    size_to_level = {}
    if len(sorted_sizes) > 0:
        size_to_level[sorted_sizes[0]] = "TITLE"
    if len(sorted_sizes) > 1:
        size_to_level[sorted_sizes[1]] = "H1"
    if len(sorted_sizes) > 2:
        size_to_level[sorted_sizes[2]] = "H2"
    if len(sorted_sizes) > 3:
        size_to_level[sorted_sizes[3]] = "H3"

    headings = []

    for page_num, words in page_word_data:
        # Group words into lines by y coordinate (rounded)
        lines = {}
        for w in words:
            y = round(w['top'], 1)
            lines.setdefault(y, []).append(w)

        # Process lines in reading order: top to bottom
        for y in sorted(lines):
            line_words = lines[y]
            if not line_words:
                continue
            # Estimate line font size as the mode or first word size
            sizes = [float(w['size']) for w in line_words]
            font_size = max(set(sizes), key = sizes.count)  # Most common size in line

            # Compose full line text including spaces as-is (with trailing spaces kept)
            # We do not strip trailing spaces in this implementation to match example
            line_text = " ".join(w['text'] for w in line_words)

            # Skip lines that are too short or have no text
            if len(line_text.strip()) < 2:
                continue

            # Assign heading level by font size and numbering pattern
            level = assign_heading_level(line_text.strip(), font_size, size_to_level)

            # Only add if recognized and not TITLE
            if level and level != "TITLE":
                headings.append({
                    "level": level,
                    "text": line_text,
                    "page": page_num
                })

    # Sort headings by page number and then by vertical position ascending (already sorted by y)
    # This ensures proper reading order
    headings.sort(key=lambda x: (x["page"]))

    return headings

def process_pdf(input_path, output_path):
    with pdfplumber.open(input_path) as pdf:
        title = extract_title(pdf.pages[0]) if pdf.pages else ""
        outline = extract_headings(pdf)
        result = {
            "title": title,
            "outline": outline
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

def main():
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return
    for pdf_file in pdf_files:
        output_file = output_dir / f"{pdf_file.stem}.json"
        print(f"Processing {pdf_file.name} ...")
        try:
            process_pdf(pdf_file, output_file)
            print(f"Output written to {output_file}")
        except Exception as e:
            print(f"Failed to process {pdf_file.name}: {e}")

if __name__ == "__main__":
    main()
