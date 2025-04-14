#!/bin/bash
set -e

python -m venv venv
source venv/bin/activate

pip install build
rm -rf dist/
python -m build

ls -lah dist/
echo "Done!"
