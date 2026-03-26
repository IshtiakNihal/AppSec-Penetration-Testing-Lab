#!/bin/bash
export DATABASE_URL=sqlite:///patched.db
cd "$(dirname "$0")"
python -m app_patched.main
