import json
import os
import sys

# --- Dependency Imports ---
try:
    import fitz  # PyMuPDF for PDF
    import docx  # python-docx for DOCX
    import markdown  # markdown for MD to HTML
    from bs4 import BeautifulSoup  # for parsing HTML from markdown
    import pandas as pd  # for CSV and Excel support
except ImportError as e:
    print(f"Missing dependency: {e.name}. Install with:")
    print("pip install pymupdf python-docx markdown beautifulsoup4 pandas openpyxl")
    sys.exit(1)


# --- PDF Conversion ---
def pdf_to_json(file_path):
    data = {"type": "pdf", "pages": []}
    try:
        with fitz.open(file_path) as pdf:
            for page_num, page in enumerate(pdf, start=1):
                text = page.get_text("text")
                data["pages"].append({
                    "page": page_num,
                    "content": text.strip()
                })
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return data


# --- DOCX Conversion ---
def docx_to_json(file_path):
    data = {"type": "docx", "paragraphs": []}
    try:
        document = docx.Document(file_path)
        for para in document.paragraphs:
            if para.text.strip():
                data["paragraphs"].append(para.text.strip())
    except Exception as e:
        print(f"Error reading DOCX: {e}")
    return data


# --- Markdown Conversion ---
def markdown_to_json(file_path):
    data = {"type": "markdown", "content": []}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            md_text = f.read()

        html = markdown.markdown(md_text)
        soup = BeautifulSoup(html, "html.parser")

        for element in soup.find_all(["h1", "h2", "h3", "p", "li"]):
            data["content"].append({
                "tag": element.name,
                "text": element.get_text(strip=True)
            })
    except Exception as e:
        print(f"Error reading Markdown: {e}")
    return data


# --- CSV & Excel Conversion (with Chunking) ---
def tabular_to_json_chunks(file_path, chunk_size=100):
    """
    Reads CSV or Excel and returns a list of (data_chunk, filename_suffix) tuples.
    Each chunk contains up to chunk_size rows.
    """
    all_chunks = []
    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext == ".csv":
            sheets = {"data": pd.read_csv(file_path)}
        else:
            xls = pd.ExcelFile(file_path)
            sheets = {name: pd.read_excel(xls, sheet_name=name) for name in xls.sheet_names}

        for sheet_name, df in sheets.items():
            rows = df.to_dict(orient="records")

            for i in range(0, len(rows), chunk_size):
                chunk_rows = rows[i: i + chunk_size]
                part_num = (i // chunk_size) + 1

                chunk_data = {
                    "type": "tabular",
                    "source_format": ext.replace(".", ""),
                    "part": part_num,
                    "columns": list(df.columns),
                    "rows": chunk_rows
                }

                suffix = (
                    f"_part{part_num}"
                    if ext == ".csv"
                    else f"_{sheet_name}_part{part_num}"
                )
                all_chunks.append((chunk_data, suffix))

    except Exception as e:
        print(f"Error reading {ext.upper()}: {e}")

    return all_chunks


# --- Dispatcher ---
def convert_to_json(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return pdf_to_json(file_path)
    elif ext in (".doc", ".docx"):
        return docx_to_json(file_path)
    elif ext in (".md", ".markdown"):
        return markdown_to_json(file_path)
    elif ext in (".csv", ".xls", ".xlsx"):
        return tabular_to_json_chunks(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


# --- Main Execution ---
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python convert_to_json.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.isfile(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)

    try:
        result = convert_to_json(file_path)

        if isinstance(result, list):
            # Chunked output (CSV or Excel)
            base_name = os.path.splitext(file_path)[0]
            for data, suffix in result:
                output_file = f"{base_name}{suffix}.json"
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"✅ Chunk saved: {output_file}")
        else:
            # Single output (PDF, DOCX, Markdown)
            output_file = os.path.splitext(file_path)[0] + ".json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"✅ Conversion successful! JSON saved to: {output_file}")

    except Exception as e:
        print(f"❌ Conversion failed: {e}")
