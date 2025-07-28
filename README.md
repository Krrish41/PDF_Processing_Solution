# PDF Processing Solution

## 📘 Overview

This tool extracts a structured outline (Title, H1, H2, H3) from text-based PDFs using layout and font-based heuristics. It works fully offline, fits within Docker image constraints, and outputs a clean hierarchical JSON for each input document.

---

## 🧠 Approach

- Uses **pdfplumber** to extract text, layout (font size, position), and structure from each PDF page.
- Determines the **document title** by selecting the largest and most centered text on the first page.
- Remaining text is grouped by **font size** and numerically prefixed patterns (like `1.`, `1.2`, etc.) to infer heading levels.
- Heading levels are mapped to:
  - `H1`: Largest heading size after title
  - `H2`: Next size down
  - `H3`: Next size down (optional)
- Outputs a structured JSON outline with heading `level`, `text`, and `page` number.

---

## 🧰 Tech Stack

- **Python 3.9**
- **pdfplumber**: For PDF parsing and text extraction
- **Standard Python libraries**: `json`, `re`, `pathlib`

📌 No ML models or training involved — heuristic, layout-aware approach ensures light weight and fast processing.

---

## 📁 Project Structure

```
.
├── input/                  # Place your PDF files here
├── output/                 # JSON outputs appear here
├── main.py                 # Main logic for extraction
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker build file
├── Commands to run.txt     # Sample terminal commands
└── README.md               # You're reading it!
```

---

## 🐳 How to Build and Run (Docker)

> ✅ Recommended for reproducible and dependency-free execution.

1. **Place your PDF(s) in the `input/` folder.**

2. **Build the Docker image:**
```bash
docker build --platform linux/amd64 -t mysolution:latest .
```

3. **Run the container:**
```bash
docker run --rm \
-v /absolute/path/to/input:/app/input \
-v /absolute/path/to/output:/app/output \
--network none mysolution:latest
```

🔁 Replace `/absolute/path/to/input` and `/absolute/path/to/output` with absolute paths on your system.

---

## 🐍 Local Python Run (for Development)

1. **Install requirements:**
```bash
pip install -r requirements.txt
```

2. **Place your PDF(s) in `input/` folder.**

3. **Run the script:**
```bash
python main.py
```

Outputs will be saved as `.json` in the `output/` directory.

---

## 📤 Output Format

Each output JSON will follow this structure:

```json
{
  "title": "Document Title",
  "outline": [
    {"level": "H1", "text": "Introduction", "page": 1},
    {"level": "H2", "text": "1.1 Background", "page": 2},
    {"level": "H3", "text": "1.1.1 Problem Statement", "page": 2}
  ]
}
```

---

## ⚠️ Troubleshooting

- ❌ Scanned/image-only PDFs are not supported (OCR not implemented).
- ✅ Works best with digital/text-based PDFs.
- 📂 Ensure Docker volumes are mounted correctly and paths are absolute.

---

## 📜 License

This project is provided as-is for educational and prototyping purposes. Feel free to modify and extend.
