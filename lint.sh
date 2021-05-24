#!/usr/bin/env bash

set -ex

mypy erp.py api.py
black erp.py api.py --check
isort --check-only erp.py api.py
flake8 erp.py api.py
