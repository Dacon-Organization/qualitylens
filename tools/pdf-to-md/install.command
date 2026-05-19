#!/bin/sh
set -eu

cd "$(dirname "$0")"

SETUP_ARGS=""
if [ "${1:-}" = "--auto" ]; then
  SETUP_ARGS="--non-interactive --cli auto"
fi

echo "pdf-to-md student installer"
echo "This bootstraps uv, Python, Java where possible, and connects detected AI tools automatically."
echo

add_path_line() {
  file="$1"
  line="$2"
  mkdir -p "$(dirname "$file")"
  touch "$file"
  if ! grep -F "$line" "$file" >/dev/null 2>&1; then
    printf "\n# pdf-to-md installer\n%s\n" "$line" >> "$file"
  fi
}

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
  if ! command -v curl >/dev/null 2>&1; then
    echo "curl was not found. Ask an AI assistant with @INSTALL.md, or install curl and run this again."
    printf "Press Enter to close..."
    read _answer || true
    exit 1
  fi
  echo "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
  add_path_line "$HOME/.zshrc" 'export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"'
  add_path_line "$HOME/.bashrc" 'export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"'
  UV="$(find_uv || true)"
fi

if [ -z "$UV" ]; then
  echo "uv installation failed. Check your internet connection and try again."
  printf "Press Enter to close..."
  read _answer
  exit 1
fi

"$UV" run --python 3.12 python setup.py $SETUP_ARGS

echo
echo "Install finished."
echo "Workspace: $HOME/Documents/pdf-to-md"
echo "To convert a file, double-click convert.command."
echo "Results are saved under the input file folder: markdown/"
echo
if [ "${1:-}" != "--auto" ]; then
  printf "Press Enter to close..."
  read _answer || true
fi
