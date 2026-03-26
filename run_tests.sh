#!/bin/bash
cd "$(dirname "$0")"
if ! curl -s http://localhost:5000 > /dev/null 2>&1; then
    echo "Error: App is not running on localhost:5000"
    echo "Please run ./run_app.sh first"
    exit 1
fi
python -m framework.main --target http://localhost:5000 --run-all
