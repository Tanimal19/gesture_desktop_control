#!/bin/bash

TARGET_DIR="${1:-.}"

echo "find __pycache__ directories:"
find "$TARGET_DIR" -type d -name "__pycache__" ! -path "*/.venv/*" -print

echo ""
read -p "delete? (y/N)" confirm

if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
    find "$TARGET_DIR" -type d -name "__pycache__" -exec rm -rf {} +
    echo "deleted"
else
    echo "skipped"
fi