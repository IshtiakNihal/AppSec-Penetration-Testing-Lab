#!/bin/bash
export DATABASE_URL=sqlite:///vulnerable.db
cd "$(dirname "$0")"
python -m app.main
