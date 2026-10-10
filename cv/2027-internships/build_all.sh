#!/usr/bin/env bash
# Compile independent role-specific CVs without modifying the primary website CV.
set -euo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if ! command -v pdflatex >/dev/null 2>&1; then
  printf 'Error: pdflatex is required. Install a TeX distribution first.\n' >&2
  exit 127
fi
shopt -s nullglob
sources=("$HERE"/*.tex)
if [ "${#sources[@]}" -eq 0 ]; then
  printf 'Error: no TeX sources found in %s\n' "$HERE" >&2
  exit 1
fi
OUT="$HERE/build"
mkdir -p -- "$OUT"
for source in "${sources[@]}"; do
  name="$(basename -- "$source")"
  printf '\nCompiling %s\n' "$name"
  for pass in 1 2; do
    if ! pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error \
        -file-line-error -output-directory="$OUT" "$source" \
        >"$OUT/${name%.tex}.pass${pass}.txt" 2>&1; then
      cat -- "$OUT/${name%.tex}.pass${pass}.txt" >&2
      exit 1
    fi
  done
  printf 'Created %s/%s.pdf\n' "$OUT" "${name%.tex}"
done
printf '\nCompiled %s CVs. Output: %s\n' "${#sources[@]}" "$OUT"
