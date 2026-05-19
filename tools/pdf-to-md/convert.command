#!/bin/sh
set -eu

cd "$(dirname "$0")"

WORKSPACE="$HOME/Documents/pdf-to-md"
mkdir -p "$WORKSPACE/courses/sample-course/ch01/source"

find_uv() {
  if command -v uv >/dev/null 2>&1; then
    command -v uv
    return 0
  fi
  for candidate in "$HOME/.local/bin/uv" "$HOME/.cargo/bin/uv"; do
    if [ -x "$candidate" ]; then
      printf "%s\n" "$candidate"
      return 0
    fi
  done
  return 1
}

UV="$(find_uv || true)"
if [ -z "$UV" ]; then
  echo "uv was not found. Run install.command first."
  printf "Press Enter to close..."
  read _answer
  exit 1
fi

echo "pdf-to-md converter"
echo "Paste a PDF or PPTX path, then press Enter."
echo "Tip: on macOS, drag the file into this window to paste its path."
echo "Recommended: put originals under $WORKSPACE/courses/<course>/<chapter>/source"
echo "Output: markdown/ and .reports/ are created under the input file folder."
echo
printf "File path: "
read INPUT_PATH
INPUT_PATH="$(printf "%s" "$INPUT_PATH" | sed "s/^['\\\"]//;s/['\\\"]$//;s/\\\\ / /g")"

if [ -z "$INPUT_PATH" ]; then
  echo "No file path entered."
  printf "Press Enter to close..."
  read _answer
  exit 1
fi

"$UV" run --python 3.12 python convert.py "$INPUT_PATH"

echo
echo "Done. Check the markdown/ folder next to the input file."
printf "Press Enter to close..."
read _answer
