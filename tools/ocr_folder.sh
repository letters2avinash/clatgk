#!/usr/bin/env bash
# OCR every PDF and image in a folder (macOS or Linux). Writes one .txt per file, mirroring the folder structure.
# usage: ocr_folder.sh ["/path/to/input"] ["/path/to/output"]
#   defaults: input = ~/Downloads/MOCK TESTS ; output = ~/Desktop/AARYA/MOCK_TESTS_OCR
# one-time install (macOS):  brew install ocrmypdf tesseract poppler
set -uo pipefail

IN="${1:-$HOME/Downloads/MOCK TESTS}"
OUT="${2:-$HOME/Desktop/AARYA/MOCK_TESTS_OCR}"
LANGS="${OCR_LANGS:-eng}"          # e.g. OCR_LANGS=eng+hin for Hindi pages
MIN_CHARS=200                      # a PDF with at least this much real text already has a text layer: no OCR needed

for t in ocrmypdf tesseract pdftotext; do
  command -v "$t" >/dev/null || { echo "Missing '$t'. Install with: brew install ocrmypdf tesseract poppler"; exit 1; }
done
[ -d "$IN" ] || { echo "Input folder not found: $IN"; exit 1; }
mkdir -p "$OUT"
LOG="$OUT/_ocr_log.txt"; : > "$LOG"
n=0; ok=0; skipped=0; failed=0

# -print0 / read -d '' keeps spaces and odd characters in file names safe
while IFS= read -r -d '' f; do
  n=$((n+1))
  rel="${f#"$IN"/}"; base="${rel%.*}"; ext="$(printf '%s' "${f##*.}" | tr '[:upper:]' '[:lower:]')"
  dest="$OUT/$base.txt"; mkdir -p "$(dirname "$dest")"
  if [ -s "$dest" ]; then echo "skip (done)  $rel"; skipped=$((skipped+1)); continue; fi
  echo "[$n] $rel"
  case "$ext" in
    pdf)
      # 1) free route: use the PDF's own text layer if it has one
      pdftotext -layout "$f" "$dest" 2>>"$LOG"
      if [ "$(tr -d '[:space:]' < "$dest" | wc -c)" -ge "$MIN_CHARS" ]; then ok=$((ok+1)); continue; fi
      # 2) scanned PDF: OCR it and keep only the sidecar text. First try keeping pages that already have text;
      #    if that fails (e.g. junk text layer), force OCR on every page.
      tmp="$(mktemp -t ocr).pdf"
      if ocrmypdf --skip-text --deskew --rotate-pages -l "$LANGS" --sidecar "$dest" "$f" "$tmp" >>"$LOG" 2>&1 || \
         ocrmypdf --force-ocr --deskew --rotate-pages -l "$LANGS" --sidecar "$dest" "$f" "$tmp" >>"$LOG" 2>&1; then ok=$((ok+1))
      else echo "   FAILED: $rel"; echo "FAILED $rel" >>"$LOG"; rm -f "$dest"; failed=$((failed+1)); fi
      rm -f "$tmp" ;;
    png|jpg|jpeg|tif|tiff|bmp|webp|heic)
      src="$f"
      if [ "$ext" = heic ] || [ "$ext" = webp ]; then            # tesseract can't read these directly (macOS sips converts)
        src="$(mktemp -t ocr).png"; sips -s format png "$f" --out "$src" >/dev/null 2>&1 || { echo "   FAILED: $rel"; failed=$((failed+1)); continue; }
      fi
      if tesseract "$src" "${dest%.txt}" -l "$LANGS" --psm 3 >>"$LOG" 2>&1; then ok=$((ok+1)); else echo "   FAILED: $rel"; echo "FAILED $rel" >>"$LOG"; failed=$((failed+1)); fi
      [ "$src" != "$f" ] && rm -f "$src" ;;
    *) : ;;   # ignore everything else
  esac
done < <(find "$IN" -type f \( -iname '*.pdf' -o -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.tif' -o -iname '*.tiff' -o -iname '*.bmp' -o -iname '*.webp' -o -iname '*.heic' \) -not -name '.*' -print0 | sort -z)

echo; echo "Done. files: $n  ok: $ok  already done: $skipped  failed: $failed"
echo "Text files: $OUT   (details in $LOG)"
