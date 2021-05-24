#!/bin/sh -e
set -x

# Format
autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place erp.py api.py
black erp.py api.py
isort erp.py api.py
