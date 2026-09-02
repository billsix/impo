#!/bin/bash
# Interactive shell in the project directory.
set -e
cd /book || exit 1
exec bash "$@"
