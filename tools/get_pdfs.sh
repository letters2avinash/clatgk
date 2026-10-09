#!/bin/bash
# Downloads every PDF from the repo into ~/Desktop/AARYA/CLAT_GK_PDFs (safe to re-run; updates files).
set -e
DEST="$HOME/Desktop/AARYA/CLAT_GK_PDFs"
TMP="$(mktemp -d)"
curl -L -sS -o "$TMP/repo.zip" "https://github.com/letters2avinash/clatgk/archive/refs/heads/claude/clat-current-affairs-cloud-q2gkmz.zip"
unzip -q "$TMP/repo.zip" -d "$TMP"
SRC="$(ls -d "$TMP"/clatgk-*)"
mkdir -p "$DEST/Practice_Tests_1-10" "$DEST/Monthly_Dashboard_PDFs"
cp "$SRC"/out/*.pdf "$DEST/Practice_Tests_1-10/" 2>/dev/null || true
if [ -d "$SRC/pdfs" ]; then cp -R "$SRC"/pdfs/* "$DEST/Monthly_Dashboard_PDFs/"; fi
rm -rf "$TMP"
echo "Saved to: $DEST"
find "$DEST" -name '*.pdf' | wc -l | xargs echo "PDF files:"
open "$DEST" 2>/dev/null || true
