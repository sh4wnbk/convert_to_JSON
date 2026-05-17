# convert_to_json

A lightweight Python utility that converts common file formats into structured JSON.
Supports PDF, DOCX, Markdown, CSV, and Excel — with automatic chunking for large tabular files.

---

## Supported Formats

| Format | Output Type | Chunked |
|--------|-------------|---------|
| `.pdf` | Pages array | No |
| `.docx` / `.doc` | Paragraphs array | No |
| `.md` / `.markdown` | Tagged content array | No |
| `.csv` | Tabular rows | Yes (100 rows/chunk) |
| `.xls` / `.xlsx` | Tabular rows per sheet | Yes (100 rows/chunk) |

---

## Requirements

Python 3.8+

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

```bash
python convert_to_json.py <file_path>
```

### Examples

```bash
# Convert a PDF
python convert_to_json.py report.pdf
# Output: report.json

# Convert a Word document
python convert_to_json.py notes.docx
# Output: notes.json

# Convert a Markdown file
python convert_to_json.py readme.md
# Output: readme.json

# Convert a CSV (chunked)
python convert_to_json.py data.csv
# Output: data_part1.json, data_part2.json, ...

# Convert an Excel file (chunked per sheet)
python convert_to_json.py spreadsheet.xlsx
# Output: spreadsheet_Sheet1_part1.json, spreadsheet_Sheet1_part2.json, ...
```

---

## Output Structure

### PDF
```json
{
  "type": "pdf",
  "pages": [
    { "page": 1, "content": "Page text here..." },
    { "page": 2, "content": "Page text here..." }
  ]
}
```

### DOCX
```json
{
  "type": "docx",
  "paragraphs": [
    "First paragraph text.",
    "Second paragraph text."
  ]
}
```

### Markdown
```json
{
  "type": "markdown",
  "content": [
    { "tag": "h1", "text": "Title" },
    { "tag": "p", "text": "Paragraph text." },
    { "tag": "li", "text": "List item." }
  ]
}
```

### CSV / Excel (chunked)
```json
{
  "type": "tabular",
  "source_format": "csv",
  "part": 1,
  "columns": ["col1", "col2", "col3"],
  "rows": [
    { "col1": "value", "col2": "value", "col3": "value" }
  ]
}
```

---

## Notes

- Chunking splits large CSV/Excel files into groups of **100 rows** per output file to keep JSON files manageable.
- Excel files with multiple sheets produce separate chunk files per sheet.
- Output JSON files are saved in the **same directory** as the input file.

---

## Project Structure

```
file_to_json/
├── convert_to_json.py   # Main converter script
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

---

## License

MIT
