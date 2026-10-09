#!/usr/bin/env python3
"""Turn scanned (image-only) PDFs into text files, free and offline.

Setup (Mac):   brew install tesseract
               pip3 install pymupdf pytesseract
Setup (Win):   install Tesseract from https://github.com/UB-Mannheim/tesseract/wiki
               pip install pymupdf pytesseract
Run:           python3 ocr_booklets.py  /path/to/folder/with/pdfs  [/path/to/output]

For every X.pdf it writes X.txt with "=== PAGE n ===" markers. Safe to stop and
re-run: finished PDFs are skipped, and a partly done PDF resumes at its last page.
"""
import sys, pathlib, io
import fitz                      # PyMuPDF
import pytesseract
from PIL import Image

DPI = 200                        # 200 is a good speed/accuracy balance; use 300 if text is small

def ocr_pdf(pdf, out_txt):
    doc = fitz.open(pdf)
    part = out_txt.with_suffix(".part")
    done = 0
    if part.exists():
        done = part.read_text(encoding="utf8").count("=== PAGE ")
    with open(part, "a", encoding="utf8") as f:
        for n in range(done, len(doc)):
            pix = doc[n].get_pixmap(dpi=DPI)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            text = pytesseract.image_to_string(img, lang="eng", config="--psm 3")
            f.write(f"=== PAGE {n+1} ===\n{text.strip()}\n\n")
            f.flush()
            print(f"  {pdf.name}: page {n+1}/{len(doc)}", end="\r")
    part.rename(out_txt)
    print(f"\n  wrote {out_txt}")

def main():
    src = pathlib.Path(sys.argv[1]).expanduser()
    dst = pathlib.Path(sys.argv[2]).expanduser() if len(sys.argv) > 2 else src / "text"
    dst.mkdir(parents=True, exist_ok=True)
    pdfs = sorted(src.glob("*.pdf"))
    if not pdfs:
        sys.exit(f"No PDFs found in {src}")
    for pdf in pdfs:
        out = dst / (pdf.stem + ".txt")
        if out.exists():
            print(f"skip {pdf.name} (done)"); continue
        print(f"OCR {pdf.name}")
        ocr_pdf(pdf, out)

if __name__ == "__main__":
    main()
